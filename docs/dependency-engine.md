# Dependency Engine

Implemented in [`apps/api/app/engines/dependency_engine.py`](../apps/api/app/engines/dependency_engine.py).

## What it does

Walks `PREREQUISITE_OF` edges in `skill_relationships` backward from a target
skill to build its full prerequisite chain, in build order (furthest
prerequisite first, target last).

```python
get_prerequisites(db, skill_id)          # recursive, cycle-safe (visited set)
get_dependency_chain_for_target(db, id)  # returns an ordered list ending at `id`
```

Example, for the seeded relationship data:

```
get_dependency_chain_for_target(MLOps)
  -> [Docker, CI/CD, Model Deployment, Model Monitoring, MLOps]
```

If a skill has no modeled prerequisites, the chain is just `[skill]`.

## Why this matters

Section 25 of the product brief calls this out explicitly: showing "Missing
MLOps" is far less useful than showing the ordered chain of what to build
first. This same function backs three different features:

- **Gap Center** (`docs/gap-engine.md`) — attaches the chain to each gap.
- **Learning Path** (`docs/recommendation-engine.md`) — resolves prerequisite
  chains for the top N open gaps and de-duplicates them into one ordered path.
- **AI Analyst** (`docs/ai-architecture.md`) — the Dependency Analyst agent
  function includes resolved chains in the grounded context so the model can
  explain *why* a skill is blocked without inventing the chain itself.

## Cycle safety

`get_prerequisites` tracks visited skill IDs and stops recursing into a skill
it has already visited in the current traversal, so a (data-entry) cycle in
`skill_relationships` cannot cause infinite recursion.
