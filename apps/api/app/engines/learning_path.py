"""Generates a deterministic, dependency-ordered learning path toward a target role."""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.engines.dependency_engine import get_dependency_chain_for_target
from app.engines.gap_engine import RoleGapResult, compute_role_gap
from app.models import LearningResource, Skill
from app.models.enums import MatchLevel


@dataclass
class LearningStep:
    order: int
    skill: Skill
    why: str
    evidence_to_create: str
    resources: list[LearningResource] = field(default_factory=list)


def generate_learning_path(db: Session, user_id: int, role_id: int, max_gaps: int = 3) -> list[LearningStep]:
    gap_result: RoleGapResult | None = compute_role_gap(db, user_id, role_id)
    if gap_result is None:
        return []

    target_gaps = [g for g in gap_result.gaps if g.match in (MatchLevel.MISSING, MatchLevel.WEAK_MATCH)]
    target_gaps.sort(key=lambda g: -g.priority_score)
    target_gaps = target_gaps[:max_gaps]

    ordered_skill_ids: list[int] = []
    for gap in target_gaps:
        chain = get_dependency_chain_for_target(db, gap.skill.id)
        for skill in chain:
            if skill.id not in ordered_skill_ids:
                ordered_skill_ids.append(skill.id)

    steps: list[LearningStep] = []
    for i, skill_id in enumerate(ordered_skill_ids, start=1):
        skill = db.get(Skill, skill_id)
        if skill is None:
            continue
        resources = db.query(LearningResource).filter(LearningResource.skill_id == skill_id).all()
        matching_gap = next((g for g in target_gaps if g.skill.id == skill_id), None)
        why = (
            f"Required for {gap_result.role.title} ({matching_gap.importance.value} priority) "
            f"and currently classified as {matching_gap.match.value}."
            if matching_gap
            else f"Prerequisite for a skill required by {gap_result.role.title}."
        )
        steps.append(
            LearningStep(
                order=i,
                skill=skill,
                why=why,
                evidence_to_create=f"A project or verified assessment demonstrating {skill.name} to raise it beyond FOUNDATIONAL.",
                resources=resources,
            )
        )

    return steps
