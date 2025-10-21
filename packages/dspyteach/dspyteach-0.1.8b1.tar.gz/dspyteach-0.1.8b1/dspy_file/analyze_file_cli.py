# path: analyze_file_cli.py
# analyze_file_cli.py - command line entry point for DSPy file analyzer with MLflow tracking + tracing
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from enum import Enum
from urllib import error as urlerror
from urllib import request
from pathlib import Path
from typing import Any, Final

import dspy
from dotenv import load_dotenv

from .file_analyzer import FileTeachingAnalyzer
from .file_helpers import collect_source_paths, read_file_content, render_prediction
from .prompts import PromptTemplate, list_bundled_prompts, load_prompt_text
from .refactor_analyzer import FileRefactorAnalyzer

try:  # dspy depends on litellm; guard in case import path changes.
    from litellm.exceptions import InternalServerError as LiteLLMInternalServerError
except Exception:  # pragma: no cover - defensive fallback if litellm API shifts
    LiteLLMInternalServerError = None  # type: ignore[assignment]

# Optional MLflow import. Enabled only with --mlflow to ensure no behavior change by default.
try:  # pragma: no cover - optional dependency
    import mlflow  # type: ignore
except Exception:  # pragma: no cover - keep CLI usable without MLflow installed
    mlflow = None  # type: ignore

class Provider(str, Enum):
    """Supported language model providers."""

    OLLAMA = "ollama"
    OPENAI = "openai"
    LMSTUDIO = "lmstudio"

    @property
    def is_openai_compatible(self) -> bool:
        return self in {Provider.OPENAI, Provider.LMSTUDIO}


DEFAULT_PROVIDER: Final[Provider] = Provider.OLLAMA
DEFAULT_OUTPUT_DIR = Path(__file__).parent / "data"
DEFAULT_OLLAMA_MODEL = "hf.co/Mungert/osmosis-mcp-4b-GGUF:Q5_K_M"
DEFAULT_LMSTUDIO_MODEL = "osmosis-mcp-4b@q8_0"
DEFAULT_OPENAI_MODEL = "gpt-5"
OLLAMA_BASE_URL = "http://localhost:11434"
LMSTUDIO_BASE_URL = "http://localhost:1234/v1"

PROVIDER_DEFAULTS: Final[dict[Provider, dict[str, Any]]] = {
    Provider.OLLAMA: {"model": DEFAULT_OLLAMA_MODEL, "api_base": OLLAMA_BASE_URL},
    Provider.LMSTUDIO: {"model": DEFAULT_LMSTUDIO_MODEL, "api_base": LMSTUDIO_BASE_URL},
    Provider.OPENAI: {"model": DEFAULT_OPENAI_MODEL, "api_base": None},
}


def _resolve_option(
    cli_value: str | None, env_var: str, default: str | None = None
) -> str | None:
    """Return the CLI value if provided, otherwise fall back to env or default."""

    if cli_value is not None:
        return cli_value
    env_value = os.getenv(env_var)
    if env_value not in ("", None):
        return env_value
    return default


def _normalize_model_name(provider: Provider, raw_model: str) -> str:
    """Attach the appropriate provider prefix to the model identifier."""

    if provider is Provider.OLLAMA:
        return (
            raw_model
            if raw_model.startswith("ollama_chat/")
            else f"ollama_chat/{raw_model}"
        )

    if raw_model.startswith("openai/"):
        return raw_model
    return f"openai/{raw_model}"


def configure_model(
    provider: Provider,
    model_name: str,
    *,
    api_base: str | None,
    api_key: str | None,
) -> None:
    """Configure DSPy with the selected provider and model."""

    lm_kwargs: dict[str, Any] = {"streaming": False, "cache": False}
    if provider is Provider.OLLAMA:
        lm_kwargs["api_base"] = api_base or OLLAMA_BASE_URL
        # Ollama's OpenAI compatibility ignores api_key, so pass an empty string.
        lm_kwargs["api_key"] = ""
    else:
        if api_base:
            lm_kwargs["api_base"] = api_base
        if api_key:
            lm_kwargs["api_key"] = api_key

    identifier = _normalize_model_name(provider, model_name)
    lm = dspy.LM(identifier, **lm_kwargs)
    dspy.configure(lm=lm)
    provider_label = "LM Studio" if provider is Provider.LMSTUDIO else provider.value
    suffix = f" via {api_base}" if provider.is_openai_compatible and api_base else ""
    print(f"Configured DSPy LM ({provider_label}): {model_name}{suffix}")


class ProviderConnectivityError(RuntimeError):
    """Raised when a provider cannot be reached before running analysis."""


def _probe_openai_provider(
    api_base: str, api_key: str | None, *, timeout: float = 3.0
) -> None:
    """Make a lightweight request against an OpenAI-compatible endpoint."""

    endpoint = api_base.rstrip("/") + "/models"
    headers = {"Authorization": f"Bearer {api_key or ''}"}
    request_obj = request.Request(endpoint, headers=headers, method="GET")

    try:
        with request.urlopen(request_obj, timeout=timeout):
            return
    except urlerror.HTTPError as exc:
        raise ProviderConnectivityError(
            f"Endpoint {endpoint} responded with HTTP {exc.code}: {exc.reason}"
        ) from exc
    except urlerror.URLError as exc:
        reason = getattr(exc, "reason", exc)
        raise ProviderConnectivityError(
            f"Failed to reach {endpoint}: {reason}"
        ) from exc


def stop_ollama_model(model_name: str) -> None:
    """Stop the Ollama model to free server resources."""

    try:
        subprocess.run(
            ["ollama", "stop", model_name],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:  # pragma: no cover - warn only
        print(f"Warning: Failed to stop model {model_name}: {exc}")
    except FileNotFoundError:
        print("Warning: ollama command not found while attempting to stop the model.")


class AnalysisMode(str, Enum):
    TEACH = "teach"
    REFACTOR = "refactor"

    @property
    def render_key(self) -> str:
        return self.value

    @property
    def output_description(self) -> str:
        return "teaching report" if self is AnalysisMode.TEACH else "refactor template"

    @property
    def file_suffix(self) -> str:
        # No suffixing. Preserve original filename.
        return ""


def _prompt_for_template_selection(prompts: list[PromptTemplate]) -> PromptTemplate:
    while True:
        print("Available prompt templates:")
        for idx, template in enumerate(prompts, 1):
            print(f"  [{idx}] {template.name} ({template.path.name})")
        try:
            choice = input(f"Select a template [1-{len(prompts)}] (default 1): ")
        except EOFError:
            print("No selection provided; using first template.")
            return prompts[0]

        stripped = choice.strip()
        if not stripped:
            return prompts[0]
        if stripped.isdigit():
            idx = int(stripped)
            if 1 <= idx <= len(prompts):
                return prompts[idx - 1]
        print(f"Please enter a number between 1 and {len(prompts)}.")


def _resolve_prompt_text(prompt_arg: str | None) -> str:
    if prompt_arg:
        return load_prompt_text(prompt_arg)

    prompts = list_bundled_prompts()
    if not prompts:
        raise FileNotFoundError("No prompt templates found in prompts directory.")
    if len(prompts) == 1:
        return prompts[0].path.read_text(encoding="utf-8")

    selected = _prompt_for_template_selection(prompts)
    return selected.path.read_text(encoding="utf-8")


def _write_output(
    source_path: Path,
    content: str,
    *,
    root: Path | None = None,
    output_dir: Path | None = None,
    suffix: str = "",
) -> Path:
    """Write output to the same filename and directory layout as the analyzed path."""

    try:
        relative_path = (
            source_path.relative_to(root) if root else Path(source_path.name)
        )
    except ValueError:
        relative_path = Path(source_path.name)

    if output_dir:
        dest_path = (output_dir / relative_path).resolve()
        dest_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        dest_path = source_path

    if not content.endswith("\n"):
        content = content + "\n"

    dest_path.write_text(content, encoding="utf-8")
    return dest_path


def _confirm_analyze(path: Path) -> bool:
    prompt = f"Analyze {path}? [Y/n]: "
    while True:
        try:
            response = input(prompt)
        except EOFError:
            print("No input received; skipping.")
            return False

        normalized = response.strip().lower()
        if normalized in {"", "y", "yes"}:
            return True
        if normalized in {"n", "no"}:
            return False
        print("Please answer 'y' or 'n'.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze a single file using DSPy signatures and modules",
    )
    parser.add_argument("path", help="Path to the file to analyze")
    parser.add_argument(
        "--provider",
        choices=[provider.value for provider in Provider],
        default=None,
        help=(
            "Language model provider to use (env: DSPYTEACH_PROVIDER). "
            "Choose from 'ollama', 'lmstudio', or 'openai'."
        ),
    )
    parser.add_argument(
        "--model",
        dest="model_name",
        default=None,
        help=(
            "Override the model identifier for the selected provider "
            "(env: DSPYTEACH_MODEL)."
        ),
    )
    parser.add_argument(
        "--api-base",
        dest="api_base",
        default=None,
        help=("Override the OpenAI-compatible API base URL (env: DSPYTEACH_API_BASE)."),
    )
    parser.add_argument(
        "--api-key",
        dest="api_key",
        default=None,
        help=(
            "API key for OpenAI-compatible providers (env: DSPYTEACH_API_KEY). "
            "Falls back to OPENAI_API_KEY for the OpenAI provider."
        ),
    )
    parser.add_argument(
        "--keep-provider-alive",
        action="store_true",
        dest="keep_provider_alive",
        help="Skip stopping the local Ollama model when execution completes.",
    )
    parser.add_argument(
        "-r",
        "--raw",
        action="store_true",
        help="Print raw DSPy prediction repr instead of formatted text",
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=[mode.value for mode in AnalysisMode],
        default=AnalysisMode.TEACH.value,
        help="Select output mode: teaching report (default) or refactor prompt template.",
    )
    parser.add_argument(
        "-nr",
        "--non-recursive",
        action="store_true",
        help="When path is a directory, only analyze files in the top-level directory",
    )
    parser.add_argument(
        "-g",
        "--glob",
        action="append",
        dest="include_globs",
        default=None,
        help=(
            "Optional glob pattern(s) applied relative to the directory. Repeat to combine."
        ),
    )
    parser.add_argument(
        "-p",
        "--prompt",
        dest="prompt",
        default=None,
        help=(
            "Prompt template to use in refactor mode. Provide a name, bundled filename, or path."
        ),
    )
    parser.add_argument(
        "-i",
        "--confirm-each",
        "--interactive",
        action="store_true",
        dest="confirm_each",
        help="Prompt for confirmation before analyzing each file.",
    )
    parser.add_argument(
        "-ed",
        "--exclude-dirs",
        action="append",
        dest="exclude_dirs",
        default=None,
        help=(
            "Comma-separated relative directory paths to skip entirely when scanning."
        ),
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        default=None,
        help=("Directory to write outputs. If omitted, overwrite files in place."),
    )
    # --- MLflow options ---
    parser.add_argument(
        "--mlflow",
        action="store_true",
        help="Enable MLflow tracking of params, metrics, artifacts, and traces.",
    )
    parser.add_argument(
        "--mlflow-experiment",
        dest="mlflow_experiment",
        default=None,
        help="Name of the MLflow experiment to use or create when --mlflow is set.",
    )
    return parser


def analyze_path(
    path: str,
    *,
    raw: bool,
    recursive: bool,
    include_globs: list[str] | None,
    confirm_each: bool,
    exclude_dirs: list[str] | None,
    output_dir: Path | None,
    mode: AnalysisMode,
    prompt_text: str | None = None,
    mlflow_enabled: bool = False,
    root_hint: Path | None = None,
) -> int:
    """Run the DSPy pipeline and render results to stdout for one or many files."""

    resolved = Path(path).expanduser().resolve()
    targets = collect_source_paths(
        path,
        recursive=recursive,
        include_globs=include_globs,
        exclude_dirs=exclude_dirs,
    )

    if not targets:
        print(f"No files found under {resolved}")
        return 0

    analyzer: dspy.Module
    if mode is AnalysisMode.TEACH:
        analyzer = FileTeachingAnalyzer()
    else:
        analyzer = FileRefactorAnalyzer(template_text=prompt_text)

    root: Path | None = (
        root_hint if root_hint else (resolved if resolved.is_dir() else None)
    )

    exit_code = 0
    for target in targets:
        if confirm_each and not _confirm_analyze(target):
            print(f"Skipping {target} at user request.")
            continue

        try:
            # --- trace: read file ---
            if mlflow_enabled and mlflow is not None and hasattr(mlflow, "start_span"):
                with mlflow.start_span(
                    name="read_file", attributes={"path": str(target)}
                ):
                    content = read_file_content(target)
            else:
                content = read_file_content(target)
        except (FileNotFoundError, UnicodeDecodeError) as exc:
            print(f"Skipping {target}: {exc}")
            exit_code = 1
            continue

        # Compute relative path for logging.
        try:
            relative = target.relative_to(root) if root else Path(target.name)
        except Exception:
            relative = Path(target.name)

        print(f"\n=== Analyzing {target} ===")
        t0 = time.perf_counter()
        # --- trace: model inference ---
        if mlflow_enabled and mlflow is not None and hasattr(mlflow, "start_span"):
            with mlflow.start_span(
                name="dspy_inference",
                attributes={
                    "file": str(relative),
                    "mode": mode.value,
                    "bytes_in": len(content.encode("utf-8", errors="ignore")),
                },
            ):
                prediction = analyzer(file_path=str(target), file_content=content)
        else:
            prediction = analyzer(file_path=str(target), file_content=content)
        dt_ms = int((time.perf_counter() - t0) * 1000)

        if raw:
            output_text = repr(prediction)
            print(output_text)
        else:
            output_text = render_prediction(prediction, mode=mode.render_key)
            print(output_text, end="")

        # --- trace: write output ---
        if mlflow_enabled and mlflow is not None and hasattr(mlflow, "start_span"):
            with mlflow.start_span(
                name="write_output", attributes={"file": str(relative)}
            ):
                output_path = _write_output(
                    target,
                    output_text,
                    root=root,
                    output_dir=output_dir,
                    suffix=mode.file_suffix,
                )
        else:
            output_path = _write_output(
                target,
                output_text,
                root=root,
                output_dir=output_dir,
                suffix=mode.file_suffix,
            )
        print(f"Saved {mode.output_description} to {output_path}")

        if mlflow_enabled and mlflow is not None:
            # Nested run per analyzed file
            run_name = str(relative)
            with mlflow.start_run(nested=True, run_name=run_name):  # type: ignore[attr-defined]
                mlflow.log_params(  # type: ignore[attr-defined]
                    {
                        "path": str(relative),
                        "raw": str(raw),
                        "confirm_each": str(confirm_each),
                        "recursive": str(recursive),
                        "globs": ",".join(include_globs or []),
                        "excluded_dirs": ",".join(exclude_dirs or []),
                    }
                )
                in_bytes = len(content.encode("utf-8", errors="ignore"))
                out_chars = len(output_text)
                mlflow.log_metrics(  # type: ignore[attr-defined]
                    {
                        "input_bytes": float(in_bytes),
                        "output_chars": float(out_chars),
                        "duration_ms": float(dt_ms),
                    }
                )
                mlflow.set_tags({"analysis_mode": mode.value})  # type: ignore[attr-defined]
                mlflow.log_artifact(str(output_path))  # type: ignore[attr-defined]

                if hasattr(mlflow, "update_current_trace"):
                    try:
                        mlflow.update_current_trace(
                            tags={"file": str(relative), "analysis_mode": mode.value}
                        )
                    except Exception:
                        pass

    return exit_code


def main(argv: list[str] | None = None) -> int:
    load_dotenv()

    parser = build_parser()
    args = parser.parse_args(argv)

    provider_value = _resolve_option(
        args.provider, "DSPYTEACH_PROVIDER", DEFAULT_PROVIDER.value
    )
    try:
        provider = Provider(provider_value)
    except ValueError:  # pragma: no cover - argparse handles this
        valid = ", ".join(p.value for p in Provider)
        parser.error(f"Unsupported provider '{provider_value}'. Choose from: {valid}.")

    defaults = PROVIDER_DEFAULTS[provider]
    model_name = _resolve_option(args.model_name, "DSPYTEACH_MODEL", defaults["model"])
    api_base_default = defaults.get("api_base")
    api_base = _resolve_option(args.api_base, "DSPYTEACH_API_BASE", api_base_default)
    api_key = _resolve_option(args.api_key, "DSPYTEACH_API_KEY", None)
    if provider is Provider.OPENAI and not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
    if provider is Provider.LMSTUDIO and not api_key:
        api_key = "lm-studio"

    if provider is Provider.LMSTUDIO and api_base:
        try:
            _probe_openai_provider(api_base, api_key)
        except ProviderConnectivityError as exc:
            print("Unable to reach the LM Studio server before starting analysis.")
            print(f"Details: {exc}")
            print(
                "Start LM Studio's local API server (Developer tab → Start Server or `lms server start`) and re-run, or pass --api-base to match the running port."
            )
            return 1

    configure_model(provider, model_name, api_base=api_base, api_key=api_key)
    stop_model: str | None = model_name if provider is Provider.OLLAMA else None

    # Evaluate MLflow configuration
    mlflow_enabled = bool(args.mlflow)
    if mlflow_enabled and mlflow is None:  # type: no cover
        print(
            "Warning: --mlflow requested but MLflow is not installed. Disabling MLflow."
        )
        mlflow_enabled = False

    exit_code = 0
    try:
        analysis_mode = AnalysisMode(args.mode)
        prompt_text: str | None = None
        if analysis_mode is AnalysisMode.REFACTOR:
            try:
                prompt_text = _resolve_prompt_text(args.prompt)
            except (FileNotFoundError, ValueError) as exc:
                print(f"Error resolving prompt: {exc}")
                return 2
        elif args.prompt:
            print("Warning: --prompt is ignored outside refactor mode.")
        output_dir = (
            Path(args.output_dir).expanduser().resolve() if args.output_dir else None
        )
        if output_dir:
            print(f"Writing {analysis_mode.output_description}s to {output_dir}")
        else:
            print(f"Writing {analysis_mode.output_description}s in place")
        exclude_dirs = None
        if args.exclude_dirs:
            parsed: list[str] = []
            for entry in args.exclude_dirs:
                parsed.extend(
                    segment.strip() for segment in entry.split(",") if segment.strip()
                )
            exclude_dirs = parsed or None

        # --- MLflow parent run + root span for the whole invocation ---
        if mlflow_enabled and mlflow is not None:
            if args.mlflow_experiment:
                try:
                    mlflow.set_experiment(args.mlflow_experiment)  # type: ignore[attr-defined]
                except Exception as exc:
                    print(f"Warning: failed to set MLflow experiment: {exc}")

            tracing_supported = hasattr(mlflow, "start_span") and hasattr(
                mlflow, "update_current_trace"
            )
            run_name = f"analyze:{Path(args.path).name}"

            if tracing_supported:
                with mlflow.start_span(name="analyze_file_cli") as root_span:
                    # inputs on the root span when API exists
                    try:
                        if hasattr(root_span, "set_inputs"):
                            root_span.set_inputs({
                                "path": args.path,
                                "mode": analysis_mode.value,
                            })
                    except Exception:
                        pass

                    try:
                        mlflow.update_current_trace(
                            tags={
                                "provider": provider.value,
                                "api_base_set": str(bool(api_base)),
                            }
                        )
                    except Exception:
                        pass

                    with mlflow.start_run(run_name=run_name):  # type: ignore[attr-defined]
                        mlflow.set_tags(  # type: ignore[attr-defined]
                            {
                                "provider": provider.value,
                                "mode": analysis_mode.value,
                                "api_base": str(bool(api_base)),
                            }
                        )
                        mlflow.log_params(  # type: ignore[attr-defined]
                            {
                                "provider": provider.value,
                                "model": model_name,
                                "api_base": api_base or "",
                                "path": args.path,
                                "output_dir": str(output_dir) if output_dir else "",
                                "recursive": str(not args.non_recursive),
                            }
                        )
                        exit_code = analyze_path(
                            args.path,
                            raw=args.raw,
                            recursive=not args.non_recursive,
                            include_globs=args.include_globs,
                            confirm_each=args.confirm_each,
                            exclude_dirs=exclude_dirs,
                            output_dir=output_dir,
                            mode=analysis_mode,
                            prompt_text=prompt_text,
                            mlflow_enabled=True,
                            root_hint=Path(args.path).expanduser().resolve(),
                        )
            else:
                with mlflow.start_run(run_name=run_name):  # type: ignore[attr-defined]
                    mlflow.set_tags(  # type: ignore[attr-defined]
                        {
                            "provider": provider.value,
                            "mode": analysis_mode.value,
                            "api_base": str(bool(api_base)),
                        }
                    )
                    mlflow.log_params(  # type: ignore[attr-defined]
                        {
                            "provider": provider.value,
                            "model": model_name,
                            "api_base": api_base or "",
                            "path": args.path,
                            "output_dir": str(output_dir) if output_dir else "",
                            "recursive": str(not args.non_recursive),
                        }
                    )
                    exit_code = analyze_path(
                        args.path,
                        raw=args.raw,
                        recursive=not args.non_recursive,
                        include_globs=args.include_globs,
                        confirm_each=args.confirm_each,
                        exclude_dirs=exclude_dirs,
                        output_dir=output_dir,
                        mode=analysis_mode,
                        prompt_text=prompt_text,
                        mlflow_enabled=True,
                        root_hint=Path(args.path).expanduser().resolve(),
                    )
        else:
            exit_code = analyze_path(
                args.path,
                raw=args.raw,
                recursive=not args.non_recursive,
                include_globs=args.include_globs,
                confirm_each=args.confirm_each,
                exclude_dirs=exclude_dirs,
                output_dir=output_dir,
                mode=analysis_mode,
                prompt_text=prompt_text,
                mlflow_enabled=False,
                root_hint=Path(args.path).expanduser().resolve(),
            )
    except Exception as exc:
        if LiteLLMInternalServerError and isinstance(exc, LiteLLMInternalServerError):
            message = str(exc)
            if exc.__cause__:
                message = f"{message} (cause: {exc.__cause__})"
            print("Model request failed while generating the report.")
            print(f"Details: {message}")
            if provider is Provider.LMSTUDIO:
                print(
                    f"Confirm the LM Studio server is running and reachable at {api_base}."
                )
            return 1
        raise
    except (FileNotFoundError, IsADirectoryError) as exc:
        parser.print_usage(sys.stderr)
        print(f"{parser.prog}: error: {exc}", file=sys.stderr)
        exit_code = 2
    except KeyboardInterrupt:
        exit_code = 1
    finally:
        if provider is Provider.OLLAMA and not args.keep_provider_alive and stop_model:
            stop_ollama_model(stop_model)

    return exit_code

if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
