# NEXT ARCHITECTURE REVIEW — PsyPredictor

Date: 2026-08-13

Purpose
-------
Perform a targeted architectural inspection (no code changes) to determine the next most valuable layer to add to PsyPredictor. This review maps what exists, what is partial, which PersonState fields are dormant, and recommends the next architectural layer(s) prioritized by importance.

Current (intended) pipeline
---------------------------
PersonState → EFMSOMB → State Inference → Proposal Generation (goal/reactive/habit) → State Modulation → SystemMemory → Competition → Arbitration → DecisionResult

Files inspected (key):
- `person_state.py` — person state container
- `state_inference.py` — StateInferenceEngine
- `state_modulation.py` — StateModulator
- `action_selection.py` — propose_goal_directed / propose_reactive / propose_habitual
- `system_memory.py` — SystemMemory
- `competition.py` — BehavioralTendency, CompetitionEngine
- `arbitration.py` — arbitrate()
- `decision_engine.py` — DecisionEngine orchestration
- tests: `test_state_inference.py`, `test_state_modulation.py`, `test_state_integration.py`, `test_decision_engine.py` and full suite

Completed layers (implemented and exercised by tests)
--------------------------------------------------
1. PersonState (state container) — implemented in `person_state.py`.
2. EFMSOMB fields (emotion/feeling/mood/arousal/self_regulation/etc.) — present in `PersonState` and used by inference and reactive proposals.
3. State Inference — `StateInferenceEngine` infers multiple labels from PersonState and reports evidence/confidence; preserves manual state.
4. Proposal generation — three proposal systems implemented in `action_selection.py` (goal-directed, reactive, habitual) producing `BehavioralTendency` objects.
5. State Modulation — `StateModulator` modifies tendency strength deterministically and records reasons/factors.
6. System Memory — `SystemMemory` influences tendencies via `assess_tendency` and is integrated into `CompetitionEngine`.
7. Competition/Conflict resolution and Confidence — `CompetitionEngine` does normalization, weighting, aggregation, conflict classification, and confidence breakdown.
8. Arbitration — `arbitrate()` provides final selection and a textual reason.
9. Decision Engine — orchestration combining all above; integrates State of Mind inference and modulation and surfaces state metadata in `DecisionResult`.
10. Test coverage — the full suite runs and passes (45 tests at time of review).

Partial / supported areas (present but limited)
----------------------------------------------
- Habit strengths and pattern learner hooks exist but are light-weight in heuristics (`action_selection.propose_habitual`).
- SystemMemory supports flexible string rules and simple matching; good surface for future structure but currently heuristic.
- `StateModulator` uses a small explicit factor table (deterministic); easy to extend but not yet multi-factor.

Dormant or weakly-used `PersonState` fields
--------------------------------------------
Below each field is marked: (Used / Partial / Unused) and where it currently affects pipeline.

- `perception`: UNUSED — defined in `PersonState` but not read anywhere. No perceptual filtering layer.
- `appraisal`: UNUSED — present but not used; appraisal-based re-interpretation absent.
- `expectations`: UNUSED — not consumed; predictive / expectation signals not driving proposals or inference.
- `trigger`: PARTIAL — stored but rarely used; some scripts set `trigger` but no pipeline step maps triggers → proposals or inference.
- `physiology`: UNUSED — present but `arousal`, `energy`, `perceived_control` are independent fields actually used; `physiology` itself not inspected.
- `energy`: PARTIAL — `energy` exists on `PersonState` but not effectively used in proposals or modulation (no fatigue modeling).
- `perceived_control`: USED — read by `action_selection.ActionSelector.score_actions` and influences negotiation/avoidance heuristics.
- `awareness`: USED — read by inference and scoring (affects confusion/neglect heuristics and StayQuiet/Negotiation biases).
- `beliefs`: PARTIAL — SystemMemory reads beliefs when assessing tendencies; `PersonState.beliefs` is present but proposals rarely consult it directly.
- `values`: PARTIAL — `action_selection.propose_goal_directed` reads `values`; SystemMemory also stores values for later influence.
- `needs`: PARTIAL — `propose_goal_directed` reads `needs`; otherwise rarely used.
- `behavior`: UNUSED — `PersonState.behavior` attribute exists but is not integrated into pipeline.
- `history`: PARTIAL — `SystemMemory.history` and `PersonState.history` exist, but `PersonState.history` is not actively consulted by proposal generators.
- `personality`: PARTIAL — `personality` (aggression/avoidant) is used by `ActionSelector.score_actions` but currently limited to a couple of scalars; richer personality parameters are dormant.
- `active_patterns`: UNUSED — `PersonState.active_patterns` exists but not used; `pattern_learner`/`pattern_recognizer` used in tests but not tightly integrated into DecisionEngine for perception-appraisal loop.
- `learning_parameters`: UNUSED — present for future tuning but not consumed.
- `execution`: UNUSED at decision time — reserved to store post-decision execution outcome, not fed back into immediate proposals.
- `outcome`: PARTIAL — used in learning tests and prediction, but not used online in decision pipeline for immediate adaptation.
- `consequence`: UNUSED — present for longer-term learning tracking but not used in pipeline.

High-level gaps discovered
-------------------------
1. Perception / Appraisal / Expectations chain is not implemented. The `PersonState` contains `perception`, `appraisal`, and `expectations` placeholders, but no layer transforms external events (or `trigger`) into internal representations. Currently proposals mostly read raw EFMSOMB fields and higher-level fields (goals/needs/personality), skipping an explicit perceptual-interpretation stage.

2. Predictive / expectation signals are absent. `expectations` is not populated from past outcomes or predictions; there is no generative prediction → surprise/error signal feeding inference or modulation.

3. Physiology and energy dynamics are not modeled. `energy` is present but not used to gate proposals or adjust modulator factors (e.g., fatigue reducing tendency strength).

4. Active pattern recognition / perception coupling is weak. Pattern recognition exists in other modules and tests, but `PersonState.active_patterns` is not driven by a perception layer in the pipeline.

5. Execution → Outcome → Learning feedback loop is partial: learning modules exist (pattern learner, adaptation), but online integration (update `PersonState` after `DecisionResult`/execution, immediate adjustment of expectations) is not implemented in the DecisionEngine pipeline.

Does Perception→Appraisal→Expectations need its own layer?
-----------------------------------------------------------
Short answer: YES — it is the most important missing architectural layer.

Analysis summary:
- Current design already separates container (`PersonState`) from inference, proposal, modulation, memory, competition, and arbitration. That separation is good and supports adding a perception/appraisal layer without invasive redesign.
- Several fields in `PersonState` are expressly reserved for perception/appraisal (`perception`, `appraisal`, `expectations`, `trigger`) but are unused. That indicates the architecture intended such a layer, but it was not implemented yet.
- Building Perception→Appraisal→Expectations as a focused layer will: (a) centralize interpretation logic, (b) create reproducible evidence for StateInferenceEngine (rather than having inference read raw fields directly), (c) produce explicit expectation/prediction signals used by learning and modulation, and (d) reduce duplication across proposal systems.

What is already modeled vs missing in the full causal chain?
-----------------------------------------------------------
Modeled (exists and integrated):
- Situation (external context) → partial: `context` and `trigger` fields exist but triggers are not transformed.
- Emotion / Feeling / Mood: present and used.
- State of Mind: inferred and integrated.
- Goals/Needs/Values/Personality: present and influence proposals (partially via `ActionSelector`).
- Competing tendencies → Competition → Arbitration → Decision: implemented and tested.

Missing or incomplete:
- Perception: how external events become `perception` objects is not implemented.
- Appraisal: no explicit appraisal step mapping perception → affective/cognitive appraisals.
- Expectations: predictive signals and prediction errors are not represented or fed into inference/modulation.
- Execution/outcome loop: no automatic wiring from DecisionResult → PersonState.execution/outcome → immediate learning/expectation update.
- Physiology/energy dynamics: not incorporated.

Recommended next layer (ranked priorities)
-----------------------------------------
Critical (1): Perception → Appraisal → Expectations layer
- Why: numerous `PersonState` fields are reserved for interpretation but unused. An explicit perceptual/appraisal layer will deliver consistent inputs to `StateInferenceEngine`, enable expectation/prediction signals for modulation and learning, and prevent adding heuristics ad‑hoc into proposal systems.

Important (2): Execution/Outcome → Learning bridge
- Why: close the loop so decisions update `PersonState` (execution/outcome) and upstream expectations/patterns. This enables real-time adaptation and provides evidence to `StateInferenceEngine` and `SystemMemory`.

Important (2): Physiology & Energy gating
- Why: energy/fatigue and physiology often modulate action strength and self-regulation; integrating them into `StateModulator` or a small regulator will improve realism.

Later (3): Richer perception-to-pattern coupling & active patterns
- Why: once appraisal/prediction and execution loops exist, integrate `active_patterns` with perception to match experienced sequences and drive habitual proposals.

Architectural risks
-------------------
- Adding perception/appraisal logic inside proposal systems (goal/reactive/habit) would duplicate code and break modularity. Keep it as a single layer that publishes interpreted signals.
- Overfitting: do not add heavy psychological formulas now; keep explicit, deterministic rules and clear evidence reporting.
- Data flow confusion: ensure the inference layer reads appraisal results rather than raw perception to keep explainability.

What should NOT be built yet
---------------------------
- Do NOT add complex probabilistic cognitive models (Bayesian belief networks) now.
- Do NOT entangle CompetitionEngine with appraisal or perception internals — competition must remain agnostic to the origin of pressures.
- Do NOT convert StateInferenceEngine into an action selector or inject decision traces into inference as evidence (the final action must not be used to infer state at decision time).

Proposed future pipeline (next iteration)
-----------------------------------------
External Event / Trigger
  ↓
Perception Layer (raw senses → structured perceptions)
  ↓
Appraisal Layer (perception → interpreted significance: threat, opportunity, responsibility, etc.)
  ↓
Expectations / Predictive Signals (generate expectations for outcomes; compute prediction error when outcomes observed)
  ↓
EFMSOMB (emotion, feeling, mood, arousal updated by appraisal & expectations)
  ↓
State Inference (consume appraisal + EFMSOMB + expectations → State of Mind inference)
  ↓
Proposal Generation (goal/reactive/habitual read PersonState + appraisal/expectations)
  ↓
State Modulation (apply State of Mind + physiology/energy modifiers)
  ↓
SystemMemory (contextual multiplicative adjustments)
  ↓
Competition → Arbitration → DecisionResult
  ↓
Execution → Outcome → Learning (update expectations, pattern learner, system memory)

Deliverables from this review
-----------------------------
- `NEXT_ARCHITECTURE_REVIEW.md` (this document)
- Recommendation to implement a minimal Perception→Appraisal→Expectations service before adding further heuristics

Next steps (no coding until approval)
------------------------------------
1. Review this document and confirm you want the Perception→Appraisal→Expectations layer next.
2. If approved, I'll propose a minimal API for the perception/appraisal layer (data contracts: Perception object, Appraisal object, Expectations object) and a small set of deterministic rules to populate `person_state.perception`, `person_state.appraisal`, and `person_state.expectations`.

Conclusion (plain language)
---------------------------
You already have a working decision pipeline and State of Mind integrated. Many `PersonState` fields reserved for interpretation are not used yet — most importantly `perception`, `appraisal`, and `expectations`. The next critical step is to add a small, explicit Perception→Appraisal→Expectations layer that turns external events into interpreted signals. This will (a) make `StateInferenceEngine` cleaner and more explainable, (b) enable prediction/error signals for learning, and (c) reduce ad-hoc heuristics being scattered through proposal systems. Don't build complex models yet — start with a minimal, deterministic interpretation layer and a clear API.
