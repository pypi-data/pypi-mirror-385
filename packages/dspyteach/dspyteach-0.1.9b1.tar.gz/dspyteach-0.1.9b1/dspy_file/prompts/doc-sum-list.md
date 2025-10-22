<!-- $1 = document name/title, $2 = target topics (list), $3 = citation source -->

# Document Outline and Targeted Summaries

## Task

* Create an outline of $1 using headings and bullets.
* In separate steps, pull and summarize only the sections about: $2.
* Cite $3 with line ranges for each pulled summary.
* If a section is not present, explicitly state that it is missing.

## Inputs

* Document: $1
* Topics: $2
* Citation source: $3

## Output format

1. **Outline of $1**

   * Bulleted hierarchy of all headings.

2. **Targeted section summaries**
   For each item in $2:

   * **Section:** *topic*
   * **Summary:** 2–4 sentences focused on that topic only.
   * **Citations:** $3, lines X–Y.
   * **Status:** “Not present” if the section does not exist.

## Notes

* Do not summarize content outside the requested topics.
* Include line ranges with every citation.
* Keep wording concise.
