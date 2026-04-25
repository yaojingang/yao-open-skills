# Multi-turn Dialogue Loop

Use this workflow when the user starts with only a decision question plus current state, not a complete structured brief.

## Goal

Turn an incomplete decision conversation into a documented Bayesian process:

1. weak initial prior
2. preliminary judgment
3. next missing-information questions
4. iterative prior or posterior updates
5. final decision-readiness call
6. round-by-round process log for the final report

## Operating Rules

- Do not wait for perfect input before giving the first useful answer.
- Start with the lightest defensible prior and say clearly that it is provisional.
- After every round, record:
  - what the user added
  - which uncertainty gap it addresses
  - the prior at the start of the round
  - the Bayesian update path used in the round
  - the posterior at the end of the round
  - current decision readiness
  - remaining gaps
- Treat the previous round's posterior as the next round's starting prior unless a better reference class forces a reset.
- Stop the loop and produce a final decision only when either:
  - readiness is high enough and key gaps are closed, or
  - the best action is clearly to hold or run a low-cost test first

## Round Template

Each round should be serializable into the request JSON:

```json
{
  "round": 1,
  "stage": {"zh": "初始问题澄清", "en": "Initial framing"},
  "user_input_summary": {"zh": "...", "en": "..."},
  "assistant_focus": {"zh": "...", "en": "..."},
  "new_information": [{"zh": "...", "en": "..."}],
  "assistant_next_questions": [{"zh": "...", "en": "..."}],
  "missing_information": [{"zh": "...", "en": "..."}],
  "prior_probability_before": 0.18,
  "bayes_update": {
    "update_method": "odds-update",
    "likelihood_ratio": 1.6,
    "direction": "support",
    "dependency_discount": 0.9
  },
  "posterior_probability_after": 0.26,
  "decision_readiness": 0.44,
  "interim_judgment": {"zh": "...", "en": "..."}
}
```

## Decision-readiness Guidance

- `0.00 - 0.44`: still collecting critical information
- `0.45 - 0.74`: nearly ready; one or two gaps still matter
- `0.75 - 1.00`: ready to make a formal decision

Readiness is not the same as posterior probability. It reflects whether the decision is mature enough to act on.
