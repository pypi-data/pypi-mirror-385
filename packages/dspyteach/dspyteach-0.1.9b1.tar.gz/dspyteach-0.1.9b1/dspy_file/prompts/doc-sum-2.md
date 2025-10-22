<!-- $1=document name or identifier, $2=first target topic, $3=second target topic, $4=third target topic, $5=citation source to reference -->

# {$2 or Inferred Name}

## Task

* Produce a hierarchical outline of $1 using headings and bullets.
* In separate steps, extract and condense only material about $2, $3, and $4.
* Attach citations to $5 with explicit line ranges.
* If a target topic is absent, state that it is missing.

## Steps

1. Scan $1 and draft the outline.
2. Locate content relevant to each of $2, $3, $4.
3. Summarize each located section in plain language.
4. Add citations to $5 with line spans.
5. Note any missing sections.

## Output format

* **Outline**

  * Bulleted hierarchy for $1.
* **Targeted summaries**

  * **$2:** short summary + citations to $5 with line ranges.
  * **$3:** short summary + citations to $5 with line ranges.
  * **$4:** short summary + citations to $5 with line ranges.
* **Missing**

  * List any of $2, $3, $4 not found.

## Validation

* Summaries reference only the specified topics.
* Every claim includes a citation to $5 with line ranges.
* No content outside the outline and targeted summaries.
