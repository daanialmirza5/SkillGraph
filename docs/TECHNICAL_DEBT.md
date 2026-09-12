# SkillGraph — Technical Debt & Architectural Audit

**Repository**: `SkillGraph`  
**Status**: Tier 1 Flagship (38 passing tests)

## Prioritized Debt Items
- **[P1 — High] Async Task Queue for Heavy Artifact Ingestion**: Parsing large external repositories runs synchronously in request lifecycles. Should be moved to Celery/ARQ with Redis.
- **[P2 — Medium] In-Memory Taxonomy Caching**: Skill prerequisite DAG is queried from DB repeatedly. Should use Redis or in-memory LRU cache.
- **[P3 — Low] JWT Refresh Token Rotation**: Current auth uses standalone access tokens. Add sliding window refresh tokens in HttpOnly cookies.
