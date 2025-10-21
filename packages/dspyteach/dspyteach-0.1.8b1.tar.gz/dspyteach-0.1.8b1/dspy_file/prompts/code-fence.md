# Command: /markdown:wrap-md-fence

# Usage: /markdown:wrap-md-fence "your content here"

# Args

# - {{content}}: raw bytes to wrap verbatim inside the fence

prompt = """
Wrap the provided {{content}} verbatim with a Markdown code fence labeled md.

Rules:

* Zero changes to {{content}} (byte-for-byte).
* Preserve encoding, line endings, and terminal newline presence/absence.
* No additional output or whitespace outside the fence.

Output exactly:

```md
{{content}}
```

Acceptance:

* Inner bytes are identical to {{content}}.
* Only the opening line `md and the closing` are added.
  """
