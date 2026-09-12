# SkillGraph

### Turn what you can prove into what you can become.

An evidence-based skills intelligence and career gap analysis platform. It
models a real graph — claimed skills → evidence → capability → target role →
gaps → recommendations — instead of matching resume keywords.

> SkillGraph uses synthetic demonstration profiles, roles, skills, and
> evidence. Readiness scores and capability indicators are analytical
> estimates, not hiring decisions, professional certifications, or
> guarantees of employment.

---

## The problem

People can usually list what they've *studied*. They struggle to answer:

- "What can I actually **prove**?"
- "What exactly am I missing for the role I want, and in what order should I
  close it?"

Resumes reduce experience to keywords. SkillGraph instead distinguishes:

| | Meaning |
|---|---|
| **Claimed** | You say you have this skill. |
| **Evidenced** | You have at least one project, job, certification, or assessment backing it. |
| **Demonstrated** | That evidence, scored for recency/complexity/verification, is strong. |
| **Target** | A skill your chosen role requires. |

## Why SkillGraph is different

It is not a resume builder, a chatbot, a job board, or a keyword matcher.
Every number it shows traces back to a real row in the database:

- **Evidence vs. claims** — you can claim "Kubernetes" and have zero evidence
  for it; SkillGraph calls that an *evidence gap*, distinct from not knowing
  the skill at all.
- **Dependency-aware gaps** — "Missing MLOps" becomes
  `Docker → CI/CD → Model Deployment → Model Monitoring → MLOps`.
- **Evidence-first recommendations** — the platform recommends a specific
  project from a curated catalog, and shows exactly which of your gaps it
  closes and why, instead of a generic course list.
- **Grounded AI** — the AI analyst is only allowed to narrate what the
  deterministic engines already computed. It cannot invent a project, a
  score, or a role requirement, and it cannot mutate your data.

## Evidence-Based Skill Intelligence

For every skill you claim or have evidence for, SkillGraph computes a
0–100 capability score from a documented, deterministic formula (evidence
type strength × recency decay × complexity × verification, combined with
diminishing returns across repeated evidence, saturating smoothly at 100).
Full formula: [`docs/capability-scoring.md`](docs/capability-scoring.md).

## Skill Graph

156 skills across 16 categories, connected by `PREREQUISITE_OF`, `USED_WITH`,
`RELATED_TO`, and `SUBSKILL_OF` relationships — a real graph, explorable
interactively (React Flow) at `/skill-graph`.
Details: [`docs/skill-taxonomy.md`](docs/skill-taxonomy.md).

## Role Graph

41 synthetic roles across 9 categories (Software Engineering, AI/ML, Data,
Cloud, DevOps, Cybersecurity, Product, Analytics, Research), each with
weighted (`CRITICAL`/`HIGH`/`MEDIUM`/`LOW`) required skills.
Details: [`docs/role-matching.md`](docs/role-matching.md).

## Gap Engine

Compares your evidence graph against a role's requirement graph and produces
a weighted readiness score, a per-skill match classification
(`STRONG_MATCH`/`PARTIAL_MATCH`/`WEAK_MATCH`/`MISSING`), and a prioritized,
dependency-aware gap list. Details: [`docs/gap-engine.md`](docs/gap-engine.md),
[`docs/dependency-engine.md`](docs/dependency-engine.md).

## Evidence vs Claims

The Portfolio page (`/portfolio`) surfaces "what your portfolio does not
prove" — skills you claim with zero supporting evidence — as a first-class,
distinct signal from a plain skill gap.

## Career Simulator

`/career-simulator` lets you add hypothetical evidence and see the projected
readiness shift for a role, entirely in memory — nothing is written to your
real profile unless you separately add real evidence.

## Learning Path

A deterministic, dependency-ordered path from your current gaps to a target
role, each step naming *why* it's included and *what evidence to create*
next. Details: [`docs/recommendation-engine.md`](docs/recommendation-engine.md).

## Project Recommendations

"What should I build next?" — the recommendation engine scores a curated
catalog of 24 project templates against your open gaps and returns the one
that closes the most weighted gap, with an explicit list of which skills it
closes.

## AI Career Analyst

A multi-provider (Anthropic / OpenAI / Google / **Mock, default, no API key
required**) analyst that retrieves your skill graph, role graph, evidence,
and gap results, assembles them via specialized analyst functions (Skill,
Gap, Role, Evidence, Dependency, Project Advisor, Career Narrator), and asks
an LLM to narrate — never to invent. Every answer ships with an evidence
panel, a confidence label, and explicit limitations. Prompt-injection
defenses treat all free-text user content as untrusted data.
Full design: [`docs/ai-architecture.md`](docs/ai-architecture.md).

## Architecture

```
USER -> CLAIMED SKILLS -> EVIDENCE -> CAPABILITY MODEL -> TARGET ROLE
     -> ROLE REQUIREMENTS -> SKILL GAP -> DEPENDENCY ANALYSIS
     -> ACTION PLAN -> NEW EVIDENCE -> UPDATED CAPABILITY GRAPH
```

Full diagram and repo layout: [`docs/architecture.md`](docs/architecture.md).

## Tech Stack

**Frontend:** Next.js 14 (App Router) · TypeScript · Tailwind CSS ·
TanStack Query · React Flow · Recharts · Lucide icons

**Backend:** FastAPI · Python 3.12 · Pydantic v2 · SQLAlchemy 2.0 · JWT auth
(python-jose) · bcrypt

**Database:** PostgreSQL-ready via SQLAlchemy; SQLite by default for local
development (same schema, zero external dependency)

**AI:** Provider abstraction over Anthropic / OpenAI / Google, with a fully
functional Mock provider as the default — the whole app works with **no API
key**

**Testing:** Pytest (unit + integration, FastAPI `TestClient`)

**Infra:** Docker, Docker Compose (API + Web + Postgres), GitHub Actions CI

## Synthetic Data

Generated by [`seed/generate_synthetic_data.py`](seed/generate_synthetic_data.py)
(`python -m seed.generate_synthetic_data`):

| | Count |
|---|---|
| Skills | 156 |
| Roles | 41 |
| Synthetic user profiles | 21 (20 personas + 1 admin) |
| Projects | 102 |
| Evidence records | 338 |
| Learning resources | 44 |
| Assessment questions | 31 |
| Assessment attempts | 12 |
| Recommendations (demo states) | 6 |
| Audit events | 466 |

20 personas across Frontend, Backend, AI, Data, DevOps, Cybersecurity,
Student, Career-switcher, Early-career, and Experienced-engineer profiles,
each internally consistent — a persona's "strong" skills get multiple recent
projects; a persona's "evidence gap" skills are claimed with deliberately
zero evidence, to demonstrate that concept.

## Evaluation

38/38 automated tests passing (27 unit, 7 integration), plus a clean
`typecheck`/`lint`/production `build` on the frontend. Full results and
explicitly what was *not* independently verified (Docker execution, real LLM
providers, browser E2E): [`docs/evaluation.md`](docs/evaluation.md).

## Security

JWT auth, bcrypt password hashing, per-user data isolation enforced
structurally (not just checked), Pydantic input validation, a structured
error format with no leaked stack traces, security headers, a rate limiter,
and an explicit AI threat model. Full write-up:
[`docs/security.md`](docs/security.md).

## Setup

### Backend

```bash
cd apps/api
python -m venv .venv
.venv/Scripts/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env          # optional — sensible defaults work as-is

cd ../..
python -m seed.generate_synthetic_data   # seeds ~338 evidence records, 21 users, etc.

cd apps/api
uvicorn app.main:app --reload --port 8000
```

API docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd apps/web
npm install
cp .env.local.example .env.local
npm run dev
```

App at `http://localhost:3000`.

### Docker Compose (API + Web + Postgres)

```bash
docker compose up --build
```

*(Written and reviewed by hand; not executed in the environment this was
built in — see `docs/evaluation.md`.)*

## Demo Accounts

Any seeded `@skillgraph.dev` email, password `SkillGraph2026!` — e.g.
`aayush.sharma@skillgraph.dev` (AI-focused persona). The login page pre-fills
this account. An admin account also exists at `admin@skillgraph.dev` with the
same password.

## Demo Walkthrough

1. Log in → **Dashboard**: evidence coverage, strong skills, evidence gaps,
   next best action.
2. **Roles** → pick a target role → see weighted readiness and "set as
   career goal".
3. **Gap Center** → critical/high/medium gaps, each with its dependency
   chain, plus a dedicated evidence-gap section.
4. **Learning Path** → the ordered, dependency-resolved path to close the
   top gaps.
5. **Recommendations** → "What should I build next?" — accept, reject, or
   leave a suggestion pending (human-in-the-loop, logged to the audit
   trail).
6. **Career Simulator** → add hypothetical evidence, see the readiness
   delta, confirm your real profile is untouched.
7. **AI Analyst** → ask "why am I not ready for this role?" and inspect the
   evidence panel backing the answer.
8. **Audit Trail** → every mutation above, timestamped.

## Limitations

- Docker images were written but not built/run in this environment (no
  Docker daemon available); see `docs/evaluation.md`.
- Real AI providers (Anthropic/OpenAI/Google) were implemented but not
  exercised against a live key — only the default Mock provider was tested.
- No browser/E2E (Playwright) test run was performed; the frontend is
  verified via a clean typecheck/lint/production build plus full backend API
  verification.
- `RoleSkill.min_capability_score` is stored and returned but not yet used
  to hard-gate a match classification.
- The rate limiter is in-process/in-memory, adequate for a single-instance
  demo, not for a multi-instance production deployment.

## Roadmap

- GitHub repository ingestion for real (not synthetic) repo metadata as
  evidence.
- Persisted per-skill capability history for a real Career Timeline view.
- Multi-instance-safe rate limiting (Redis-backed).
- Playwright E2E suite covering the six scenarios in `docs/evaluation.md`.

---

*Built as an end-to-end portfolio project demonstrating skill-graph
modeling, evidence-based scoring, dependency-aware gap analysis, and
grounded (not generative-fiction) AI over a real data model.*
