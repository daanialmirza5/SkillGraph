from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.engines.assessment_engine import qualifies_as_evidence, score_attempt
from app.models import AssessmentAttempt, AssessmentQuestion, AuditEvent, Evidence, User
from app.models.enums import EvidenceType, VerificationStatus
from app.schemas.schemas import AssessmentQuestionOut, AssessmentResultOut, AssessmentSubmit

router = APIRouter(prefix="/api/assessments", tags=["assessments"])


@router.get("/questions", response_model=list[AssessmentQuestionOut])
def get_questions(skill_id: int, limit: int = Query(default=5, le=20), db: Session = Depends(get_db)):
    return db.query(AssessmentQuestion).filter(AssessmentQuestion.skill_id == skill_id).limit(limit).all()


@router.post("", response_model=AssessmentResultOut, status_code=status.HTTP_201_CREATED)
def submit_assessment(payload: AssessmentSubmit, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AssessmentResultOut:
    questions = db.query(AssessmentQuestion).filter(AssessmentQuestion.id.in_(payload.answers.keys())).all()
    if not questions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": {"code": "NO_QUESTIONS", "message": "No matching questions found for submitted answers"}})

    result = score_attempt(questions, payload.answers)
    becomes_evidence = qualifies_as_evidence(result)

    attempt = AssessmentAttempt(
        user_id=user.id, skill_id=payload.skill_id, score=result.score, total=result.total,
        answers={str(k): v for k, v in payload.answers.items()}, became_evidence=becomes_evidence,
    )
    db.add(attempt)
    db.flush()

    if becomes_evidence:
        db.add(Evidence(
            user_id=user.id, skill_id=payload.skill_id, type=EvidenceType.ASSESSMENT,
            title=f"Verified assessment ({result.percentage}%)", date=date.today(),
            verification_status=VerificationStatus.VERIFIED, complexity=3,
        ))

    db.add(AuditEvent(user_id=user.id, action="ASSESSMENT_COMPLETED", entity_type="AssessmentAttempt", entity_id=attempt.id, new_value={"score": result.score, "total": result.total}))
    db.commit()

    return AssessmentResultOut(
        score=result.score, total=result.total, percentage=result.percentage, capability_signal=result.capability_signal,
        became_evidence=becomes_evidence, per_question=result.per_question,
    )
