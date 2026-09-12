"""Skill gap engine: compares a user's evidence graph against a role's requirement graph.

Readiness formula (documented in docs/role-matching.md and docs/gap-engine.md):

  weight(importance) = CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1
  coverage(skill)     = min(capability_score / 100, 1.0)
  readiness           = 100 * sum(weight_i * coverage_i) / sum(weight_i)

This is a *weighted capability coverage estimate*, not a probability of
being hired and not a certification of competence.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.engines.graph_service import SkillGraphEntry, build_user_skill_graph
from app.models import Role, RoleSkill, Skill
from app.models.enums import Importance, MatchLevel

IMPORTANCE_WEIGHT: dict[Importance, int] = {
    Importance.CRITICAL: 4,
    Importance.HIGH: 3,
    Importance.MEDIUM: 2,
    Importance.LOW: 1,
}

STRONG_THRESHOLD = 75
PARTIAL_THRESHOLD = 40
WEAK_THRESHOLD = 15


def classify(score: float, has_evidence: bool) -> MatchLevel:
    if not has_evidence or score < WEAK_THRESHOLD:
        return MatchLevel.MISSING
    if score < PARTIAL_THRESHOLD:
        return MatchLevel.WEAK_MATCH
    if score < STRONG_THRESHOLD:
        return MatchLevel.PARTIAL_MATCH
    return MatchLevel.STRONG_MATCH


@dataclass
class RoleSkillGap:
    skill: Skill
    importance: Importance
    min_capability_score: int
    user_score: float
    user_level: str
    match: MatchLevel
    is_evidence_gap: bool
    weight: int

    @property
    def priority_score(self) -> float:
        """Higher = more urgent to close. Combines importance weight with how far the skill is from the bar."""
        coverage = min(self.user_score / 100, 1.0)
        return round(self.weight * (1 - coverage), 3)


@dataclass
class RoleGapResult:
    role: Role
    readiness: float
    gaps: list[RoleSkillGap] = field(default_factory=list)

    @property
    def strong(self) -> list[RoleSkillGap]:
        return [g for g in self.gaps if g.match == MatchLevel.STRONG_MATCH]

    @property
    def partial(self) -> list[RoleSkillGap]:
        return [g for g in self.gaps if g.match == MatchLevel.PARTIAL_MATCH]

    @property
    def weak(self) -> list[RoleSkillGap]:
        return [g for g in self.gaps if g.match == MatchLevel.WEAK_MATCH]

    @property
    def missing(self) -> list[RoleSkillGap]:
        return [g for g in self.gaps if g.match == MatchLevel.MISSING]


def compute_role_gap(db: Session, user_id: int, role_id: int) -> RoleGapResult | None:
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        return None

    role_skills = db.query(RoleSkill).filter(RoleSkill.role_id == role_id).all()
    if not role_skills:
        return RoleGapResult(role=role, readiness=0.0, gaps=[])

    user_graph = build_user_skill_graph(db, user_id)

    gaps: list[RoleSkillGap] = []
    weighted_sum = 0.0
    weight_total = 0.0

    for rs in role_skills:
        entry: SkillGraphEntry | None = user_graph.get(rs.skill_id)
        score = entry.capability.score if entry else 0.0
        level = entry.capability.level.value if entry else "FOUNDATIONAL"
        has_evidence = entry.has_evidence if entry else False
        is_evidence_gap = entry.is_evidence_gap if entry else False

        weight = IMPORTANCE_WEIGHT[rs.importance]
        coverage = min(score / 100, 1.0)
        weighted_sum += weight * coverage
        weight_total += weight

        gaps.append(
            RoleSkillGap(
                skill=rs.skill,
                importance=rs.importance,
                min_capability_score=rs.min_capability_score,
                user_score=score,
                user_level=level,
                match=classify(score, has_evidence),
                is_evidence_gap=is_evidence_gap,
                weight=weight,
            )
        )

    readiness = round(100 * weighted_sum / weight_total, 1) if weight_total else 0.0
    gaps.sort(key=lambda g: -g.priority_score)

    return RoleGapResult(role=role, readiness=readiness, gaps=gaps)


def rank_roles_by_fit(db: Session, user_id: int, role_ids: list[int]) -> list[RoleGapResult]:
    results = [compute_role_gap(db, user_id, rid) for rid in role_ids]
    valid = [r for r in results if r is not None]
    valid.sort(key=lambda r: r.readiness, reverse=True)
    return valid
