"""Specialized analysis functions ("agents") that each turn one slice of the
structured skill/role/evidence graph into a grounded fact set. A single
CareerNarrator pass then turns the combined facts into prose. No agent may
invent a skill, evidence item, or score that isn't present in the underlying
data returned by the engines.
"""

from __future__ import annotations

from app.engines.dependency_engine import get_dependency_chain_for_target
from app.engines.gap_engine import RoleGapResult
from app.engines.graph_service import SkillGraphEntry
from app.engines.recommendation_engine import ProjectRecommendation
from sqlalchemy.orm import Session


def skill_analyst(user_graph: dict[int, SkillGraphEntry]) -> list[str]:
    facts = []
    for entry in sorted(user_graph.values(), key=lambda e: -e.capability.score)[:8]:
        facts.append(
            f"{entry.skill.name}: {entry.capability.level.value} (score {entry.capability.score}/100, "
            f"{entry.capability.evidence_count} evidence item(s), confidence {entry.capability.confidence.value})"
        )
    return facts


def gap_analyst(gap_result: RoleGapResult) -> list[str]:
    facts = []
    for gap in gap_result.gaps[:6]:
        evidence_note = " [claimed but no supporting evidence]" if gap.is_evidence_gap else ""
        facts.append(
            f"{gap.skill.name}: {gap.match.value} — role importance {gap.importance.value}, "
            f"current score {gap.user_score}/100{evidence_note}"
        )
    return facts


def role_analyst(gap_result: RoleGapResult) -> list[str]:
    return [
        f"Target role: {gap_result.role.title} ({gap_result.role.level} level, {gap_result.role.category})",
        f"Weighted capability coverage: {gap_result.readiness}%",
        f"Strong matches: {len(gap_result.strong)}, Partial: {len(gap_result.partial)}, "
        f"Weak: {len(gap_result.weak)}, Missing: {len(gap_result.missing)}",
    ]


def evidence_analyst(user_graph: dict[int, SkillGraphEntry], skill_id: int) -> list[str]:
    entry = user_graph.get(skill_id)
    if entry is None or not entry.evidence:
        return ["No evidence on file for this skill."]
    facts = []
    for ev in entry.evidence:
        facts.append(f"{ev.type.value} — \"{ev.title}\" ({ev.date.isoformat()}, {ev.verification_status.value})")
    return facts


def dependency_analyst(db: Session, skill_id: int) -> list[str]:
    chain = get_dependency_chain_for_target(db, skill_id)
    if len(chain) <= 1:
        return []
    return [" -> ".join(s.name for s in chain)]


def project_advisor(recommendations: list[ProjectRecommendation]) -> list[str]:
    facts = []
    for rec in recommendations:
        facts.append(
            f"Recommended: \"{rec.title}\" — closes {', '.join(rec.closes_gap_skill_names)} "
            f"(expected gap reduction: {rec.expected_gap_reduction})"
        )
    return facts


def career_narrator(question: str, sections: dict[str, list[str]]) -> str:
    lines = [f"Question: {question}", ""]
    for title, facts in sections.items():
        if not facts:
            continue
        lines.append(f"## {title}")
        lines.extend(f"- {fact}" for fact in facts)
        lines.append("")
    return "\n".join(lines)
