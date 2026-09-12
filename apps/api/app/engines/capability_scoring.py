"""Evidence-based capability scoring engine.

Formula (documented in docs/capability-scoring.md):

  item_score   = base_strength(type) * recency_multiplier(date) *
                 complexity_multiplier(complexity) * verification_multiplier(status)

  raw_total    = sum of item_score, sorted descending, with diminishing-returns
                 weight 1 / (1 + 0.4 * rank) applied per item (repetition matters,
                 but each additional piece of evidence contributes less than the last)

  score        = 100 * (1 - exp(-raw_total / 120))   [0-100, saturating]

  level        = FOUNDATIONAL / DEVELOPING / PRACTICAL / STRONG / EXPERT-LIKE (by score band)
  confidence   = LOW / MEDIUM / HIGH (by evidence count + verification mix)

This is an *evidence-based capability indicator*, not a measurement of true
human expertise and not a hiring probability.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date

from app.models.enums import CapabilityLevel, ConfidenceLevel, EvidenceType, VerificationStatus

BASE_STRENGTH: dict[EvidenceType, float] = {
    EvidenceType.WORK_EXPERIENCE: 70.0,
    EvidenceType.INTERNSHIP: 55.0,
    EvidenceType.PUBLICATION: 60.0,
    EvidenceType.COMPETITION: 50.0,
    EvidenceType.PROJECT: 45.0,
    EvidenceType.GITHUB_REPOSITORY: 35.0,
    EvidenceType.ASSESSMENT: 40.0,
    EvidenceType.CERTIFICATION: 30.0,
    EvidenceType.PORTFOLIO: 25.0,
    EvidenceType.COURSE: 15.0,
}

VERIFICATION_MULTIPLIER: dict[VerificationStatus, float] = {
    VerificationStatus.VERIFIED: 1.2,
    VerificationStatus.SELF_REPORTED: 1.0,
    VerificationStatus.UNVERIFIED: 0.85,
}

SATURATION_CONSTANT = 120.0
DIMINISHING_RETURNS_FACTOR = 0.4

LEVEL_BANDS: list[tuple[int, CapabilityLevel]] = [
    (85, CapabilityLevel.EXPERT_LIKE),
    (65, CapabilityLevel.STRONG),
    (40, CapabilityLevel.PRACTICAL),
    (20, CapabilityLevel.DEVELOPING),
    (0, CapabilityLevel.FOUNDATIONAL),
]


def recency_multiplier(evidence_date: date, as_of: date | None = None) -> float:
    as_of = as_of or date.today()
    months_ago = max(0, (as_of.year - evidence_date.year) * 12 + (as_of.month - evidence_date.month))
    if months_ago <= 6:
        return 1.0
    if months_ago <= 12:
        return 0.9
    if months_ago <= 24:
        return 0.75
    if months_ago <= 36:
        return 0.55
    return 0.35


def complexity_multiplier(complexity: int) -> float:
    complexity = max(1, min(5, complexity))
    return 0.7 + 0.15 * complexity


@dataclass
class EvidenceInput:
    type: EvidenceType
    date: date
    complexity: int
    verification_status: VerificationStatus
    id: int | None = None


@dataclass
class CapabilityResult:
    score: float
    level: CapabilityLevel
    confidence: ConfidenceLevel
    evidence_count: int
    contributions: list[dict] = field(default_factory=list)


def score_evidence_item(item: EvidenceInput, as_of: date | None = None) -> float:
    base = BASE_STRENGTH[item.type]
    rec = recency_multiplier(item.date, as_of)
    cx = complexity_multiplier(item.complexity)
    ver = VERIFICATION_MULTIPLIER[item.verification_status]
    return base * rec * cx * ver


def level_for_score(score: float) -> CapabilityLevel:
    for threshold, level in LEVEL_BANDS:
        if score >= threshold:
            return level
    return CapabilityLevel.FOUNDATIONAL


def confidence_for(items: list[EvidenceInput]) -> ConfidenceLevel:
    if not items:
        return ConfidenceLevel.LOW
    verified_count = sum(1 for i in items if i.verification_status == VerificationStatus.VERIFIED)
    if len(items) >= 3 and verified_count >= 1:
        return ConfidenceLevel.HIGH
    if len(items) >= 2:
        return ConfidenceLevel.MEDIUM
    if len(items) == 1 and verified_count == 1:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.LOW


def compute_capability(items: list[EvidenceInput], as_of: date | None = None) -> CapabilityResult:
    if not items:
        return CapabilityResult(score=0.0, level=CapabilityLevel.FOUNDATIONAL, confidence=ConfidenceLevel.LOW, evidence_count=0)

    scored = sorted(
        ((item, score_evidence_item(item, as_of)) for item in items),
        key=lambda pair: pair[1],
        reverse=True,
    )

    raw_total = 0.0
    contributions = []
    for rank, (item, item_score) in enumerate(scored):
        weight = 1 / (1 + DIMINISHING_RETURNS_FACTOR * rank)
        contribution = item_score * weight
        raw_total += contribution
        contributions.append(
            {
                "evidence_id": item.id,
                "type": item.type.value,
                "item_score": round(item_score, 2),
                "weight": round(weight, 3),
                "contribution": round(contribution, 2),
            }
        )

    score = 100 * (1 - math.exp(-raw_total / SATURATION_CONSTANT))
    score = round(min(100.0, score), 1)

    return CapabilityResult(
        score=score,
        level=level_for_score(score),
        confidence=confidence_for(items),
        evidence_count=len(items),
        contributions=contributions,
    )
