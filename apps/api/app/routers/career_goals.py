from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.engines.gap_engine import compute_role_gap
from app.models import AuditEvent, CareerGoal, Role, User
from app.schemas.schemas import CareerGoalCreate, CareerGoalOut

router = APIRouter(prefix="/api/career-goals", tags=["career-goals"])


@router.get("", response_model=list[CareerGoalOut])
def list_goals(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(CareerGoal).filter(CareerGoal.user_id == user.id).order_by(CareerGoal.created_at.desc()).all()


@router.post("", response_model=CareerGoalOut, status_code=status.HTTP_201_CREATED)
def create_goal(payload: CareerGoalCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CareerGoal:
    role = db.query(Role).filter(Role.id == payload.target_role_id).first()
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": {"code": "NOT_FOUND", "message": "Role not found"}})

    db.query(CareerGoal).filter(CareerGoal.user_id == user.id, CareerGoal.active.is_(True)).update({"active": False})

    gap_result = compute_role_gap(db, user.id, payload.target_role_id)
    goal = CareerGoal(
        user_id=user.id, target_role_id=payload.target_role_id, timeline_months=payload.timeline_months,
        active=True, baseline_readiness=gap_result.readiness if gap_result else 0.0,
    )
    db.add(goal)
    db.flush()
    db.add(AuditEvent(user_id=user.id, action="ROLE_SELECTED", entity_type="CareerGoal", entity_id=goal.id, new_value={"target_role_id": role.id, "baseline_readiness": goal.baseline_readiness}))
    db.commit()
    db.refresh(goal)
    return goal
