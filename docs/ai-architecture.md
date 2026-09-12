# AI Architecture

## Pipeline

```
User Question
      |
      v
Retrieve Skill Graph (graph_service.build_user_skill_graph)
      |
      v
Retrieve Role Graph + Gap Result (gap_engine.compute_role_gap)      [if a role is selected]
      |
      v
Retrieve Evidence + Dependency Chains (per top gap)
      |
      v
Retrieve Project Recommendation (recommendation_engine)
      |
      v
Evidence Package  (assembled by app/ai/agents.py)
      |
      v
LLM (or Mock provider)
      |
      v
Grounded Explanation + Evidence Panel + Confidence + Limitations
```

Everything above the LLM call is deterministic and reuses the exact same
engine functions the REST API and frontend use — the AI layer has no private
path to the data that could diverge from what a human sees on the Gap Center
or Learning Path pages.

## "Multi-agent" design

The product brief calls for specialized analyst roles (Skill Analyst, Gap
Analyst, Role Analyst, Evidence Analyst, Dependency Analyst, Project Advisor,
Career Narrator). These are implemented as separate, independently testable
**functions** in `app/ai/agents.py`, each responsible for turning one slice of
already-computed structured data into a fact list:

- `skill_analyst` — top evidenced skills by score
- `role_analyst` — target role summary + readiness
- `gap_analyst` — top gaps with match state
- `evidence_analyst` — raw evidence records for a given skill
- `dependency_analyst` — resolved prerequisite chain for a skill
- `project_advisor` — the current top project recommendation
- `career_narrator` — combines all of the above into one structured brief

This is a deliberate design choice: rather than running N separate LLM calls
(more latency, more cost, and more surface area for one agent to
hallucinate a fact another agent didn't provide), a single LLM call narrates
a brief that was already assembled by deterministic, unit-testable
functions. This keeps the "multi-agent" separation of concerns without the
reliability and cost problems of an actual multi-LLM-call pipeline for a
task where the underlying facts are already fully known.

## Multi-provider abstraction

`app/ai/providers.py` defines `AIProvider.generate(system_prompt, user_prompt)`
with four implementations:

| Provider | How it works |
|---|---|
| `mock` (default) | No network call. Formats the assembled evidence package into readable prose. **The entire application works with this and no API key.** |
| `anthropic` | Raw `httpx` POST to the Messages API. |
| `openai` | Raw `httpx` POST to the Chat Completions API. |
| `google` | Raw `httpx` POST to the Gemini `generateContent` endpoint. |

Selected via `AI_PROVIDER` env var; falls back to `mock` if unset or
unrecognized. Real providers require their respective `*_API_KEY` env var and
raise a clear error if it's missing — they are never silently substituted.

## Grounding rules (enforced via system prompt + code)

1. The model may only reference what's in the evidence package — the system
   prompt (`career_analyst.SYSTEM_PROMPT`) states this explicitly, and the
   package itself is built exclusively from real query results.
2. If information is missing, the required response is: *"The current
   profile does not contain enough evidence to determine this."*
3. The model must never claim a hiring outcome or "expert" status — this is
   a hard rule in the system prompt, reinforced by the disclaimer shown
   everywhere readiness numbers appear (see `docs/security.md`).
4. The AI **cannot** mutate scores, evidence, roles, or recommendation status.
   It can only be asked questions; every write path in the API requires a
   normal authenticated request from the human user (see the Human-in-the-loop
   workflow in `docs/recommendation-engine.md`).

## Prompt-injection defense

Free-text the user or another user's public data might contain (project
descriptions, notes) is treated as untrusted. `career_analyst.py` provides:

- `flag_prompt_injection(text)` — a small pattern set that flags common
  override attempts ("ignore ... instructions", "you are now", "disregard
  ... rules", "system prompt").
- `wrap_untrusted(label, text)` — wraps such content in an
  `<untrusted_user_content>` tag, appending a `[FLAGGED: ...]` marker when a
  pattern matches, so a reviewer (or future LLM call) can see it was treated
  as inert data rather than an instruction.

The system prompt separately instructs the model that any tagged content is
data to analyze, never an instruction to follow — this is the primary
defense; the regex flags are a secondary, auditable signal, not the sole
protection (see `docs/security.md` for the full threat model and its limits).

Tested in
[`tests/unit/test_ai_security.py`](../apps/api/tests/unit/test_ai_security.py)
and exercised end-to-end in
[`tests/integration/test_api_flow.py::test_ai_analyst_responds_without_api_key`](../apps/api/tests/integration/test_api_flow.py).
