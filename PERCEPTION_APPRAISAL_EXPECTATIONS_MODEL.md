# Perception → Appraisal → Expectations Model (Design)

Date: 2026-08-13

Purpose
-------
Define the API and data contracts for a minimal, deterministic Perception → Appraisal → Expectations subsystem for PsyPredictor. This document specifies the representations, required fields, provenance, confidence, boundaries, a small first-pass rule set, coexistence and contradiction handling, behavior under insufficient information, manual vs inferred flags, integration with `StateInferenceEngine`, and examples.

Design principles (non-negotiable)
--------------------------------
- Keep the layer deterministic, explainable, and traceable.
- Perception must remain observational (what is sensed), not interpretive.
- Appraisal must be interpretive (meaning assigned to perceptions).
- Expectations must be predictive statements about likely outcomes and their confidence.
- Do not implement learning or ML here; produce rules with explicit evidence lists.
- Do not modify `StateInferenceEngine`, `DecisionEngine`, `StateModulator`, `CompetitionEngine`, or `arbitration` in this design stage.

Overview: data contracts
------------------------
Three core objects: `Perception`, `Appraisal`, and `Expectations`.

Representation choice: runtime dataclass objects (recommended)
------------------------------------------------------------
PsyPredictor is already structured around runtime objects instead of dictionary-centric contracts. Examples include `PersonState`, `BehavioralTendency`, `DecisionResult`, and `StateInferenceResult`, which are all object-oriented runtime records with explicit fields and explainable mutation points. For this layer, the best fit is a dataclass-based runtime object model, not `TypedDict`.

Why the dataclass choice is the best fit for PsyPredictor:
- Existing architecture: `PersonState` is a runtime object that stores state, and the rest of the pipeline already consumes object graphs rather than ad hoc dict contracts.
- Explainability/provenance: dataclass objects can carry field-level provenance, support default values, and remain easy to inspect in debug output without losing type fidelity.
- Mutation vs immutability: the project already mutates `PersonState` and other runtime objects in-place. A dataclass allows snapshot-style updates while still supporting mutation at assembly time.
- Serialization: dict conversion is easy at the boundary for storage, API transfer, or JSON output, but the in-memory model remains an object and is not forced into dict-only semantics.
- Testing: object assertions are clearer than nested dict assertions, and dataclasses preserve explicit structure for unit tests.
- Future learning/history storage: runtime objects are natural for attaching evidence, timestamps, and later learning history without squeezing everything into loose dict keys.
- Compatibility with `StateInferenceEngine`: it already works with structured runtime objects and evidence dictionaries; dataclass objects are compatible with this design and simpler to consume.
- Compatibility with `DecisionEngine`: the stage objects can be attached directly to `PersonState` and consumed by later modules without forcing an intermediate dict conversion.
- Ease of debugging: dataclass `repr` and attribute inspection are significantly easier for human debugging and for tracing provenance during single-step execution.

The implementation should therefore use runtime dataclass objects for `Perception`, `Appraisal`, `Expectations`, and their nested items, while allowing optional conversion to dictionaries at the serialization boundary when needed.

General representation rules
- All objects are runtime data objects with explicit fields and clear defaults. They are stored on `PersonState` as typed object instances, not loose dictionaries.
- All objects include: `id` (unique), `timestamp` (ISO8601), `source` (string), `evidence` (list of provenance records), `confidence` (float 0.0–1.0), `manual` (bool), and `insufficient_data` (bool).
- `evidence` entries are small provenance records: {"field": str, "value": any, "source": str, "note": str}.
- The object model remains explainable and debug-friendly, while serialization to dictionaries remains optional and externally generated.

1) Perception
-------------
Purpose: structured, de-duplicated observations derived from raw external event(s) or sensors. Perception must not include meaning/interpretation.

Required fields:
- `id`: string
- `timestamp`: string
- `source`: string (e.g., "trigger", "sensor", "user_report", "system")
- `observations`: list of Observation objects (see below)
- `confidence`: float (0.0–1.0) overall confidence in the perception extraction
- `manual`: bool (if true, perception was manually supplied)
- `insufficient_data`: bool (True when no usable perception was extracted)

Optional fields:
- `context_id`: string (links to PersonState.context or event id)
- `note`: human text

Observation object (each item in `observations`):
- `type`: string (e.g., "voice_volume", "gesture", "proximity", "utterance", "facial_expression")
- `value`: any (raw or normalized value, e.g., "loud", 0.8)
- `normalized`: optional numeric value (0.0–1.0) when applicable
- `location`: optional string
- `timestamp`: optional string
- `evidence`: list of provenance records

Meaning of fields:
- `observations` enumerate *what was sensed* (e.g., "voice volume: loud", "utterance: 'You never listen'", "distance: close").
- `confidence` reflects parser/sensor reliability and does NOT imply appraisal confidence.

What can produce a Perception:
- Raw events (triggers), sensors, transcripts, user inputs, or upstream modules that annotate raw events.

What Perception must NOT directly determine:
- Appraisal labels (threat/opportunity), expectations, or State of Mind. Those are separate layers.

2) Appraisal
------------
Purpose: assign interpreted significance to perceptions in human-understandable terms (controllability, intentionality, relevance, valence), producing a small set of appraisal frames that downstream systems can consume.

Required fields:
- `id`, `timestamp`, `source`, `confidence`, `manual`, `insufficient_data`
- `frames`: list of AppraisalFrame objects

AppraisalFrame object:
- `label`: string (e.g., "threat", "opportunity", "unfairness", "ambiguity", "irrelevant")
- `dimension_scores`: dict of specific appraisal dimensions (see below) with values in [-1.0, 1.0]
- `supporting_perceptions`: list of Perception.ids used as evidence
- `evidence`: list of provenance records (each includes why this frame applies)
- `confidence`: float (0.0–1.0) for this frame

Standard appraisal dimensions (each between -1.0 and 1.0):
- `valence` (positive → favorable, negative → unfavorable)
- `goal_relevance` (0.0–1.0; negative allowed if detrimental)
- `controllability` (-1.0 to 1.0; high positive means person can control outcome)
- `intentionality` (-1.0 to 1.0; positive indicates perceived intentionality by others)
- `suddenness` (0.0–1.0)
- `ambiguity` (0.0–1.0)
- `social_threat` (0.0–1.0)

Meaning of fields:
- `frames` are independent appraisal hypotheses; multiple frames can coexist (e.g., both "threat" and "ambiguity").
- `dimension_scores` provide structured numeric cues that `StateInferenceEngine` can consume.

What can produce an Appraisal:
- Perception objects + PersonState context, goals, needs, values, and simple deterministic rules.

What Appraisal must NOT directly determine:
- Final State of Mind labels (the `StateInferenceEngine` will decide), action selection, or learning updates.

3) Expectations
---------------
Purpose: short-term predictive statements about likely outcomes and their confidence; used to compute prediction error when actual outcomes occur and to modulate proposals.

Required fields:
- `id`, `timestamp`, `source`, `confidence`, `manual`, `insufficient_data`
- `predictions`: list of Prediction objects

Prediction object:
- `outcome_label`: string (e.g., "confrontation", "apology", "ignore", "negotiation")
- `probability`: float (0.0–1.0)
- `supporting_appraisals`: list of AppraisalFrame.ids
- `evidence`: list of provenance records

Optional fields:
- `expected_timeline`: optional estimated time horizon (seconds/minutes)

Meaning of fields:
- `predictions` are mutually non-exclusive; probabilities should sum <= 1.0 (they are independent hypotheses) unless normalized.

What can produce Expectations:
- Appraisal frames + PersonState.history/patterns + simple mapping rules or prior probabilities.

What Expectations must NOT directly determine:
- State of Mind labels (they are a cue for inference), final action choice, or training updates (these happen after outcome).

Evidence / Provenance model
---------------------------
- Each object includes `evidence`: list of {"field": str, "value": any, "source": str, "note": str}
- `source` indicates origin ("sensor", "transcript", "manual", "system", "pattern_learner").
- `confidence` is computed as the minimum of constituent confidences (for composition) or provided by manual input.

Information flow (exact)
------------------------
1. External Event / Trigger: raw event enters the system (could be timestamps, transcripts, sensor data, or direct `trigger` in `PersonState`).
2. Trigger normalization boundary: `Perceptor.process(trigger, person_state)` accepts any of the following inputs: a raw string, a dictionary payload, or a structured event object. The method must normalize these into one internal representation before feature extraction. For the first implementation, the accepted types are: string, dictionary, or structured object with fields such as `text`, `event_type`, `properties`, and `metadata`.
3. Perception processing: `Perceptor.process(trigger, person_state)` extracts a structured `Perception` object with observations and per-observation confidence.
4. Appraisal: `Appraiser.evaluate(perception, person_state)` produces one or more `AppraisalFrame` objects with dimension scores and links to supporting perceptions.
5. Expectations: `ExpectationsGenerator.update(appraisals, person_state)` produces `Expectations` predictions with probabilities and supporting evidence.
6. EFMSOMB update (optional): appraisal may recommend incremental EFMSOMB adjustments (e.g., temporary `emotion` candidate suggestions), but these must be added to `PersonState` only via an explicit step (and can be flagged as `suggested_emotion` rather than automatically written).
7. StateInferenceEngine.infer(person_state): reads `person_state.appraisal` + `person_state.expectations` + EFMSOMB fields and returns `StateInferenceResult`. The inference engine remains the final decider of state labels and must preserve manual state.
8. Proposal generation systems read `person_state.appraisal` and `person_state.expectations` to produce `BehavioralTendency` objects (backwards-compatible: if appraisal/expectation empty, they fall back to prior heuristics).
9. State modulation, SystemMemory, Competition, Arbitration, Decision follow as before.

Trigger normalization boundary
------------------------------
Decision: `Perceptor.process(trigger, person_state)` accepts all of the following inputs:
- string
- dictionary
- structured event object
- any combination of the above via a single normalized internal event form

This is the right boundary because the raw trigger may arrive in multiple sources (transcript, sensor, user report, or system event), but the extraction logic should not fork into three different code paths. The normalization step converts all accepted forms into a single internal event shape with at least:
- `event_type`
- `text` or equivalent content field
- `properties` dictionary
- `metadata` dictionary

The normalization boundary is where type checking and safety rules live; the downstream extraction layer only sees one normalized event representation. This keeps the Perception stage deterministic and explainable while preserving flexibility for external input types.

Insufficient-data policy
------------------------
The design chooses a single, deterministic policy across all three layers:
- The result object is still created and returned.
- `confidence` is set to `0.0`.
- `insufficient_data` is explicitly set to `True`.
- `observations`, `frames`, or `predictions` are empty as appropriate.

This is the best fit because it preserves an explicit status and a numeric confidence value without overloading the object with ambiguous placeholder data. It is also consistent with the existing state inference contract in `StateInferenceResult`, where insufficient data is represented as an explicit status and not as a guessed semantic label.

A perception that is insufficient is therefore represented as:
- empty observation list
- confidence 0.0
- insufficient_data = True

This is the same pattern used for appraisal and expectations: empty result set + numeric zero confidence + explicit insufficient-data flag.

Boundaries (exact)
------------------
- Perception vs Appraisal: Perception = raw facts about the observable world; Appraisal = interpretation of those facts in terms of significance to the person. Perception objects must not contain labels such as "threat" or "hostile intent".
- Appraisal vs Emotion: Appraisal assigns dimensions and frames (e.g., threat with controllability=-0.8). Emotion determination (e.g., set `person_state.emotion='fear'`) is a downstream decision; Appraisal exposes the structured cues and evidence used by `StateInferenceEngine` to infer emotion/state.
- Expectations vs Goals: Expectations are short-term predictions about outcomes; Goals are longer-term desires/targets. Expectations may reference goals as supporting evidence but must not overwrite goals.
- Expectations vs State of Mind: Expectations are input features (predictive signals) for `StateInferenceEngine`, not synonyms for State of Mind.
- State of Mind vs Behavioral Tendency: State of Mind is a descriptive label inferred from appraisal/EFMSOMB; Behavioral Tendency is the generated pressure to act. State of Mind may modulate tendency strength but must not directly select actions.

Deterministic first-pass rule set (small, explainable)
----------------------------------------------------
Rules operate on Perception → Appraisal → Expectations. They are deterministic boolean or threshold rules producing frames and predictions with evidence strings.

Perception rules (examples):
- If trigger includes a spoken utterance AND transcript contains second-person accusatory phrases (e.g., "you never", "you always"), create Observation: {type: "utterance", value: text, normalized: None, confidence: parser_conf}
- If `voice_volume` sensor > threshold_high, create Observation with normalized ~0.9 and confidence scaled by sensor reliability.

Appraisal rules (examples):
- Threat frame rule: If observations include `utterance` with accusatory content OR `proximity:close` AND `voice_volume` high, then produce frame label="threat" with `valence=-0.8`, `social_threat=0.9`, `controllability=-0.5`, supporting_perceptions=[...], confidence = min(perception_confidences) × 0.9. Evidence: textual reason.
- Ambiguity frame rule: If perceptions include contradictory cues (e.g., calm words but high volume) or `awareness` < 0.3, add frame label="ambiguity" with `ambiguity=0.9`.
- Opportunity frame rule: If perception contains praise/offer keywords and `values` include "gain", produce frame "opportunity" with positive valence.

Expectations rules (examples):
- From Threat appraisal: map to predictions {"confrontation":0.6, "ignore":0.2, "apology":0.1} scaled by prior history (if `history` shows confrontations frequently increase `confrontation` probability).
- From Ambiguity appraisal: produce broader low-confidence predictions (e.g., equal probabilities across a small set).

Rules for coexistence and contradictions
----------------------------------------
- Multiple appraisal frames may be active; each frame carries its own confidence and evidence.
- Contradictions are represented by multiple frames with overlapping supporting perceptions and non-zero confidences (e.g., both "threat" and "ambiguity").
- A `contradiction_score` can be computed for the set of frames (optional) as normalized entropy over frame confidences; keep this for explainability but not required for first pass.

Insufficient information handling
--------------------------------
- If no meaningful `Perception` can be extracted (low confidence), `Perceptor` emits a valid but empty `Perception` object with `observations=[]`, `confidence=0.0`, and `insufficient_data=True`.
- `Appraiser` emits an empty `frames` list, `confidence=0.0`, and `insufficient_data=True`.
- `ExpectationsGenerator` emits an empty prediction list, `confidence=0.0`, and `insufficient_data=True`.
- `StateInferenceEngine` receives `insufficient_data` from inference if appraisal/expectations are empty and should preserve manual state if present.

Manual vs inferred data
------------------------
- Any `Perception`, `Appraisal`, or `Expectations` object can be manually set (`manual=true`). Manual objects have a higher authority flag and `StateInferenceEngine` should prefer manual_state over inferred ones and report source="manual".
- Inference never overwrites a manual `person_state.state_of_mind`; manual data must be preserved.

Integration with `StateInferenceEngine` (exact)
---------------------------------------------
- `StateInferenceEngine.infer(person_state)` will be called after `Appraiser` and `ExpectationsGenerator` populate `person_state.appraisal` and `person_state.expectations`.
- The inference engine must be updated to prefer appraisal dimension scores and frames as evidence (not raw free-text emotion only). For now, it can read the existing `person_state` fields; the code change to `StateInferenceEngine` will be minimal (add lookups into `person_state.appraisal.frames` and `person_state.expectations.predictions`) but **we will not modify `StateInferenceEngine` now** — this design specifies the contract so the change can be small, and will be implemented after approval.
- `StateInferenceResult.evidence` should include appraisal and expectation provenance records (frame IDs, prediction IDs) for traceability.

DecisionEngine changes required (minimal)
----------------------------------------
- Add a pre-proposal hook in `DecisionEngine.decide()` to call the Perception→Appraisal→Expectations pipeline and populate `PersonState.perception`, `.appraisal`, `.expectations`.
- Proposal modules (goal/reactive/habitual) should read `person_state.appraisal`/`expectations` if present; otherwise fall back to current logic. This is additive and backward-compatible.
- `StateModulator`, `CompetitionEngine`, and `arbitration` require no change.

Representation of multiple items (coexistence)
--------------------------------------------
- `person_state.perception` holds a list of `Perception` objects with unique IDs.
- `person_state.appraisal.frames` holds a list of AppraisalFrame objects; frames include `confidence` and `evidence` so consumers can weigh them.
- `person_state.expectations.predictions` holds multiple predictions; their probabilities provide relative weights for expectation strength but are not normalized unless explicitly requested.

Contradiction representation
----------------------------
- Contradictory appraisals are represented as multiple frames with non-zero confidences and overlapping evidence. A `conflicts` array may be added with short textual descriptions generated by the Appraiser (e.g., "utterance calming but volume high").

What to do when information is insufficient
------------------------------------------
- Appraiser returns empty frames, Expectations empty, and a `insufficient_data` flag. `StateInferenceEngine` returns `source='insufficient-data'` and `confidence='unknown'`. Proposals fall back to current EFMSOMB-driven heuristics.

Manual vs inferred data rules
----------------------------
- Manual inputs are allowed at all stages (e.g., operator sets `person_state.appraisal` manually); modules must mark `manual=true` and include `evidence` stating the manual override.
- `StateInferenceEngine` treats manual appraisal/expectations as high-confidence evidence but still preserves `person_state.state_of_mind` when manually assigned.

Examples (5 concrete scenarios)
-------------------------------
Example 1 — Conflict (verbal attack)
- External event: transcript: "You always screw things up!"; voice volume high; proximity close.
- Perception:
  - Observation 1: {type:"utterance", value:"You always screw things up!", confidence:0.95}
  - Observation 2: {type:"voice_volume", value:"high", normalized:0.9, confidence:0.9}
  - Observation 3: {type:"proximity", value:"close", normalized:0.8, confidence:0.8}
- Appraisal frames:
  - Frame A: label="threat", dimension_scores:{valence:-0.9, social_threat:0.95, controllability:-0.4}, supporting_perceptions:[obs1,obs2,obs3], confidence:0.86, evidence:[...]
  - Frame B: label="ambiguity", dimension_scores:{ambiguity:0.4}, supporting_perceptions:[obs1], confidence:0.3, evidence:[...]
- Expectations:
  - Prediction 1: {outcome_label:"confrontation", probability:0.7, supporting_appraisals:[Frame A], evidence:[...]} 
  - Prediction 2: {outcome_label:"ignore", probability:0.2, supporting_appraisals:[Frame B], evidence:[...]}
- State of Mind implication: strong input to `StateInferenceEngine` for 'threatened'/'defensive' labels; evidence points to social threat and low controllability.

Example 2 — Opportunity (offer)
- External event: "I can help you with that"; calm tone; offer gesture.
- Perception: utterance (positive), gesture (offer), volume normal.
- Appraisal frame: label="opportunity", valence:0.8, goal_relevance:0.7, controllability:0.6, confidence:0.8
- Expectations: {"assistance":0.7, "no_action_needed":0.2}
- State implication: supports calm/confident inference and increases goal-directed tendency toward reciprocity/cooperation.

Example 3 — Uncertainty (ambiguous info)
- External event: fragmented message, mixed signals, low awareness.
- Perception: partial utterance, inconsistent volume, missing context.
- Appraisal: frame="ambiguity", ambiguity:0.9, confidence:0.5
- Expectations: low-confidence spread across outcomes (confrontation:0.25, ignore:0.25, clarify:0.25)
- State implication: supports `confused` inference; modulators may lower confidence of strong reactive proposals.

Example 4 — Social rejection
- External event: explicit exclusion phrase "we don't want you here"; multiple witnesses
- Perception: utterance, multiple sources, corroboration
- Appraisal: label="social_threat", valence:-0.95, intentionality:0.9, social_threat:0.95
- Expectations: {"withdraw":0.6, "respond":0.3}
- State implication: favors `threatened`/`defensive` labels; increases strength of reactive tendencies but modulated by perceived control.

Example 5 — Neutral situation
- External event: small procedural comment "please pass the salt"
- Perception: utterance, low volume
- Appraisal: empty or label="irrelevant" with low valence magnitude
- Expectations: empty or low-confidence predictions
- State implication: insufficient to change State of Mind; proposals driven by baseline goals/personality/habits.

Acceptance criteria for first implementation
-------------------------------------------
- The system must produce runtime dataclass objects for `Perception`, `Appraisal`, and `Expectations` with required fields for representative triggers in tests.
- `StateInferenceEngine.infer()` must accept appraisal and expectations evidence and include them in `StateInferenceResult.evidence` (this will be a minor change after design approval).
- Decision outcomes must remain deterministic and backward-compatible when appraisal/expectations are not present.
- `Perceptor.process` must accept string, dictionary, or structured event input and normalize it to one internal event shape before extraction.
- `insufficient_data` must be explicit and consistent across all three layers.

Final API contract
------------------
Perceptor.process(trigger, person_state) -> Perception
- Accepts: string, dictionary, or structured event object.
- Normalizes the trigger to an internal event representation before extraction.
- Returns a `Perception` object with observations, provenance, confidence, and `insufficient_data` status.

Appraiser.evaluate(perception, person_state) -> Appraisal
- Accepts either a single `Perception` object or a sequence of `Perception` objects.
- Produces an `Appraisal` object with one or more `AppraisalFrame` records.
- Returns empty frames with `confidence=0.0` and `insufficient_data=True` if no meaningful interpretation exists.

ExpectationsGenerator.update(appraisals, person_state) -> Expectations
- Accepts either a single `Appraisal` object or a sequence of `Appraisal` objects.
- Produces an `Expectations` object with probability-based predictions and provenance.
- Returns empty predictions with `confidence=0.0` and `insufficient_data=True` when no meaningful expectation can be inferred.

Next steps (after approval)
---------------------------
1. Finalize the exact runtime object definitions for the three dataclass-based result types and nested items.
2. Implement a minimal, well-tested deterministic module that populates `PersonState.perception`, `.appraisal`, `.expectations` and add unit tests for the 5 scenarios above.
3. Add a small `DecisionEngine` pre-proposal hook that calls the pipeline; ensure proposal modules read appraisal/expectation when available.

Appendix: minimal JSON schema sketches
------------------------------------
Perception (sketch):
```
{
  "id": "p-20260813-0001",
  "timestamp": "2026-08-13T12:00:00Z",
  "source": "trigger",
  "observations": [ {"type":"utterance","value":"You never listen","confidence":0.95}, ... ],
  "confidence": 0.9,
  "manual": false
}
```

Appraisal frame (sketch):
```
{
  "id": "a-0001",
  "label": "threat",
  "dimension_scores": {"valence":-0.9, "social_threat":0.95, "controllability":-0.5},
  "supporting_perceptions": ["p-20260813-0001"],
  "evidence": [{"field":"utterance","value":"You never listen","source":"transcript","note":"accusatory phrase"}],
  "confidence": 0.86,
  "manual": false
}
```

Expectations (sketch):
```
{
  "id": "e-0001",
  "predictions": [ {"outcome_label":"confrontation","probability":0.7}, {"outcome_label":"ignore","probability":0.2} ],
  "confidence": 0.75,
  "manual": false
}
```

End of document.
