# Role Matching

Implemented in [`apps/api/app/engines/gap_engine.py`](../apps/api/app/engines/gap_engine.py).

## Role skill requirements

Each `RoleSkill` row pairs a role with a skill, an `importance`
(`CRITICAL` / `HIGH` / `MEDIUM` / `LOW`), and a `min_capability_score`
threshold (not currently used to hard-gate a match, but recorded for future
use and shown in the API so a UI can flag "below the expected bar for this
role" explicitly).

## Readiness formula

```
weight(importance) = CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1
coverage(skill)     = min(capability_score / 100, 1.0)
readiness           = 100 * sum(weight_i * coverage_i) / sum(weight_i)
```

This is a **weighted capability coverage estimate**. It is displayed
everywhere as "your evidence currently covers approximately X% of the
weighted capabilities modeled for this demo role" — never as a hiring
probability or a guarantee of qualification (see `docs/security.md`).

## Per-skill classification

```python
def classify(score, has_evidence):
    if not has_evidence or score < 15: return MISSING
    if score < 40:  return WEAK_MATCH
    if score < 75:  return PARTIAL_MATCH
    return STRONG_MATCH
```

Note that a skill with a nonzero score but **no evidence record** is still
classified `MISSING` — score alone never overrides the evidence check, which
is what keeps "claimed but unsupported" skills from silently counting toward
readiness.

## Ranking roles ("best-fit")

`rank_roles_by_fit()` computes the gap result for every role and sorts by
readiness descending — this powers the "Ranked role matches" / best-fit
explorer. It is explicitly labeled as *evidence-based capability alignment*,
not employment probability.

## Role comparison

`GET /api/roles/compare?ids=1,2,3` computes the gap result for each role and
returns a shared skill × role importance matrix, so the frontend can render
the side-by-side comparison table described in the product brief.
