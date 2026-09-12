from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import AuditEvent, Evidence, Skill, User
from app.models.enums import EvidenceType, VerificationStatus
from app.schemas.schemas import EvidenceCreate, EvidenceOut

router = APIRouter(prefix="/api/evidence", tags=["evidence"])


def _validate_enum(value: str, enum_cls, field_name: str):
    try:
        return enum_cls(value)
    except ValueError:
        valid = ", ".join(e.value for e in enum_cls)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_ENUM_VALUE", "message": f"{field_name} must be one of: {valid}"}},
        )


@router.get("", response_model=list[EvidenceOut])
def list_evidence(
    skill_id: int | None = None,
    limit: int = Query(default=100, le=500),
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Evidence]:
    query = db.query(Evidence).filter(Evidence.user_id == user.id)
    if skill_id is not None:
        query = query.filter(Evidence.skill_id == skill_id)
    return query.order_by(Evidence.date.desc()).offset(offset).limit(limit).all()


@router.post("", response_model=EvidenceOut, status_code=status.HTTP_201_CREATED)
def create_evidence(payload: EvidenceCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Evidence:
    skill = db.query(Skill).filter(Skill.id == payload.skill_id).first()
    if skill is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": {"code": "SKILL_NOT_FOUND", "message": "Skill not found"}})

    ev_type = _validate_enum(payload.type, EvidenceType, "type")
    verification = _validate_enum(payload.verification_status, VerificationStatus, "verification_status")

    if not (1 <= payload.complexity <= 5):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": {"code": "INVALID_COMPLEXITY", "message": "complexity must be between 1 and 5"}})

    evidence = Evidence(
        user_id=user.id,
        skill_id=payload.skill_id,
        type=ev_type,
        title=payload.title,
        description=payload.description,
        date=payload.date,
        source=payload.source,
        verification_status=verification,
        complexity=payload.complexity,
        project_id=payload.project_id,
    )
    db.add(evidence)
    db.flush()
    db.add(AuditEvent(user_id=user.id, action="EVIDENCE_ADDED", entity_type="Evidence", entity_id=evidence.id, new_value={"skill_id": skill.id, "type": ev_type.value}))
    db.commit()
    db.refresh(evidence)
    return evidence
