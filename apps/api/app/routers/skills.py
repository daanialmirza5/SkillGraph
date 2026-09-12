from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.engines.graph_service import build_user_skill_graph
from app.models import Skill, SkillCategory, User
from app.schemas.schemas import SkillCategoryOut, SkillOut, UserSkillCapabilityOut

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("/categories", response_model=list[SkillCategoryOut])
def list_categories(db: Session = Depends(get_db)) -> list[SkillCategory]:
    return db.query(SkillCategory).order_by(SkillCategory.name).all()


@router.get("", response_model=list[SkillOut])
def list_skills(
    category_id: int | None = None,
    q: str | None = Query(default=None, description="Search by name"),
    limit: int = Query(default=200, le=500),
    offset: int = 0,
    db: Session = Depends(get_db),
) -> list[Skill]:
    query = db.query(Skill)
    if category_id is not None:
        query = query.filter(Skill.category_id == category_id)
    if q:
        query = query.filter(Skill.name.ilike(f"%{q}%"))
    return query.order_by(Skill.name).offset(offset).limit(limit).all()


@router.get("/me/graph", response_model=list[UserSkillCapabilityOut])
def my_skill_graph(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[UserSkillCapabilityOut]:
    graph = build_user_skill_graph(db, user.id)
    return [
        UserSkillCapabilityOut(
            skill=entry.skill,
            claimed=entry.claimed,
            score=entry.capability.score,
            level=entry.capability.level.value,
            confidence=entry.capability.confidence.value,
            evidence_count=entry.capability.evidence_count,
            is_evidence_gap=entry.is_evidence_gap,
        )
        for entry in sorted(graph.values(), key=lambda e: -e.capability.score)
    ]


@router.get("/{skill_id}", response_model=SkillOut)
def get_skill(skill_id: int, db: Session = Depends(get_db)) -> Skill:
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if skill is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": {"code": "NOT_FOUND", "message": "Skill not found"}})
    return skill
