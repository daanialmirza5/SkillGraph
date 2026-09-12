from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.engines.learning_path import generate_learning_path
from app.models import User
from app.schemas.schemas import LearningStepOut

router = APIRouter(prefix="/api/learning-paths", tags=["learning"])


@router.get("", response_model=list[LearningStepOut])
def learning_path(role_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[LearningStepOut]:
    steps = generate_learning_path(db, user.id, role_id)
    return [
        LearningStepOut(
            order=s.order, skill=s.skill, why=s.why, evidence_to_create=s.evidence_to_create,
            resource_titles=[r.title for r in s.resources],
        )
        for s in steps
    ]
