from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    role: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    name: str
    role: str


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    headline: str | None = None
    bio: str | None = None
    persona: str | None = None
    target_role_id: int | None = None
    target_level: str | None = None
    target_timeline_months: int | None = None


class ProfileUpdate(BaseModel):
    headline: str | None = None
    bio: str | None = None
    target_role_id: int | None = None
    target_level: str | None = None
    target_timeline_months: int | None = None


class SkillCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class SkillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    category_id: int
    description: str | None = None
    aliases: list[str] = Field(default_factory=list)
    parent_skill_id: int | None = None


class UserSkillCapabilityOut(BaseModel):
    skill: SkillOut
    claimed: bool
    score: float
    level: str
    confidence: str
    evidence_count: int
    is_evidence_gap: bool


class EvidenceCreate(BaseModel):
    skill_id: int
    type: str
    title: str
    description: str | None = None
    date: date
    source: str | None = None
    verification_status: str = "SELF_REPORTED"
    complexity: int = 3
    project_id: int | None = None


class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    skill_id: int
    type: str
    title: str
    description: str | None = None
    date: date
    source: str | None = None
    verification_status: str
    complexity: int
    project_id: int | None = None


class ProjectCreate(BaseModel):
    name: str
    description: str
    role_title: str | None = None
    duration_months: int = 1
    technologies: list[str] = Field(default_factory=list)
    responsibilities: str | None = None
    outcomes: str | None = None
    repository_url: str | None = None
    demo_url: str | None = None
    complexity: int = 3
    is_production: bool = False
    started_on: date | None = None
    completed_on: date | None = None
    skill_ids: list[int] = Field(default_factory=list)


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    role_title: str | None = None
    duration_months: int
    technologies: list[str]
    complexity: int
    is_production: bool
    repository_url: str | None = None
    demo_url: str | None = None
    created_at: datetime


class RoleSkillOut(BaseModel):
    skill: SkillOut
    importance: str
    min_capability_score: int


class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    category: str
    description: str | None = None
    level: str


class RoleDetailOut(RoleOut):
    required_skills: list[RoleSkillOut]


class GapSkillOut(BaseModel):
    skill: SkillOut
    importance: str
    user_score: float
    user_level: str
    match: str
    is_evidence_gap: bool
    priority_score: float


class RoleGapOut(BaseModel):
    role: RoleOut
    readiness: float
    strong: list[GapSkillOut]
    partial: list[GapSkillOut]
    weak: list[GapSkillOut]
    missing: list[GapSkillOut]


class RoleFitSummary(BaseModel):
    role: RoleOut
    readiness: float


class LearningStepOut(BaseModel):
    order: int
    skill: SkillOut
    why: str
    evidence_to_create: str
    resource_titles: list[str]


class ProjectRecommendationOut(BaseModel):
    title: str
    description: str
    target_skill_names: list[str]
    closes_gap_skill_names: list[str]
    reason: str
    expected_gap_reduction: str


class AssessmentQuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    skill_id: int
    difficulty: str
    question_type: str
    question: str
    options: list[str]


class AssessmentSubmit(BaseModel):
    skill_id: int
    answers: dict[int, str]


class AssessmentResultOut(BaseModel):
    score: int
    total: int
    percentage: float
    capability_signal: str
    became_evidence: bool
    per_question: list[dict]


class CareerGoalCreate(BaseModel):
    target_role_id: int
    timeline_months: int = 6


class CareerGoalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    target_role_id: int
    timeline_months: int
    active: bool
    baseline_readiness: float | None = None
    created_at: datetime


class RecommendationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    type: str
    title: str
    description: str
    reason: str
    target_skills: list[str]
    target_role_id: int | None = None
    expected_gap_reduction: str
    status: str
    created_at: datetime


class RecommendationDecision(BaseModel):
    status: str  # ACCEPTED | EDITED | REJECTED


class SimulationRequestItem(BaseModel):
    skill_id: int
    evidence_type: str = "PROJECT"
    complexity: int = 4
    verification_status: str = "SELF_REPORTED"


class SimulationRequest(BaseModel):
    role_id: int
    hypothetical_evidence: list[SimulationRequestItem]


class SimulationResultOut(BaseModel):
    role_title: str
    before_readiness: float
    after_readiness: float
    delta: float
    newly_covered_skills: list[str]


class AIQuestionRequest(BaseModel):
    question: str
    role_id: int | None = None


class AIAnswerOut(BaseModel):
    answer: str
    evidence_used: list[str]
    reasoning_basis: list[str]
    confidence: str
    limitations: list[str]
    provider: str


class AuditEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    action: str
    entity_type: str
    entity_id: int | None = None
    created_at: datetime


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
