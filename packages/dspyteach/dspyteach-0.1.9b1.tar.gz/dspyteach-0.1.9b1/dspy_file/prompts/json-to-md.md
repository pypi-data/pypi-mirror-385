<!--
$1: JSON payload to be rendered
$2: Document title text
$3: Introductory summary (one short paragraph)
$4: Keys to omit or redact (array)
$5: Per-section item display cap (integer)
$6: Date-like key names (array)
$7: URL-like key names (array)
-->

# JSON → Markdown Renderer Template

**Task:** Produce a readable, skimmable Markdown document from $1.

## Acceptance Criteria

1. A single H1 appears at the top; every top-level object/array in $1 is surfaced as its own section.
2. Arrays of uniform objects render as tables with stable columns; mixed or sparse arrays render as bullet lists.
3. Nested structures are grouped into subsections with breadcrumb-style paths.
4. Any keys listed in $4 are excluded; secret-looking values are redacted.
5. When item counts exceed $5, show the first $5 and append a “+N more” indicator.
6. No fields are invented; preserve source ordering; output must be valid Markdown.

## Process

* Parse $1. If parsing fails, output exactly `Invalid JSON` followed by a minimal valid example inside a fenced block.
* Begin with an “At a glance” summary (≤6 bullets).
* Then render detailed sections in source order, choosing table vs list per structure.
* Conclude with “Data Notes” documenting truncations, redactions, and any schema inferences.

## Parameters

* Title: $2
* Intro: $3
* Max nesting depth: (set as needed; default sensible)
* Table minimum width (columns): (set as needed; default sensible)
* Wrap width (characters): (set as needed; default sensible)
* Date keys: $6
* URL keys: $7

## Output Format

* Emit Markdown only.
* The first line must be `#` followed by $2.

## Sections to Generate

* **At a glance** — concise bullets summarizing counts, key entities, notable timestamps/URLs (use $6 and $7 to identify).
* **Per-root section** — one per top-level key/array from $1.

  * **Subsections** — follow nested paths (e.g., `parent › child › leaf`).
  * Choose **Table** if objects are shape-consistent; otherwise use a **List**.
  * Apply omissions ($4), redactions, date/url formatting ($6, $7), and item cap ($5).
* **Data Notes** — list truncations, redactions, assumptions, and schema hints observed during rendering.

## Tests (sanity checks)

* Parsing error path returns only the exact failure string plus a minimal example.
* Large arrays respect $5 and show correct “+N more”.
* Uniform arrays become tables; mixed arrays do not.
* Source key order is preserved at every level.
* Redactions and omissions reflect $4 precisely.

## Open Questions

* What defaults should apply for max depth, table width, and wrap width when not provided?
* Should date and URL detection rely solely on $6/$7 or also on heuristics?
