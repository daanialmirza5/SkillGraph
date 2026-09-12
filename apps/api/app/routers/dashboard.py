from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.engines.gap_engine import compute_role_gap
from app.engines.graph_service import build_user_skill_graph
from app.engines.recommendation_engine import recommend_project_for_role
from app.models import CareerGoal, Evidence, Project, User

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    graph = build_user_skill_graph(db, user.id)
    strong = [e for e in graph.values() if e.capability.level.value in ("STRONG", "EXPERT-LIKE")]
    evidence_gaps = [e for e in graph.values() if e.is_evidence_gap]

    active_goal = db.query(CareerGoal).filter(CareerGoal.user_id == user.id, CareerGoal.active.is_(True)).first()

    readiness = None
    next_action = None
    if active_goal is not None:
        gap_result = compute_role_gap(db, user.id, active_goal.target_role_id)
        if gap_result is not None:
            readiness = gap_result.readiness
            recs = recommend_project_for_role(db, user.id, active_goal.target_role_id, top_n=1)
            if recs:
                next_action = {"title": recs[0].title, "reason": recs[0].reason}

    return {
        "evidence_coverage_skill_count": len(graph),
        "strong_skill_count": len(strong),
        "evidence_gap_count": len(evidence_gaps),
        "project_count": db.query(Project).filter(Project.user_id == user.id).count(),
        "evidence_count": db.query(Evidence).filter(Evidence.user_id == user.id).count(),
        "active_goal_role_id": active_goal.target_role_id if active_goal else None,
        "target_role_readiness": readiness,
        "next_best_action": next_action,
        "disclaimer": (
            "SkillGraph uses synthetic demonstration profiles, roles, skills, and evidence. "
            "Readiness scores and capability indicators are analytical estimates, not hiring "
            "decisions, professional certifications, or guarantees of employment."
        ),
    }
