# Architecture

## System overview

```
                     SKILLGRAPH
                         |
                +--------+--------+
                v                 v
          USER PROFILE       ROLE LIBRARY
                |                 |
                v                 v
           EVIDENCE GRAPH     ROLE SKILL GRAPH
                |                 |
                +--------+--------+
                         v
                  SKILL GAP ENGINE
                         |
              +----------+----------+
              v          v          v
        DEPENDENCIES   PRIORITY   COVERAGE
              |          |          |
              +----------+----------+
                         v
                RECOMMENDATION ENGINE
                         |
              +----------+----------+
              v          v          v
          LEARNING    PROJECTS    ASSESSMENTS
              |          |          |
              +----------+----------+
                         v
                   AI ANALYST
                         |
                         v
                  HUMAN REVIEW
                         |
                         v
                    AUDIT LOG
```

## Repository layout

```
skillgraph/
  apps/
    api/            FastAPI backend (Python 3.12, SQLAlchemy 2.0, Pydantic v2)
      app/
        core/       config, database session, JWT auth, security headers/rate limit
        models/     SQLAlchemy ORM models (domain entities)
        engines/    the actual intelligence: scoring, gaps, dependencies, recs, sim, assessments
        ai/         provider abstraction + grounded career analyst
        routers/    REST API endpoints
        schemas/    Pydantic request/response schemas
        data/       curated static data used at runtime (project templates)
      tests/
        unit/       engine-level tests, no HTTP layer
        integration/ FastAPI TestClient end-to-end flows
    web/            Next.js 14 (App Router) + TypeScript + Tailwind frontend
  seed/             synthetic data definitions + the generator script
  docs/             this documentation
  .github/workflows/ CI (lint, test, typecheck, build)
```

## Request flow

1. The Next.js frontend authenticates via `POST /api/auth/login` (OAuth2 password
   flow) and stores a JWT in `localStorage`.
2. Every subsequent request carries `Authorization: Bearer <token>`.
   `app/core/deps.py` decodes the token and resolves the current `User`; all
   "my data" endpoints filter by `user.id` server-side — a user can never read
   or write another user's evidence, projects, or goals.
3. Endpoints call into `app/engines/*`, which are pure functions over the
   database session — no engine talks to the network or an LLM. This keeps the
   scoring/gap/recommendation logic deterministic, unit-testable in isolation,
   and impossible for an LLM to silently influence.
4. The AI layer (`app/ai/*`) is the only component that reaches an LLM (or the
   Mock provider), and it only ever *narrates* what the engines already
   computed — see `ai-architecture.md`.

## Why this shape

The spec's central product principle is "what can this person prove?", not
"what keywords are on their resume?" That means the evidence model and the
scoring/gap/recommendation engines are the real product; the API and frontend
are thin layers over them. Per the build priority in the project brief, engine
correctness was implemented and tested before frontend polish, and the AI
layer was built last, on top of already-correct deterministic data.
