"""Dependency-aware gap analysis: walks PREREQUISITE_OF edges in the skill graph.

Rather than reporting "Missing MLOps", this resolves the prerequisite chain so
the platform can explain *why* and *in what order* to close the gap.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import Skill, SkillRelationship
from app.models.enums import RelationshipType


@dataclass
class DependencyStep:
    skill: Skill
    depth: int


def get_prerequisites(db: Session, skill_id: int, _visited: set[int] | None = None, _depth: int = 0) -> list[DependencyStep]:
    """Returns prerequisite skills for `skill_id`, ordered furthest-first (build order)."""
    visited = _visited if _visited is not None else set()
    if skill_id in visited:
        return []
    visited.add(skill_id)

    rels = (
        db.query(SkillRelationship)
        .filter(
            SkillRelationship.to_skill_id == skill_id,
            SkillRelationship.relationship_type == RelationshipType.PREREQUISITE_OF,
        )
        .all()
    )

    chain: list[DependencyStep] = []
    for rel in rels:
        prereq_skill = rel.from_skill
        upstream = get_prerequisites(db, prereq_skill.id, visited, _depth + 1)
        chain.extend(upstream)
        if not any(step.skill.id == prereq_skill.id for step in chain):
            chain.append(DependencyStep(skill=prereq_skill, depth=_depth + 1))

    return chain


def get_dependency_chain_for_target(db: Session, target_skill_id: int) -> list[Skill]:
    """Ordered build path (prerequisites first) ending at the target skill."""
    prereqs = get_prerequisites(db, target_skill_id)
    prereqs_sorted = sorted(prereqs, key=lambda s: -s.depth)
    target = db.get(Skill, target_skill_id)
    ordered = [step.skill for step in prereqs_sorted]
    if target is not None:
        ordered.append(target)
    return ordered
