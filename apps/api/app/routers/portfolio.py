from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.engines.graph_service import build_user_skill_graph
from app.models import User

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.get("")
def portfolio(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    graph = build_user_skill_graph(db, user.id)

    strong = sorted([e for e in graph.values() if e.capability.score >= 65], key=lambda e: -e.capability.score)
    moderate = sorted([e for e in graph.values() if 35 <= e.capability.score < 65], key=lambda e: -e.capability.score)
    weak = sorted([e for e in graph.values() if e.capability.score < 35], key=lambda e: -e.capability.score)

    claimed_no_evidence = [
        {"skill": e.skill.name, "note": f"You claim {e.skill.name}, but your current evidence graph contains no supporting evidence."}
        for e in graph.values() if e.is_evidence_gap
    ]

    categories_covered = {e.skill.category.name for e in graph.values() if e.capability.score >= 40}

    return {
        "strong": [{"skill": e.skill.name, "score": e.capability.score} for e in strong],
        "moderate": [{"skill": e.skill.name, "score": e.capability.score} for e in moderate],
        "weak": [{"skill": e.skill.name, "score": e.capability.score} for e in weak],
        "what_your_portfolio_does_not_prove": claimed_no_evidence,
        "categories_covered": sorted(categories_covered),
    }
