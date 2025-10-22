<!--
$1 = source document path or identifier
$2 = outline granularity and style (e.g., headings-only, headings+bullets)
$3 = topic/category A to extract
$4 = topic/category B to extract
$5 = topic/category C to extract
$6 = citation format details (e.g., include file path and line ranges)
$7 = behavior if a requested topic is missing
-->

# {Targeted Outline and Section Summaries}

## Step 1 — Outline

Create an outline of $1 using $2.

## Step 2 — Targeted extracts and summaries

For each topic below, locate the relevant section(s), pull the content, and produce a concise summary. Provide citations per $6. If a topic is not found, follow $7.

* (A) $3
* (B) $4
* (C) $5

## Output format

* **Outline:** structured as specified by $2.
* **Extracts:** for each topic (A–C)

  * Pulled text: short excerpt(s)
  * Summary: 2–5 bullets
  * Citations: per $6

## Validation

* Confirm that only topics $3–$5 are summarized.
* Confirm citation format matches $6.
* Apply $7 for any missing topic.
