# Evidence Model

## The core distinction

SkillGraph tracks three separate facts about a skill, never conflating them:

| State | Table | Meaning |
|---|---|---|
| **Claimed** | `user_skills` (`claimed=true`) | The user says they have this skill. |
| **Evidenced** | `evidence` rows exist for that skill | There is at least one supporting record. |
| **Demonstrated** | Computed | The evidence, once scored, is strong enough to be believable (see `capability-scoring.md`). |

A skill can be **claimed with no evidence** at all — that's an *evidence gap*
(`SkillGraphEntry.is_evidence_gap` in `app/engines/graph_service.py`), which is
reported distinctly from a *skill gap* (the user doesn't have the skill at
all). See `docs/gap-engine.md` for how the two are surfaced differently.

## Evidence types

`PROJECT`, `WORK_EXPERIENCE`, `INTERNSHIP`, `CERTIFICATION`, `COURSE`,
`GITHUB_REPOSITORY`, `PUBLICATION`, `COMPETITION`, `PORTFOLIO`, `ASSESSMENT`.

Each type has an inherent base strength (see `capability-scoring.md`) —
e.g. verified work experience counts for more than a course, by design.

## Evidence fields

```
skill_id, type, title, description, date, source,
verification_status  (UNVERIFIED | SELF_REPORTED | VERIFIED)
complexity            (1-5, defaults to 3)
project_id            (optional link to a Project record)
```

## Projects as an evidence source

A `Project` can have many `Evidence` rows (one per skill it demonstrates) and
many `ProjectSkill` rows (the skills it's tagged with, independent of whether
formal Evidence exists yet — this lets the frontend show "skills used in this
project" even before a user has filed a dedicated Evidence record for each
one).

## Assessments as an evidence source

A completed skill assessment that scores >= 70% automatically creates a
`VERIFIED` `ASSESSMENT`-type Evidence row (`app/engines/assessment_engine.py`,
`qualifies_as_evidence`). Below that threshold, the attempt is recorded but
does **not** become evidence — a bad assessment attempt should not inflate a
capability score.

## What the platform will never claim

An evidence record is not proof of true human expertise, and a high
capability score is not a guarantee of on-the-job performance. Every score
and gap classification is described in the UI and API as an *evidence-based
indicator*, not a measurement of the person. See `docs/security.md` and the
disclaimer text used throughout the frontend (`app/routers/dashboard.py`,
`components/Disclaimer.tsx`).
