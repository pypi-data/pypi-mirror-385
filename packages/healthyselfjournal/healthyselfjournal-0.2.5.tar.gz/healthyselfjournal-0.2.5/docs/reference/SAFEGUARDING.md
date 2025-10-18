# Safeguarding

STILL IN PROGRESS

## Introduction

Concise principles and practices to prevent harm in a voice‑first journaling app. Focus: anti‑sycophancy, autonomy support, rumination mitigation, usage pacing, and clear boundaries/referrals.

## See also

- `PRODUCT_VISION_FEATURES.md` – values (evidence, long‑term wellbeing)
- `SCIENTIFIC_RESEARCH_EVIDENCE_PRINCIPLES.md` – research standards
- `GLOBAL_CRISIS_RESOURCES.md` – comprehensive verified crisis helplines globally
- `../research/AUTONOMY_SUPPORT_MI_SDT_FOR_JOURNALING.md` – MI/SDT autonomy support
- `../research/ANTI_SYCOPHANCY_AND_PARASOCIAL_RISK_GUARDRAILS.md` – anti‑sycophancy guardrails
- `PRIVACY.md` – local‑first data boundaries
- `DIALOGUE_FLOW.md` – question sequencing

## Principles

- Evidence‑based by default; prioritize long‑term wellbeing over engagement
- Autonomy‑supportive language; permission‑based suggestions
- Neutral acknowledgements; avoid praise, superlatives, emojis, role claims
- Redirect rumination to specifics, time bounds, or a small next step
- Clear scope boundaries; signpost human help when needed
- Encourage offline action and human connection; add gentle break nudges

## Guardrails (operational)

- Prompt rules: anti‑praise/anti‑sycophancy; neutrality; rumination pivots
- Break pacing: non‑blocking reminder around ~20 minutes; weekly usage reflection
- Boundaries footer: brief reminder of scope + verified crisis resources (see `GLOBAL_CRISIS_RESOURCES.md`)
- Summary style: concise, action‑oriented highlights; avoid valence‑laden approval
- Optional runtime checks: flag exclamation/superlatives; cap affect‑only loops

## Implementation notes

- See `healthyselfjournal/prompts/question.prompt.md.jinja` for exact rules
- CLI should expose break‑nudge configuration and referral text source
- Crisis resources: comprehensive verified catalogue in `GLOBAL_CRISIS_RESOURCES.md` (verified quarterly)
- Research found 9% of mental health apps provided erroneous crisis numbers; our catalogue uses authoritative sources
- Tests: add cases for short‑take discards, rumination pivot triggers, boundary text presence

## References (selected)

- WHO (2023). Ethics and governance of AI for health: `https://www.who.int/publications/i/item/9789240077989`
- NICE (2022). Evidence Standards Framework (DHT): `https://www.nice.org.uk/about/what-we-do/our-programmes/evidence-standards-framework-for-digital-health-technologies`
- MI/SDT overview and meta‑analyses: see linked research docs above
- Rumination and self‑distancing: Nolen‑Hoeksema (2008); Kross et al. (2014)
