"""Career what-if simulator: recomputes role readiness with hypothetical evidence
added in-memory only. Never writes to the database.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from sqlalchemy.orm import Session

from app.engines.capability_scoring import EvidenceInput, compute_capability
from app.engines.gap_engine import IMPORTANCE_WEIGHT, RoleGapResult, classify, compute_role_gap
from app.engines.graph_service import build_user_skill_graph
from app.models import Role, RoleSkill
from app.models.enums import EvidenceType, VerificationStatus


@dataclass
class HypotheticalEvidence:
    skill_id: int
    type: EvidenceType = EvidenceType.PROJECT
    complexity: int = 4
    verification_status: VerificationStatus = VerificationStatus.SELF_REPORTED
    evidence_date: date = field(default_factory=date.today)


@dataclass
class SimulationResult:
    role_title: str
    before_readiness: float
    after_readiness: float
    delta: float
    newly_covered_skills: list[str]


def simulate_role_readiness(
    db: Session, user_id: int, role_id: int, hypothetical: list[HypotheticalEvidence]
) -> SimulationResult | None:
    before: RoleGapResult | None = compute_role_gap(db, user_id, role_id)
    if before is None:
        return None

    role = db.query(Role).filter(Role.id == role_id).first()
    role_skills = db.query(RoleSkill).filter(RoleSkill.role_id == role_id).all()
    if not role_skills:
        return SimulationResult(role_title=role.title, before_readiness=0.0, after_readiness=0.0, delta=0.0, newly_covered_skills=[])

    user_graph = build_user_skill_graph(db, user_id)

    hypothetical_by_skill: dict[int, list[HypotheticalEvidence]] = {}
    for h in hypothetical:
        hypothetical_by_skill.setdefault(h.skill_id, []).append(h)

    weighted_sum = 0.0
    weight_total = 0.0
    newly_covered = []

    for rs in role_skills:
        existing_entry = user_graph.get(rs.skill_id)
        existing_items = [
            EvidenceInput(type=ev.type, date=ev.date, complexity=ev.complexity, verification_status=ev.verification_status, id=ev.id)
            for ev in (existing_entry.evidence if existing_entry else [])
        ]
        new_items = [
            EvidenceInput(type=h.type, date=h.evidence_date, complexity=h.complexity, verification_status=h.verification_status)
            for h in hypothetical_by_skill.get(rs.skill_id, [])
        ]
        combined = existing_items + new_items
        capability = compute_capability(combined)

        weight = IMPORTANCE_WEIGHT[rs.importance]
        coverage = min(capability.score / 100, 1.0)
        weighted_sum += weight * coverage
        weight_total += weight

        before_match = existing_entry.capability.score if existing_entry else 0.0
        if new_items and classify(capability.score, True) in ("STRONG_MATCH", "PARTIAL_MATCH") and before_match < 40:
            newly_covered.append(rs.skill.name)

    after_readiness = round(100 * weighted_sum / weight_total, 1) if weight_total else 0.0

    return SimulationResult(
        role_title=role.title,
        before_readiness=before.readiness,
        after_readiness=after_readiness,
        delta=round(after_readiness - before.readiness, 1),
        newly_covered_skills=newly_covered,
    )
