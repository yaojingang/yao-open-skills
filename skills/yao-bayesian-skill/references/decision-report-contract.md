# Decision Report Contract

Every report should follow this structure.

## Required Sections

1. One-sentence conclusion
2. Decision question
3. Prior setup
4. New evidence table
5. Bayesian update
6. Natural-frequency explanation
7. Action thresholds
8. Expected value comparison
9. Sensitivity analysis
10. Next information to collect
11. Caveats and risks
12. Appendix or calculation note

When export is enabled, the same report should be rendered consistently to:

- `json` as the canonical machine-readable source
- `markdown` as the readable source draft
- `html` as the visual report
- `pdf` as the shareable fixed-layout artifact
- `docx` as the editable document artifact

## Mandatory Distinctions

Never mix these categories:

- observed
- estimated
- assumed

The report should let a reviewer tell which numbers came from data, which came from judgment, and which came from policy or utility assumptions.

## Natural-Frequency Rule

Translate the main result into a concrete frequency statement.

Example:

- "Out of 100 similar cases, the prior suggests about 18 successes."
- "After current evidence, the estimate becomes about 47 successes out of 100."

## Output Schema Alignment

Target the JSON layout in `templates/report.schema.json`.

At minimum, fill:

- `summary`
- `prior`
- `evidence`
- `posterior`
- `decision`
- `sensitivity`
- `natural_frequency`
- `warnings`

## Recommendation Rule

Do not stop at posterior probability.

The conclusion must answer:

- what to do now
- why that action is justified
- what evidence would change the recommendation
- when to reopen the decision
