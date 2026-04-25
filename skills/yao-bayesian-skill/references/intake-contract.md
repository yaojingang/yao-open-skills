# Intake Contract

Turn the user's raw request into one decision brief before doing calculations.

## Minimum Brief

Capture these fields explicitly:

- `title`: short decision label
- `decision_question`: the concrete decision to make
- `hypothesis`: what must be true for the main action to be justified
- `time_horizon`: how long the judgment should hold
- `success_metric`: what counts as success
- `actions`: at least two options, ideally three
- `known_evidence`: observed signals, counts, or source pointers
- `risk_tolerance`: low, medium, or high
- `cost_or_utility_view`: enough information to compare actions
- `high_risk_domain`: true for medical, legal, financial, or other regulated domains

## Reference-Class Rule

Before setting a prior, name the closest usable reference class.

Ask:

- What similar cases are actually comparable?
- What important factors make this case different?
- Which signals are base-rate signals and which are case-specific evidence?

If the reference class is weak, say so and downgrade prior confidence.

## Missing-Field Rule

If one of these is missing, do not hide the gap:

- no explicit hypothesis
- no time horizon
- no action set
- no success metric
- no usable evidence

State the blockers first, then propose the smallest additional information needed.

When the user only gives a decision question plus current state:

- start with a weak prior and label it as provisional
- give one preliminary judgment instead of pretending the final decision is ready
- ask only the next 1 to 3 highest-value follow-up questions
- begin a multi-turn log so each new answer can update the prior or posterior cleanly

## Action Framing Rule

Do not ask only "Is H true?"

Always connect the judgment to actions such as:

- act now
- run a lower-cost test first
- pause

This skill is for evidence-to-action reporting, not for abstract probability discussion.
