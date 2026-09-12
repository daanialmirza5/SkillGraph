# Skill Taxonomy

Defined in [`seed/skills_data.py`](../seed/skills_data.py).

## Categories (16)

Programming, Data, Machine Learning, AI, Cloud, DevOps, Databases, Backend,
Frontend, Security, Systems, Product, Communication, Leadership, Research,
Domain Knowledge.

## Skills (156)

Each skill has: `name`, `category`, `description`, `aliases` (alternate names
a resume or project description might use), and an optional `parent_skill`
(e.g. "React" is a subskill of "JavaScript"). Parent/child pairs are also
materialized as explicit `SUBSKILL_OF` rows in `skill_relationships` so the
same relationship table drives every kind of skill-graph traversal.

## Relationship types

| Type | Meaning | Used by |
|---|---|---|
| `PARENT_OF` / `SUBSKILL_OF` | Hierarchical grouping (e.g. Machine Learning → Deep Learning) | Skill graph display |
| `PREREQUISITE_OF` | You should learn A before B is practical | Dependency engine, learning paths |
| `USED_WITH` | Commonly paired in practice (e.g. Python + Pandas) | Skill graph display |
| `RELATED_TO` | Conceptually related but not a hard dependency | Skill graph display |

`EXTRA_RELATIONSHIPS` in `seed/skills_data.py` defines ~50 explicit edges,
including real prerequisite chains such as:

```
Docker -> CI/CD -> Model Deployment -> Model Monitoring -> MLOps
Python -> Machine Learning -> Deep Learning -> Large Language Models -> Prompt Engineering
HTML -> CSS -> React -> Next.js
```

Only `PREREQUISITE_OF` edges are walked by the dependency engine
(`app/engines/dependency_engine.py`) — the other relationship types are
descriptive and used for the graph explorer UI, not for gap logic.

## Extending the taxonomy

To add a skill: add a tuple to `SKILLS` in `seed/skills_data.py`, then wire it
into any role that requires it (`seed/roles_data.py`), any learning resource
(`seed/learning_resources_data.py`), and optionally a project template
(`apps/api/app/data/project_templates.py`). The generator
(`seed/generate_synthetic_data.py`) validates every cross-reference at import
time — a typo'd skill name fails loudly rather than silently seeding bad data.
