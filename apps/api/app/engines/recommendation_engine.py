"""Evidence-first project recommendations.

Rather than recommending only courses, this engine picks a curated project
template that closes the largest amount of weighted gap for a target role,
and explains exactly which gaps it closes and why.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.data.project_templates import PROJECT_TEMPLATES
from app.engines.gap_engine import RoleGapResult, compute_role_gap
from app.models.enums import MatchLevel


@dataclass
class ProjectRecommendation:
    title: str
    description: str
    target_skill_names: list[str]
    closes_gap_skill_names: list[str]
    reason: str
    expected_gap_reduction: str  # LOW / MEDIUM / HIGH
    supports_role_titles: list[str]


def _expected_reduction_label(closed_weight: float, total_weight: float) -> str:
    if total_weight == 0:
        return "LOW"
    ratio = closed_weight / total_weight
    if ratio >= 0.25:
        return "HIGH"
    if ratio >= 0.1:
        return "MEDIUM"
    return "LOW"


def recommend_project_for_role(db: Session, user_id: int, role_id: int, top_n: int = 1) -> list[ProjectRecommendation]:
    gap_result: RoleGapResult | None = compute_role_gap(db, user_id, role_id)
    if gap_result is None:
        return []

    open_gaps = {g.skill.name: g for g in gap_result.gaps if g.match in (MatchLevel.MISSING, MatchLevel.WEAK_MATCH, MatchLevel.PARTIAL_MATCH)}
    if not open_gaps:
        return []

    total_weight = sum(g.weight for g in gap_result.gaps)

    scored_templates = []
    for template in PROJECT_TEMPLATES:
        overlap = [name for name in template["skills"] if name in open_gaps]
        if not overlap:
            continue
        closed_weight = sum(open_gaps[name].weight for name in overlap)
        scored_templates.append((closed_weight, overlap, template))

    scored_templates.sort(key=lambda t: -t[0])
    top = scored_templates[:top_n]

    recommendations: list[ProjectRecommendation] = []
    for closed_weight, overlap, template in top:
        priority_names = sorted(overlap, key=lambda n: -open_gaps[n].priority_score)
        reason_parts = [
            f"{name} ({open_gaps[name].importance.value}, currently {open_gaps[name].match.value})"
            for name in priority_names
        ]
        reason = (
            f"Your current evidence graph is missing or weak in {len(overlap)} skill(s) required for "
            f"{gap_result.role.title}: {', '.join(reason_parts)}. This project produces direct evidence for all of them."
        )
        recommendations.append(
            ProjectRecommendation(
                title=template["title"],
                description=template["description"],
                target_skill_names=template["skills"],
                closes_gap_skill_names=overlap,
                reason=reason,
                expected_gap_reduction=_expected_reduction_label(closed_weight, total_weight),
                supports_role_titles=[gap_result.role.title],
            )
        )
    return recommendations
