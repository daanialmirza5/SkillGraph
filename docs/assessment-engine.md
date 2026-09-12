# Assessment Engine

Implemented in [`apps/api/app/engines/assessment_engine.py`](../apps/api/app/engines/assessment_engine.py).
Question bank: [`seed/assessment_questions_data.py`](../seed/assessment_questions_data.py) (31 hand-written MCQs
across 22 skills, Beginner/Intermediate/Advanced, each with an explanation).

## Scoring

Deterministic exact-match scoring against `AssessmentQuestion.correct_answer`.
A missing or wrong answer counts as incorrect — there is no partial credit.

```
percentage = 100 * correct / total
signal:
  >= 85% -> STRONG
  >= 65% -> PRACTICAL
  >= 40% -> DEVELOPING
  else   -> FOUNDATIONAL
```

## Assessment -> Evidence

An attempt becomes a piece of `VERIFIED` `ASSESSMENT`-type evidence only if
`percentage >= 70` (`qualifies_as_evidence`). This is a deliberate threshold:
a mediocre quiz result should not silently inflate a capability score, and an
assessment is explicitly documented (in the UI and here) as a **capability
signal**, not a professional certification and not equivalent to real-world
work experience — see `docs/evidence-model.md` for how evidence types are
weighted differently in scoring.

## Why MCQs and not open-ended grading

Open-ended answers would require an LLM to grade, which reintroduces the
grounding problem this platform is designed to avoid (see
`docs/ai-architecture.md`). Deterministic MCQ scoring means an assessment
result is always reproducible and auditable.
