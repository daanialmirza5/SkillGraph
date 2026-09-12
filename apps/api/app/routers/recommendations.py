from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.engines.recommendation_engine import recommend_project_for_role
from app.models import AuditEvent, Recommendation, User
from app.schemas.schemas import ProjectRecommendationOut, RecommendationDecision, RecommendationOut

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("/preview", response_model=list[ProjectRecommendationOut])
def preview_recommendations(role_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    recs = recommend_project_for_role(db, user.id, role_id, top_n=3)
    return [
        ProjectRecommendationOut(
            title=r.title, description=r.description, target_skill_names=r.target_skill_names,
            closes_gap_skill_names=r.closes_gap_skill_names, reason=r.reason, expected_gap_reduction=r.expected_gap_reduction,
        )
        for r in recs
    ]


@router.post("/generate", response_model=RecommendationOut, status_code=status.HTTP_201_CREATED)
def generate_and_save(role_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Recommendation:
    recs = recommend_project_for_role(db, user.id, role_id, top_n=1)
    if not recs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": {"code": "NO_GAP", "message": "No open gaps found for this role — nothing to recommend."}})
    r = recs[0]
    rec = Recommendation(
        user_id=user.id, type="PROJECT", title=r.title, description=r.description, reason=r.reason,
        target_skills=r.target_skill_names, target_role_id=role_id, expected_gap_reduction=r.expected_gap_reduction,
        status="SUGGESTED",
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


@router.get("", response_model=list[RecommendationOut])
def list_recommendations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Recommendation).filter(Recommendation.user_id == user.id).order_by(Recommendation.created_at.desc()).all()


@router.post("/{recommendation_id}/decision", response_model=RecommendationOut)
def decide_recommendation(recommendation_id: int, payload: RecommendationDecision, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Recommendation:
    rec = db.query(Recommendation).filter(Recommendation.id == recommendation_id, Recommendation.user_id == user.id).first()
    if rec is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": {"code": "NOT_FOUND", "message": "Recommendation not found"}})
    if payload.status not in ("ACCEPTED", "EDITED", "REJECTED"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": {"code": "INVALID_STATUS", "message": "status must be ACCEPTED, EDITED, or REJECTED"}})

    previous_status = rec.status
    rec.status = payload.status
    rec.decided_at = datetime.now(timezone.utc)
    action = "RECOMMENDATION_ACCEPTED" if payload.status == "ACCEPTED" else "RECOMMENDATION_REJECTED"
    db.add(AuditEvent(user_id=user.id, action=action, entity_type="Recommendation", entity_id=rec.id, previous_value={"status": previous_status}, new_value={"status": payload.status}))
    db.commit()
    db.refresh(rec)
    return rec
