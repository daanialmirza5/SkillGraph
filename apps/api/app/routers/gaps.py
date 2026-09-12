from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.engines.dependency_engine import get_dependency_chain_for_target
from app.engines.gap_engine import compute_role_gap
from app.models import User
from app.schemas.schemas import SkillOut

router = APIRouter(prefix="/api/skill-gaps", tags=["gaps"])


@router.get("")
def skill_gaps(role_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = compute_role_gap(db, user.id, role_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": {"code": "NOT_FOUND", "message": "Role not found"}})

    def gap_payload(g):
        chain = get_dependency_chain_for_target(db, g.skill.id)
        return {
            "skill": SkillOut.model_validate(g.skill).model_dump(),
            "importance": g.importance.value,
            "match": g.match.value,
            "user_score": g.user_score,
            "is_evidence_gap": g.is_evidence_gap,
            "priority_score": g.priority_score,
            "dependency_chain": [s.name for s in chain],
        }

    critical = [g for g in result.gaps if g.importance.value == "CRITICAL" and g.match.value != "STRONG_MATCH"]
    high = [g for g in result.gaps if g.importance.value == "HIGH" and g.match.value != "STRONG_MATCH"]
    medium = [g for g in result.gaps if g.importance.value in ("MEDIUM", "LOW") and g.match.value != "STRONG_MATCH"]
    evidence_gaps = [g for g in result.gaps if g.is_evidence_gap]

    return {
        "role_title": result.role.title,
        "readiness": result.readiness,
        "critical_gaps": [gap_payload(g) for g in critical],
        "high_priority_gaps": [gap_payload(g) for g in high],
        "medium_priority_gaps": [gap_payload(g) for g in medium],
        "evidence_gaps": [gap_payload(g) for g in evidence_gaps],
    }
