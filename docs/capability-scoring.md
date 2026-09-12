# Capability Scoring

Implemented in [`apps/api/app/engines/capability_scoring.py`](../apps/api/app/engines/capability_scoring.py).
Tested in [`tests/unit/test_capability_scoring.py`](../apps/api/tests/unit/test_capability_scoring.py).

This produces an **evidence-based capability indicator** — not a measurement
of true human expertise and not a hiring signal on its own.

## Inputs

For a given (user, skill) pair, every `Evidence` row becomes an
`EvidenceInput(type, date, complexity, verification_status)`.

## Step 1 — score each evidence item

```
item_score = base_strength(type) * recency_multiplier(date)
                                  * complexity_multiplier(complexity)
                                  * verification_multiplier(status)
```

**Base strength by evidence type** (0-100 scale):

| Type | Base | Type | Base |
|---|---|---|---|
| Work Experience | 70 | Assessment | 40 |
| Internship | 55 | Certification | 30 |
| Publication | 60 | Portfolio | 25 |
| Competition | 50 | Course | 15 |
| Project | 45 | | |
| GitHub Repository | 35 | | |

**Recency multiplier** (age of the evidence, in months):

| Age | Multiplier |
|---|---|
| ≤ 6 months | 1.00 |
| ≤ 12 months | 0.90 |
| ≤ 24 months | 0.75 |
| ≤ 36 months | 0.55 |
| > 36 months | 0.35 |

This is a decay factor, not a cliff — old evidence still counts, just less.

**Complexity multiplier**: `0.7 + 0.15 * complexity`, for `complexity` in
`[1, 5]` → ranges from 0.85 to 1.45.

**Verification multiplier**: `VERIFIED` = 1.2, `SELF_REPORTED` = 1.0,
`UNVERIFIED` = 0.85.

## Step 2 — combine with diminishing returns

Repetition matters, but the fifth project demonstrating "Python" shouldn't
count as much as the first. Items are sorted by score descending, then each
is weighted by rank:

```
weight(rank) = 1 / (1 + 0.4 * rank)     # rank 0, 1, 2, ...
raw_total    = sum(item_score * weight(rank))
```

## Step 3 — normalize to a saturating 0-100 score

```
score = 100 * (1 - exp(-raw_total / 120))
```

This saturates smoothly instead of hard-capping, so a large pile of strong
evidence approaches but never artificially jumps to exactly 100.

## Step 4 — map to a label

| Score | Level |
|---|---|
| ≥ 85 | EXPERT-LIKE |
| ≥ 65 | STRONG |
| ≥ 40 | PRACTICAL |
| ≥ 20 | DEVELOPING |
| < 20 | FOUNDATIONAL |

## Confidence

Independent of the score, `confidence_for()` reports `LOW` / `MEDIUM` / `HIGH`
based on how much and how verified the evidence is — 3+ items with at least
one verified is `HIGH`; a single self-reported item is `LOW`. A high score
with low confidence (e.g. one very complex but unverified project) is
possible and is surfaced honestly rather than hidden.
