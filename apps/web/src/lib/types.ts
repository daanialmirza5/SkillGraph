export interface Skill {
  id: number;
  name: string;
  category_id: number;
  description?: string | null;
  aliases: string[];
  parent_skill_id?: number | null;
}

export interface SkillCategory {
  id: number;
  name: string;
}

export interface UserSkillCapability {
  skill: Skill;
  claimed: boolean;
  score: number;
  level: string;
  confidence: string;
  evidence_count: number;
  is_evidence_gap: boolean;
}

export interface Role {
  id: number;
  title: string;
  category: string;
  description?: string | null;
  level: string;
}

export interface RoleSkillOut {
  skill: Skill;
  importance: string;
  min_capability_score: number;
}

export interface RoleDetail extends Role {
  required_skills: RoleSkillOut[];
}

export interface GapSkill {
  skill: Skill;
  importance: string;
  user_score: number;
  user_level: string;
  match: string;
  is_evidence_gap: boolean;
  priority_score: number;
}

export interface RoleGap {
  role: Role;
  readiness: number;
  strong: GapSkill[];
  partial: GapSkill[];
  weak: GapSkill[];
  missing: GapSkill[];
}

export interface RoleFitSummary {
  role: Role;
  readiness: number;
}

export interface DashboardData {
  evidence_coverage_skill_count: number;
  strong_skill_count: number;
  evidence_gap_count: number;
  project_count: number;
  evidence_count: number;
  active_goal_role_id: number | null;
  target_role_readiness: number | null;
  next_best_action: { title: string; reason: string } | null;
  disclaimer: string;
}

export interface Project {
  id: number;
  name: string;
  description: string;
  role_title?: string | null;
  duration_months: number;
  technologies: string[];
  complexity: number;
  is_production: boolean;
  repository_url?: string | null;
  demo_url?: string | null;
  created_at: string;
}

export interface Evidence {
  id: number;
  skill_id: number;
  type: string;
  title: string;
  description?: string | null;
  date: string;
  source?: string | null;
  verification_status: string;
  complexity: number;
  project_id?: number | null;
}

export interface LearningStep {
  order: number;
  skill: Skill;
  why: string;
  evidence_to_create: string;
  resource_titles: string[];
}

export interface ProjectRecommendation {
  title: string;
  description: string;
  target_skill_names: string[];
  closes_gap_skill_names: string[];
  reason: string;
  expected_gap_reduction: string;
}

export interface Recommendation {
  id: number;
  type: string;
  title: string;
  description: string;
  reason: string;
  target_skills: string[];
  target_role_id?: number | null;
  expected_gap_reduction: string;
  status: string;
  created_at: string;
}

export interface AssessmentQuestion {
  id: number;
  skill_id: number;
  difficulty: string;
  question_type: string;
  question: string;
  options: string[];
}

export interface AssessmentResult {
  score: number;
  total: number;
  percentage: number;
  capability_signal: string;
  became_evidence: boolean;
  per_question: Array<{ question_id: number; correct: boolean; given_answer: string | null; correct_answer: string; explanation: string | null }>;
}

export interface SimulationResult {
  role_title: string;
  before_readiness: number;
  after_readiness: number;
  delta: number;
  newly_covered_skills: string[];
}

export interface AIAnswer {
  answer: string;
  evidence_used: string[];
  reasoning_basis: string[];
  confidence: string;
  limitations: string[];
  provider: string;
}

export interface AuditEvent {
  id: number;
  action: string;
  entity_type: string;
  entity_id?: number | null;
  created_at: string;
}

export interface PortfolioData {
  strong: { skill: string; score: number }[];
  moderate: { skill: string; score: number }[];
  weak: { skill: string; score: number }[];
  what_your_portfolio_does_not_prove: { skill: string; note: string }[];
  categories_covered: string[];
}

export interface CareerGoal {
  id: number;
  target_role_id: number;
  timeline_months: number;
  active: boolean;
  baseline_readiness: number | null;
  created_at: string;
}

export interface GraphData {
  nodes: Array<{ id: string; type: string; label: string; category?: string; score?: number; level?: string }>;
  edges: Array<{ source: string; target: string; type: string }>;
}
