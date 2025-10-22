<!-- $1=Document name or ID, $2=Topic 1, $3=Topic 2, $4=Topic 3, $5=Citation source -->

# Targeted Outline and Summaries

## Inputs

* Document: $1
* Focus areas: $2, $3, $4
* Citations: $5 with line ranges

## Procedure

1. Produce a headings-and-bullets outline of $1.
2. For each focus area ($2, $3, $4), locate relevant material only and write a concise summary.
3. Attach citations to each summary using $5 with line intervals.
4. If a focus area is absent, state that explicitly.

## Constraints

* Summaries include only content tied to their focus area.
* Use line intervals for every cited excerpt.
* No content outside scope.

## Output format

### Outline

* (bulleted hierarchy of $1)

### Summaries

#### $2

* Summary
* Citations: $5 lines X–Y, ...

#### $3

* Summary
* Citations: $5 lines X–Y, ...

#### $4

* Summary
* Citations: $5 lines X–Y, ...

### Missing

* List any focus areas not found, or “none.”
