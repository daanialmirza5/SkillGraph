from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.engines.simulator import HypotheticalEvidence, simulate_role_readiness
from app.models import User
from app.models.enums import EvidenceType, VerificationStatus
from app.schemas.schemas import SimulationRequest, SimulationResultOut

router = APIRouter(prefix="/api/simulations", tags=["simulations"])


@router.post("", response_model=SimulationResultOut)
def run_simulation(payload: SimulationRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> SimulationResultOut:
    hypothetical = []
    for item in payload.hypothetical_evidence:
        try:
            ev_type = EvidenceType(item.evidence_type)
            verification = VerificationStatus(item.verification_status)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": {"code": "INVALID_ENUM_VALUE", "message": "Invalid evidence_type or verification_status"}})
        hypothetical.append(HypotheticalEvidence(skill_id=item.skill_id, type=ev_type, complexity=item.complexity, verification_status=verification))

    result = simulate_role_readiness(db, user.id, payload.role_id, hypothetical)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": {"code": "NOT_FOUND", "message": "Role not found"}})

    return SimulationResultOut(
        role_title=result.role_title, before_readiness=result.before_readiness, after_readiness=result.after_readiness,
        delta=result.delta, newly_covered_skills=result.newly_covered_skills,
    )
