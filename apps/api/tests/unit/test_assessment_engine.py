from app.engines.assessment_engine import qualifies_as_evidence, score_attempt
from app.models import AssessmentQuestion


def make_question(session, skill_id, correct="A"):
    q = AssessmentQuestion(skill_id=skill_id, difficulty="Beginner", question="2+2?", options=["A", "B"], correct_answer=correct, explanation="Because math.")
    session.add(q)
    session.commit()
    return q


def test_perfect_score_yields_strong_signal(db_session, sample_skills):
    questions = [make_question(db_session, sample_skills["python"].id) for _ in range(4)]
    answers = {q.id: q.correct_answer for q in questions}
    result = score_attempt(questions, answers)
    assert result.score == 4
    assert result.percentage == 100.0
    assert result.capability_signal == "STRONG"
    assert qualifies_as_evidence(result) is True


def test_all_wrong_yields_foundational_and_no_evidence(db_session, sample_skills):
    questions = [make_question(db_session, sample_skills["python"].id) for _ in range(4)]
    answers = {q.id: "wrong-answer" for q in questions}
    result = score_attempt(questions, answers)
    assert result.score == 0
    assert result.capability_signal == "FOUNDATIONAL"
    assert qualifies_as_evidence(result) is False


def test_missing_answer_counts_as_incorrect(db_session, sample_skills):
    questions = [make_question(db_session, sample_skills["python"].id)]
    result = score_attempt(questions, {})
    assert result.score == 0
    assert result.per_question[0]["correct"] is False
