"""Builds the user's evidence graph: claimed skills -> evidence -> capability scores."""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.engines.capability_scoring import CapabilityResult, EvidenceInput, compute_capability
from app.models import Evidence, Skill, UserSkill


@dataclass
class SkillGraphEntry:
    skill: Skill
    claimed: bool
    capability: CapabilityResult
    evidence: list[Evidence] = field(default_factory=list)

    @property
    def has_evidence(self) -> bool:
        return len(self.evidence) > 0

    @property
    def is_evidence_gap(self) -> bool:
        """Claimed but unsupported by evidence — different from not knowing the skill at all."""
        return self.claimed and not self.has_evidence


def build_user_skill_graph(db: Session, user_id: int) -> dict[int, SkillGraphEntry]:
    claimed_rows = db.query(UserSkill).filter(UserSkill.user_id == user_id, UserSkill.claimed.is_(True)).all()
    claimed_skill_ids = {row.skill_id for row in claimed_rows}

    evidence_rows = db.query(Evidence).filter(Evidence.user_id == user_id).all()
    evidence_by_skill: dict[int, list[Evidence]] = {}
    for ev in evidence_rows:
        evidence_by_skill.setdefault(ev.skill_id, []).append(ev)

    all_skill_ids = claimed_skill_ids | set(evidence_by_skill.keys())
    if not all_skill_ids:
        return {}

    skills = {s.id: s for s in db.query(Skill).filter(Skill.id.in_(all_skill_ids)).all()}

    graph: dict[int, SkillGraphEntry] = {}
    for skill_id in all_skill_ids:
        skill = skills.get(skill_id)
        if skill is None:
            continue
        items = evidence_by_skill.get(skill_id, [])
        inputs = [
            EvidenceInput(
                type=ev.type,
                date=ev.date,
                complexity=ev.complexity,
                verification_status=ev.verification_status,
                id=ev.id,
            )
            for ev in items
        ]
        capability = compute_capability(inputs)
        graph[skill_id] = SkillGraphEntry(
            skill=skill,
            claimed=skill_id in claimed_skill_ids,
            capability=capability,
            evidence=items,
        )
    return graph
