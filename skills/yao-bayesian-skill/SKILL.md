---
name: yao-bayesian-skill
description: Convert uncertain real-world choices into an auditable Bayesian evidence-to-action report with priors, evidence grading, posterior update, action thresholds, sensitivity checks, multi-turn decision logs, and Markdown plus bilingual HTML output. Do not use for Bayes theorem tutoring, homework, generic brainstorming with no report, or final licensed medical, legal, or financial advice.
---

# Yao Bayesian Skill

## Use This Skill For

- structure a vague choice into hypothesis, time horizon, success metric, and actions
- set a prior, grade evidence, update posterior, compare action thresholds, and recommend next information
- start from incomplete input with a weak prior, then improve the judgment through multi-turn questioning
- export one synchronized Chinese-first `markdown` plus bilingual `html` report

## Do Not Route Here

- Bayes theorem tutoring or homework-only calculations
- broad research or brainstorming with no explicit decision report
- final professional medical, legal, or investment advice

## Default Workflow

1. Use `references/intake-contract.md` to convert the request into one structured decision brief.
2. If input is incomplete, read `references/multi-turn-dialogue-loop.md`; start with a weak prior and ask the minimum next questions.
3. Use `references/evidence-prior-playbook.md` to grade evidence and choose the lightest valid update path.
4. Run `references/prior-hygiene-checklist.md`; show only the 3-5 principles most relevant to this case.
5. Maintain the round log: user input, remaining gap, update path, probability change, and decision readiness.
6. Run `scripts/bayesian_decision_report.py` for canonical JSON or `scripts/generate_report_bundle.py` for `markdown + html`.
7. Finalize with `references/decision-report-contract.md`, `references/report-export-pipeline.md`, and `references/sensitivity-and-safety.md`.

## Iteration And Implementation Constraints

When extending this skill: state assumptions before coding, keep the smallest valid workflow, touch only files required by the request, and define user-visible success checks before editing. Typical checks: incomplete input yields a weak prior plus follow-up questions; each round is logged; the report explains belief changes; HTML/Markdown still render the intended guidance.

## Output Contract

- Produce a decision report, not a formula dump; mark numbers as observed, estimated, or assumed.
- Put the plain-language conclusion and action recommendation before technical sections.
- Include weak evidence, dependence risk, sensitivity, prior-hygiene checks, and high-risk disclaimers when relevant.
- For multi-turn use, log prior, posterior, readiness, gaps, and formula/update path for each round.
- Reports default to Simplified Chinese; HTML also supports Chinese/English switching, sticky navigation, collapsible advanced sections, and top-right `Print` / `Save as PDF`.
- Printing or saving HTML as PDF should expand folded sections first.

## Reference Map

- `references/intake-contract.md`: request-to-brief conversion
- `references/multi-turn-dialogue-loop.md`: incomplete-input handling and iterative questioning
- `references/evidence-prior-playbook.md`: evidence tiers, priors, update-path selection
- `references/prior-hygiene-checklist.md`: default judgment priors for checking priors, evidence, and action intensity
- `references/decision-report-contract.md`: required report sections and schema alignment
- `references/report-export-pipeline.md`: automatic HTML/Markdown generation and bilingual HTML rules
- `references/sensitivity-and-safety.md`: sensitivity analysis and high-risk disclaimers
- `scripts/bayesian_decision_report.py`: canonical V0/V1 calculation
- `scripts/generate_report_bundle.py`: Chinese-first Markdown plus bilingual HTML
