# Security

## Authentication & authorization

- JWT bearer tokens (`python-jose`, HS256), issued on `/api/auth/login` and
  `/api/auth/register`, expiring after `JWT_EXPIRE_MINUTES` (default 12h).
- Passwords hashed with `bcrypt` directly (12-round default salt), truncated
  to 72 bytes per bcrypt's own limit before hashing — never stored or logged
  in plaintext.
- Every "my data" endpoint (`/api/profile`, `/api/evidence`, `/api/projects`,
  `/api/career-goals`, `/api/recommendations`, `/api/audit`, ...) filters
  exclusively by `current_user.id` from the decoded token — there is no
  endpoint that accepts an arbitrary user ID from the client for these
  routes, so cross-user access is structurally not possible rather than
  merely checked. This is exercised directly in
  `tests/integration/test_api_flow.py::test_cross_user_data_is_isolated`.
- A minimal RBAC role (`user` / `admin`) exists on the `User` model with an
  `require_admin` dependency, for future admin-only endpoints; none of the
  current endpoints require it, so cross-user data isolation does not depend
  on role checks being correct.

## Input validation

- All request bodies are validated by Pydantic v2 schemas.
- Enum-like string fields (evidence type, verification status) are validated
  against the real `Enum` and rejected with a structured
  `INVALID_ENUM_VALUE` error rather than silently coerced.
- `complexity` is range-checked (1-5) at the API boundary.

## Error format

Every error response is `{"error": {"code": "...", "message": "..."}}` —
never a raw stack trace. An unhandled exception is caught by a top-level
handler, logged server-side, and returned as a generic `INTERNAL_ERROR` to
the client (`app/main.py`).

## Transport & headers

- CORS is restricted to `CORS_ORIGINS` (defaults to the local frontend origin
  only).
- Every response gets `X-Content-Type-Options: nosniff`,
  `X-Frame-Options: DENY`, and `Referrer-Policy: no-referrer`.
- A simple in-memory sliding-window rate limiter
  (`RATE_LIMIT_PER_MINUTE`, default 120/min per client IP) protects against
  basic abuse. It is intentionally simple (in-process, not distributed) —
  adequate for a single-instance demo deployment, not a substitute for a
  real edge rate limiter in a multi-instance production deployment.

## Secrets

- No secret is hardcoded anywhere in the codebase. `.env.example` documents
  every configurable value with empty/placeholder defaults.
- `.env` is git-ignored (`.gitignore`).
- AI provider keys are read from environment variables only, and the app is
  fully functional with none of them set (Mock provider).

## AI-specific threat model

See `docs/ai-architecture.md` for the full grounding and prompt-injection
design. Summary of what the AI **cannot** do, by construction:

- Cannot write to the database — every engine/AI function that reads data is
  read-only; all mutations happen through normal authenticated REST endpoints
  that a human client calls directly, never as a side effect of an AI
  response.
- Cannot see another user's data — the AI analyst is scoped to
  `current_user.id` exactly like every other endpoint.
- Cannot present invented facts as if they were computed by the engines — the
  system prompt requires it to say "not enough evidence" rather than guess,
  though this depends on the underlying model's instruction-following and is
  not a hard technical guarantee for real providers (only the Mock provider,
  used by default, is mechanically incapable of inventing facts, since it
  never generates novel text — it only reformats the evidence package).

## Known limitations

- The rate limiter is per-process and in-memory; it resets on restart and
  does not coordinate across multiple instances.
- There is no email verification or password-reset flow — out of scope for a
  demo/portfolio system with synthetic accounts.
- `RoleSkill.min_capability_score` is stored and returned by the API but not
  yet used to hard-gate a match classification — see `docs/role-matching.md`.
