# Sensitivity And Safety

## Minimum Sensitivity Pass

Every report must test at least:

- prior sensitivity
- evidence-strength sensitivity
- action-threshold sensitivity

The bundled script directly supports prior and evidence sensitivity. If threshold or utility assumptions matter, discuss them explicitly in the report even when the script is not enough.

## Stability Language

Use one of these labels:

- `stable`: main recommendation stays the same across the tested range
- `mixed`: posterior range is moderate or one scenario changes the recommendation
- `unstable`: multiple plausible settings produce different recommended actions

If the result is unstable, bias toward lower-cost information gathering.

## Information-Value Heuristic

More information is especially valuable when:

- the top two actions have similar expected value
- the posterior is near a key action threshold
- evidence quality is mostly C or D
- reference-class fit is weak

The next-information section should recommend one concrete test or data-collection move, not a vague request for more research.

## High-Risk Domain Rule

For medical, legal, financial, or regulated decisions:

- label the report as decision support only
- do not frame it as final advice
- surface the limits of the evidence and the model
- recommend licensed or domain-specific review before action

## Stop Conditions

Stop and explain the limitation when:

- the user wants a final professional judgment in a regulated domain
- the evidence graph is clearly multi-causal and cannot be represented safely with the MVP methods
- the LR assumptions are too speculative to justify numeric updating
