from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.career_analyst import ask_career_analyst
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.schemas.schemas import AIAnswerOut, AIQuestionRequest

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/analyze", response_model=AIAnswerOut)
def analyze(payload: AIQuestionRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AIAnswerOut:
    response = ask_career_analyst(db, user.id, payload.question, role_id=payload.role_id)
    return AIAnswerOut(
        answer=response.answer, evidence_used=response.evidence_used, reasoning_basis=response.reasoning_basis,
        confidence=response.confidence, limitations=response.limitations, provider=response.provider,
    )
