"""Deterministic assessment scoring.

An assessment produces a *capability signal*, not a professional certification.
A high-scoring attempt can optionally become a piece of VERIFIED evidence.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.models import AssessmentQuestion


@dataclass
class AssessmentResult:
    score: int
    total: int
    percentage: float
    capability_signal: str
    per_question: list[dict]


def score_attempt(questions: list[AssessmentQuestion], answers: dict[int, str]) -> AssessmentResult:
    per_question = []
    correct = 0
    for q in questions:
        given = answers.get(q.id)
        is_correct = given is not None and given.strip().lower() == q.correct_answer.strip().lower()
        if is_correct:
            correct += 1
        per_question.append(
            {
                "question_id": q.id,
                "correct": is_correct,
                "given_answer": given,
                "correct_answer": q.correct_answer,
                "explanation": q.explanation,
            }
        )

    total = len(questions)
    percentage = round(100 * correct / total, 1) if total else 0.0

    if percentage >= 85:
        signal = "STRONG"
    elif percentage >= 65:
        signal = "PRACTICAL"
    elif percentage >= 40:
        signal = "DEVELOPING"
    else:
        signal = "FOUNDATIONAL"

    return AssessmentResult(score=correct, total=total, percentage=percentage, capability_signal=signal, per_question=per_question)


def qualifies_as_evidence(result: AssessmentResult) -> bool:
    """Only a strong, mostly-correct attempt is treated as verified evidence."""
    return result.percentage >= 70
