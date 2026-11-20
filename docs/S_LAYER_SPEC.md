# S-Layer (State-of-Mind) Specification

Purpose
-------

This document specifies the canonical semantics for the State-of-Mind (S-layer)
vocabulary that the project will freeze for architecture and runtime audits.

Scope
-----

Applies to research, unit tests, runtime reconciliation audits, and any
integration that needs a shared interpretation of internal state labels.

Principles
----------
- Single source of truth: `registry/s_layer.yaml` is authoritative for labels.
- Explicit mappings: each label includes a `runtime_mapping` for audits.
- Separate persistence classes: `dynamic`, `semi-stable`, `core`.

Canonical labels
----------------
Canonical S labels in `registry/s_layer.yaml` are descriptive and focused on
semantic boundary tests, definitions, and examples. The freeze intentionally
records meaning and boundary tests only; it does not include runtime typing,
ranges, or `runtime_mapping` entries. Runtime mappings are assigned during the
separate runtime reconciliation audit.

Persistence categories
- dynamic: short-lived, event-to-event state (e.g., `attention`, `valence`).
- semi-stable: slowly-changing dispositions (e.g., `mood`, `habit_bias`).
- core: stable identity properties (not present in v1 of the registry).

Usage patterns
--------------
- Freezing: produce a branch that adds `registry/s_layer.yaml` and spec files.
- Audit-only: the freeze is a semantic checkpoint — do not change runtime code
  as part of the freeze. Use the runtime reconciliation audit to report mismatches.
-- Runtime reconciliation: a separate non-merge step that verifies runtime
  locations for S (for example `state_inference.py`, `StateManager` and
  `PersonState`) and records validated mappings in a reconciliation artifact.
  The reconciliation step is explicitly audit-only at first (no code changes).

Verification & testing
----------------------
- YAML validation: ensure `registry/s_layer.yaml` parses and matches a minimal
  schema (types and ranges).
- Internal consistency: confirm `runtime_mapping` paths exist or are plausibly
  documented in the codebase.

Change control
--------------
- This freeze is explicit: create a branch named `freeze/s-layer` and a PR.
- Do not merge the PR. The presence of the PR marks the canonical semantics.

Example (excerpt)
------------------
See `registry/s_layer.yaml` for the full canonical label set and examples.

Next steps for auditors
-----------------------
1. Checkout `freeze/s-layer` (once created).
2. Run a runtime reconciliation audit that inspects:
   - `state_inference.py`
   - `StateManager` implementation in `state_manager.py`
   - `PersonState` runtime attributes referenced by `runtime_mapping`.
3. Produce a mismatch report (no code changes) describing mapping gaps.
# S-Layer Semantic Specification (Freeze Record)

Purpose
- Capture the frozen semantic definition of the State-of-Mind (S) layer prior to runtime or registry mappings.

What S Is
- Definition: S = interpretive/regulatory posture describing how a person temporarily organizes attention, openness, and response strategy. Not an emotion, feeling, mood, trait, appraisal conclusion, or observable behavior.
- Scope: Episode-limited modes that guide how appraisal and action-selection weight evidence and options.

Hard Boundary Tests
- Form-generation: Remove situation/object — does the label still name a recognizable temporary posture? (PASS/FAIL)
- Situation-removal: Strip event/appraisal content — does the remainder still describe a temporary posture? (PASS/FAIL)
- Layer-purity: Ensure definition avoids valence, bodily feeling, habitual trait, appraisal outcome, or observable action.

Canonical S (frozen)
- S3 — Curious
  - Receptive exploratory attention; temporary information-seeking posture prioritizing broadened attention and hypothesis sampling.
- S8 — Open-minded
  - Episodic receptivity to alternatives and evidence; widens acceptance thresholds for the episode.
- S9 — Closed-minded
  - Transient narrowing of acceptable perspectives; increases confirmatory stance for the episode.
- S18 — Empathetic
  - Temporary perspective-taking posture prioritizing another's viewpoint and social attunement (distinct from trait empathy or emotion).
- S24 — Cautious
  - Temporary risk-averse posture favoring conservative evidence thresholds and deliberate action selection (phrased as posture, not mechanism).

Nodes removed from S (freeze mappings recorded)
- S11 Hopeful → Mood/Emotion
- S30 Patient → Trait
- S5 Creative → Trait/Cognitive-style
- S6 Analytical → Cognition/Appraisal
- S14 Judgmental → Cognition/Appraisal
- S16 Stressed → Mood
- S19 Reassured → Feeling/Emotion

Wording Guardrails
- Avoid causal/mechanistic phrases such as “lowers threat-sensitivity” or “reducing impulsive thresholds.” Use posture-focused language: “prioritizes information sampling,” “adopts a risk-averse posture,” “temporarily tolerates delay.”
- Always mark S definitions as episode-limited when overlapping with trait vocabulary.

Audit & Freeze Rationale
- The five canonical nodes pass the Form-Generation and Situation-Removal tests when phrased as transient postures and when mechanism language is removed.
- The seven removed nodes fail one or more boundary tests or map more cleanly to Mood/Feeling/Cognition/Trait; their destination-layer mappings are recorded for later reconciliation.

Next Steps (post-freeze)
1. Keep runtime and registry untouched until canonical S vocabulary is accepted.
2. Perform runtime reconciliation mapping `state_inference.py`/`StateManager` labels to this canonical set.
3. After mapping plan approval, implement registry and any runtime updates in targeted PRs.
