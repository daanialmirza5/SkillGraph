# Learning Path & Recommendation Engines

## Learning Path

Implemented in [`apps/api/app/engines/learning_path.py`](../apps/api/app/engines/learning_path.py).

1. Compute the role gap for (user, role).
2. Take the top `max_gaps` (default 3) open gaps (`MISSING` or `WEAK_MATCH`),
   already sorted by `priority_score` (see `docs/gap-engine.md`).
3. For each, resolve its full prerequisite chain via the dependency engine
   and merge all chains into one de-duplicated, ordered list of skills.
4. For each skill in the path, attach: *why* it's included (which gap it
   serves and that skill's current match state), *what evidence to create*
   next, and any matching `LearningResource` rows.

This is fully deterministic — no LLM involvement — which is what makes it
safe to show as an actionable, reproducible plan.

## Project Recommendations

Implemented in [`apps/api/app/engines/recommendation_engine.py`](../apps/api/app/engines/recommendation_engine.py),
backed by curated templates in
[`apps/api/app/data/project_templates.py`](../apps/api/app/data/project_templates.py)
(24 templates, each tagged with the skills it demonstrates).

Rather than asking an LLM to invent a project idea, the engine:

1. Computes the role gap and takes every skill classified `MISSING`,
   `WEAK_MATCH`, or `PARTIAL_MATCH` as an "open gap".
2. Scores every project template by the total *importance weight* of the
   open gaps it overlaps with (`closed_weight`).
3. Returns the top-N templates, each annotated with exactly which gaps it
   closes and an `expected_gap_reduction` label (`LOW`/`MEDIUM`/`HIGH`,
   derived from `closed_weight / total_role_weight`).

Because recommendations are drawn from a fixed, human-curated catalog rather
than generated freeform, every recommendation is inherently explainable: the
UI shows precisely which required skills the project would produce evidence
for, and why those skills were prioritized.

## Human-in-the-loop workflow

A recommendation can be persisted (`POST /api/recommendations/generate`) and
then moved through `SUGGESTED -> ACCEPTED | EDITED | REJECTED`
(`POST /api/recommendations/{id}/decision`). Every decision is written to the
audit log (`RECOMMENDATION_ACCEPTED` / `RECOMMENDATION_REJECTED`). The AI
analyst can *suggest* a recommendation is worth generating, but only this
deterministic, human-approved endpoint changes recommendation state.
