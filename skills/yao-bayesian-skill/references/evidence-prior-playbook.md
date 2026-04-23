# Evidence And Prior Playbook

## Evidence Quality Tiers

Use this grading in the final report.

| Grade | Typical source | How to use |
| --- | --- | --- |
| A | meta-analysis, systematic review, regulator guidance, official statistics, canonical textbook treatment | strong prior or strong update input |
| B | peer-reviewed paper, public dataset, industry standard, well-documented benchmark | medium-strength prior or update input |
| C | structured expert elicitation, internal historical data, carefully gathered field evidence | usable with explicit caveats |
| D | LLM suggestion, analogy, common sense, informal heuristic | weak prior only |
| E | blog post, marketing copy, social post, unattributed claim | do not use as core evidence |

## Prior Construction

Prefer one of these patterns:

- binary event with limited data: `Beta(alpha, beta)`
- binary event with only a point prior: `probability + equivalent_sample_size`
- quick report with already-encoded evidence strength: prior probability only

Always record:

- prior source summary
- reference class
- source quality
- equivalent sample size or prior strength
- what could make the prior wrong

## Weak-Prior Rule

If the prior comes mostly from common sense, analogy, or model-generated guesses:

- mark it as weak
- keep equivalent sample size low
- widen the sensitivity range
- avoid strong action claims

## Update Path Selection

Use the lightest valid method:

1. `odds update`
   - best when evidence is already expressed as likelihood ratios or Bayes factors
   - useful for quick evidence-to-action reports
2. `beta-binomial`
   - best when the user has trial counts and successes
   - good for conversion, defect, pass-rate, or uptake questions
3. `stop and escalate`
   - when evidence items are strongly dependent
   - when multiple hidden variables drive the result
   - when causal intervention matters more than static prediction

## Dependency Rule

Do not blindly multiply overlapping evidence.

When signals may come from the same underlying source:

- lower the `dependency_discount`
- explain the overlap risk
- prefer a lower-confidence recommendation

## Likelihood-Ratio Guidance

Each evidence item should say:

- what observation was seen
- whether it supports or weakens the hypothesis
- what LR or Bayes-factor assumption is being used
- what quality grade justifies that assumption

If you cannot justify the LR even approximately, say that the evidence is qualitative and avoid fake precision.
