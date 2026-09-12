from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.engines.gap_engine import compute_role_gap, rank_roles_by_fit
from app.models import Role, RoleSkill, User
from app.schemas.schemas import (
    GapSkillOut,
    RoleDetailOut,
    RoleFitSummary,
    RoleGapOut,
    RoleOut,
    RoleSkillOut,
)

router = APIRouter(prefix="/api/roles", tags=["roles"])


@router.get("", response_model=list[RoleOut])
def list_roles(
    category: str | None = None,
    q: str | None = Query(default=None),
    limit: int = Query(default=100, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
) -> list[Role]:
    query = db.query(Role)
    if category:
        query = query.filter(Role.category == category)
    if q:
        query = query.filter(Role.title.ilike(f"%{q}%"))
    return query.order_by(Role.title).offset(offset).limit(limit).all()


@router.get("/best-fit", response_model=list[RoleFitSummary])
def best_fit(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[RoleFitSummary]:
    all_role_ids = [r.id for r in db.query(Role.id).all()]
    ranked = rank_roles_by_fit(db, user.id, all_role_ids)
    return [RoleFitSummary(role=r.role, readiness=r.readiness) for r in ranked[:10]]


@router.get("/compare")
def compare_roles(ids: str = Query(..., description="Comma-separated role IDs"), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    role_ids = [int(x) for x in ids.split(",") if x.strip()]
    results = [compute_role_gap(db, user.id, rid) for rid in role_ids]
    results = [r for r in results if r is not None]

    skill_names = sorted({g.skill.name for r in results for g in r.gaps})
    matrix = []
    for name in skill_names:
        row = {"skill": name}
        for r in results:
            gap = next((g for g in r.gaps if g.skill.name == name), None)
            row[r.role.title] = gap.importance.value if gap else "-"
        matrix.append(row)

    return {
        "roles": [{"id": r.role.id, "title": r.role.title, "readiness": r.readiness} for r in results],
        "importance_matrix": matrix,
    }


@router.get("/{role_id}", response_model=RoleDetailOut)
def get_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": {"code": "NOT_FOUND", "message": "Role not found"}})
    role_skills = db.query(RoleSkill).filter(RoleSkill.role_id == role_id).all()
    return RoleDetailOut(
        id=role.id, title=role.title, category=role.category, description=role.description, level=role.level,
        required_skills=[RoleSkillOut(skill=rs.skill, importance=rs.importance.value, min_capability_score=rs.min_capability_score) for rs in role_skills],
    )


@router.get("/{role_id}/fit", response_model=RoleGapOut)
def role_fit(role_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> RoleGapOut:
    result = compute_role_gap(db, user.id, role_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": {"code": "NOT_FOUND", "message": "Role not found"}})

    def to_out(g):
        return GapSkillOut(
            skill=g.skill, importance=g.importance.value, user_score=g.user_score, user_level=g.user_level,
            match=g.match.value, is_evidence_gap=g.is_evidence_gap, priority_score=g.priority_score,
        )

    return RoleGapOut(
        role=result.role, readiness=result.readiness,
        strong=[to_out(g) for g in result.strong], partial=[to_out(g) for g in result.partial],
        weak=[to_out(g) for g in result.weak], missing=[to_out(g) for g in result.missing],
    )
