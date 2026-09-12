# Gap Engine

Implemented in [`apps/api/app/engines/gap_engine.py`](../apps/api/app/engines/gap_engine.py).

## Two different kinds of gap

1. **Skill gap** — the user has no claim and no evidence for a required skill.
2. **Evidence gap** — the user *claims* the skill, but no `Evidence` row backs
   it up (`RoleSkillGap.is_evidence_gap`). This is surfaced separately in the
   API (`GET /api/skill-gaps` returns a dedicated `evidence_gaps` bucket) and
   in the UI's Gap Center, because the fix is different: an evidence gap needs
   *proof*, not necessarily new *learning*.

## Prioritization

Not all gaps matter equally. Each gap gets a `priority_score`:

```
priority_score = weight(importance) * (1 - coverage)
```

where `coverage = min(score / 100, 1.0)`. This combines "how much the role
cares about this skill" with "how far the user currently is from covering
it" — a CRITICAL skill at 0% outranks a CRITICAL skill at 60%, which in turn
outranks a LOW-importance skill at 0%. Gaps returned by `compute_role_gap()`
are pre-sorted by this score, descending.

## Dependency-aware gaps

Rather than reporting "Missing MLOps" in isolation, `GET /api/skill-gaps`
attaches the resolved prerequisite chain from `dependency_engine.py` to every
gap (e.g. `Docker -> CI/CD -> Model Deployment -> Model Monitoring -> MLOps`),
so the UI can explain *why*, not just *that*, a skill is missing.

## API shape

`GET /api/skill-gaps?role_id=N` groups a role's open gaps into:

- `critical_gaps` — CRITICAL importance, not already a strong match
- `high_priority_gaps` — HIGH importance
- `medium_priority_gaps` — MEDIUM/LOW importance
- `evidence_gaps` — any gap where the skill is claimed but unevidenced

This mirrors the Gap Center UI (`apps/web/src/app/(app)/gaps/page.tsx`)
directly — the frontend does not re-derive any of this classification itself.
