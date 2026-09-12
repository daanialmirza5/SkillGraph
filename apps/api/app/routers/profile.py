from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import AuditEvent, Profile, User
from app.schemas.schemas import ProfileOut, ProfileUpdate

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("", response_model=ProfileOut)
def get_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Profile:
    return user.profile


@router.patch("", response_model=ProfileOut)
def update_profile(payload: ProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Profile:
    profile = user.profile
    previous = {"headline": profile.headline, "target_role_id": profile.target_role_id}
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.add(AuditEvent(
        user_id=user.id, action="PROFILE_UPDATED", entity_type="Profile", entity_id=profile.id,
        previous_value=previous, new_value=payload.model_dump(exclude_unset=True),
    ))
    db.commit()
    db.refresh(profile)
    return profile
