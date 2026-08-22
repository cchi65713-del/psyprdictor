# State of Mind Model for PsyPredictor

## Formal definition (revised)

State of Mind is the person's current psychological operating mode: the way affect, appraisal, motivation, attention, and interpretation are organized in service of perception and behavior. Critically, State of Mind is defined as an operating mode whose duration is a property of the state, not its definition. In other words, a State of Mind can appear suddenly (emergent) or be sustained over time; both are the same kind of entity with different temporal characteristics.

Important constraint (clarification): State of Mind must NOT be modeled primarily as a long-term or sustained condition. It must be able to represent rapid, event-driven emergent modes that can be transient, while also supporting persistence when maintenance factors are present.

State of Mind therefore:
- Summarizes how the agent is currently configured to interpret salience, threat, agency, effort, social meaning, and expected outcomes.
- Is evidence-backed and explainable: each active state exposes its triggers, supporting evidence, onset, confidence, and temporal provenance.
- Is multi-dimensional and multi-state: multiple states can coexist with different intensities and confidences.
- Has temporal properties (onset, duration, persistence, decay) but these are properties of a state instance rather than part of the definition of different state classes.

State of Mind is NOT:
- a raw EFMSOMB signal (emotion/feeling/mood)
- a personality trait or long-term disposition (these are priors)
- a habit or memory record (these can reinforce states)
- an action selector (it modulates tendencies; competition/arbitration selects actions)

The same underlying configuration can be instantiated as a rapid/emergent state or as a sustained mode depending on triggers and maintaining factors.

---

## Architectural boundaries

State of Mind belongs in the internal interpretation layer between appraisal/expectations and behavioral tendencies.

It sits downstream of perception, appraisal, and expectations, and upstream of behavioral tendency generation and competition. It is not a substitute for any of the following:

- EFMSOMB: affective and physiological signal layer
- needs: motivational pressure
- goals: explicit desired outcomes
- beliefs: interpretive priors
- values: evaluative standards
- personality: trait-like baseline tendencies
- history/experience: accumulated memory and learning
- action selection: competition and arbitration

These components influence State of Mind, but they remain separate architectural objects with separate roles.

The architecture should therefore treat State of Mind as a dynamic summary of the current psychological mode, not as a catch-all bucket for everything inside the person.

---

## Temporal model

State of Mind should be modeled as a time-bounded psychological configuration.

Each state instance should have a temporal envelope:
- onset time
- last update time
- current duration
- persistence status
- decay or fade profile
- evidence time window
- source of initiation

The system must distinguish at least three time scales:

1. Momentary condition
   - seconds to minutes
   - examples: suddenly angry, briefly confused, momentarily excited

2. Sustained State of Mind
   - minutes to weeks
   - examples: focused for multiple days, persistently defensive, mentally withdrawn over a period

3. Long-term disposition/pattern
   - weeks to years
   - examples: habitually cautious, naturally persistent, tends to become focused when goals matter

The same underlying dimension can exist across all three scales. For example, focus may be:
- a brief spike in attention,
- a sustained mode during a project,
- or a long-term tendency toward goal pursuit.

These are not identical states. They are different temporal instantiations of related psychological structure.

---

## Runtime structure (proposed)

The runtime representation must treat each active State of Mind as an instance with explicit fields. Minimal, deterministic object shape:

```python
StateInstance = {
   "id": str,                    # unique instance id
   "name": Optional[str],        # optional derived label (e.g., "focused")
   "dimensions": {               # optional numeric dimensions
      "threat": 0.0,
      "uncertainty": 0.0,
      "agency": 0.0,
      ...
   },
   "intensity": 0.0,             # normalized [0..1]
   "confidence": 0.0,            # explainability/confidence [0..1]
   "onset": "ISO8601",         # when the state began
   "last_update": "ISO8601",   # most recent evidence timestamp
   "duration": "PTnS or seconds",# computed or reported duration
   "persistence": "brief|sustained|persistent", # convenience tag
   "decay_rate": 0.0,            # rate used for decay step
   "triggers": [                 # list of trigger records
      {"type": "appraisal|event|memory", "id": "...", "timestamp": "..."}
   ],
   "maintaining_factors": ["goal:X", "rule:avoid"] ,
   "origin": {                   # origin provenance
      "cause_type": "emotion|event|goal|memory",
      "cause_reference": "...",
      "cause_timestamp": "...",
   },
   "manual": False,              # explicit override marker
   "reinforced": False,          # whether repeated events upgraded persistence
   "evidence": [                 # detailed evidence records
      {"source": "appraisal", "signal": "threat", "value": 0.8, "confidence": 0.7, "timestamp": "..."}
   ]
}
```

Operational functions (deterministic rules):
- `create_state_from_trigger(trigger, appraisal, efmsomb)` — create emergent StateInstance with `onset==now` and initial evidence.
- `update_state_with_evidence(state, new_evidence)` — append evidence, update intensity/confidence, set `last_update`.
- `evaluate_persistence(state)` — determine `persistence` and `reinforced` by checking maintaining_factors, evidence continuity, and repetition counts.
- `decay_step(state, elapsed_seconds)` — reduce intensity based on `decay_rate` and evidence staleness; mark expired when below threshold.
- `suspend_or_reinforce(state, memory, personality)` — consult priors to bias persistence but only as priors, not as replacement for evidence.
- `derive_labels(state)` — derive short human-friendly labels deterministically from dimensions (kept separate from canonical state instance).

State list container in `PersonState`:

```python
person_state.states = {
   "active": [StateInstance, ...],
   "recent": [StateInstance, ...],
   "baseline": {"dimensions": {...}},
}
```

`baseline` is a separate summary of the person's normal operating mode (a prior), used for comparison and recovery.

---

## State dimensions

State of Mind should be represented as a set of dimensions rather than a single label. A minimal version should include the following dimensions, even if some are initially latent rather than fully numeric.

Core dimensions:
- threat sensitivity
- uncertainty / confusion
- agency / confidence
- defensiveness
- focus / goal orientation
- social openness / withdrawal
- effort / activation
- self-regulation / control
- urgency / time pressure
- coherence / stability

These dimensions are purposefully not the same as raw EFMSOMB values. They represent how the person is currently configured to interpret and respond.

A minimal implementation can start with a dict-like set of active states and later add weighted dimensions. The first-pass object should preserve the possibility of attaching a scalar intensity and confidence value to each dimension or state.

---

## Persistence model

A state becomes a sustained State of Mind when it remains active long enough to matter as a stable mode of operation.

The model should distinguish:
- active now
- recently active
- decaying
- expired
- manually overridden

Persistence should be represented by a combination of:
- recurrence or continuity of evidence,
- time since onset,
- rate of change in intensity,
- number of supporting inputs,
- stability across recent events.

The following should not be encoded as a hard-coded single threshold, but the system needs a threshold concept for determinism:
- temporary state: duration below short-window threshold
- sustained state: duration above the sustained-window threshold
- persistent mode: duration above the persistent-window threshold and significant stability

A practical deterministic first-pass can use simple windows such as:
- brief: < 10 minutes
- sustained: 10 minutes to 7 days
- persistent: > 7 days
- disposition: long-term baseline over repeated episodes

The exact thresholds should be configuration-level and not hard-coded into action selection.

---

## Intensity model

Every active state should have an intensity value in a bounded range, ideally $[0, 1]$ or a normalized scalar with a defined interpretation.

Intensity answers: how strongly is this state currently active?

Examples:
- mildly distracted: 0.35
- strongly threatened: 0.8
- deeply focused: 0.9
- temporarily confused: 0.55

Intensity should be dynamic and should degrade or strengthen according to:
- recency of supportive evidence,
- repeat exposure to the same trigger,
- physical and energetic state,
- competing evidence,
- manual override status.

Important rule: intensity does not imply action choice. It modifies modulation strength and explanatory confidence, not the arbitration result directly.

---

## Multi-state representation

State of Mind should allow multiple simultaneous states to coexist without forcing a single winner.

A minimal representation could be:

```python
state_of_mind = {
    "focused": {"active": True, "intensity": 0.82, "confidence": 0.87, "duration": "14 days"},
    "defensive": {"active": True, "intensity": 0.58, "confidence": 0.63, "duration": "3 hours"},
    "confident": {"active": False, "intensity": 0.14, "confidence": 0.44}
}
```

This is more expressive than a raw string or simple boolean dictionary, while still fitting the current dict-based architecture.

The representation should support:
- active states
- inactive but recently relevant states
- primary state
- secondary states
- contradiction tracking
- decayed states
- manual overrides

A deterministic architecture can still expose a simplified summary:
- `primary_state`
- `secondary_states`
- `state_confidence`
- `state_summary`
- `manual_state`
- `inferred_states`

The key is that multi-state coexistence is allowed without pretending there is only one state at a time.

---

## Sudden (emergent) vs Sustained states — how they differ

- Sudden/Emergent states:
   - Creation: triggered immediately by an Event → Perception → Appraisal → EFMSOMB cascade.
   - Onset: near-instantaneous; `onset == now` when created.
   - Evidence: often dominated by appraisal and EFMSOMB signals tied to the trigger.
   - Maintenance: usually decays rapidly unless maintaining factors (goals, repeated triggers, strong memories, context) are present.
   - Typical roles: transient urgency, acute focus, immediate defensiveness, shock, embarrassment-driven motivation.

- Sustained states:
   - Creation: may start as an emergent state but becomes sustained when maintaining factors persist or reinforcement occurs.
   - Onset: may have same initial onset, but `duration` and `reinforced` become meaningful over time.
   - Evidence: supported by repeated appraisals, consistent behavior, memory retrieval, ongoing goals or environmental support.
   - Maintenance: persistence is computed from evidence continuity, decay rates, and priors.

Key architectural note: these are the same class of object; difference is the state instance's temporal/maintenance attributes.

---

## Returning toward baseline (decay and recovery)

Mechanics:
- Each StateInstance carries a `decay_rate` and `last_update` timestamp.
- Periodic `decay_step` reduces `intensity` as evidence becomes stale: `intensity := intensity * exp(-decay_rate * elapsed)` (or a deterministic step rule).
- If `intensity` drops below a low threshold (configurable), the instance is moved from `active` to `recent` or removed entirely.
- `baseline` summary in `PersonState` provides a target toward which transient states recover. Recovery can be faster when evidence contradicts the state and when baseline priors are strong.
- Manual overrides set `manual=True` and prevent automatic removal until an explicit release or time-limited override expires.

Practical deterministic rules (first pass):
- decay window: evaluate every decision cycle (or fixed tick), reduce intensity if no supporting evidence in `window_seconds`.
- immediate suppression: strong contradicting evidence (high-confidence appraisal/opportunity) can sharply reduce intensity.

---

## Reinforcement: how repeated experiences convert temporary states into longer-term patterns

Process outline:
1. Emergent state instances record their triggers and evidence.
2. Each time the same or similar trigger (or evidence supporting same dimensions) occurs, `update_state_with_evidence` increments a `recurrence_count` and updates timestamps.
3. `evaluate_persistence` checks: if `recurrence_count >= recurrence_threshold` within `window_seconds` or if maintaining_factors persist, mark `reinforced=True` and increase `persistence` and reduce `decay_rate`.
4. When `reinforced` becomes true repeatedly across many episodes, the system can emit a long-term disposition signal to learning modules (PatternLearner / SystemMemory) so that disposition is recorded as a prior (not as the new state itself).

Important: reinforcement never overwrites immediate evidence. Long-term pattern storage is an additional artifact recorded in Memory/PersonProfile, not the active StateInstance container.

---

## What must be remembered about the origin of a state

For explainability and future reasoning the StateInstance must keep:
- `triggers[]`: event/appraisal IDs and timestamps that initiated or updated the state.
- `origin.cause_type` and `origin.cause_reference`: whether the cause was an `emotion`, an external `event`, a `goal` change, `pain`, or a retrieved `memory` and a reference to that object.
- `origin.cause_timestamp`: when the trigger occurred.
- `evidence[]`: time-stamped records of appraisal/EFMSOMB signals and expectation predictions that supported the state.
- `recurrence_count` and `first_onset`: how often the state has reappeared and when it first appeared.
- `manual` flag and `manual_override_reason` if a user/system explicitly set it.

This provenance allows the system to answer: "What caused this state?", "Is the cause still present?", "Was the cause remembered or reactivated?", and "Has this state been reinforced by repetition?"

---

## What remains outside State of Mind

Keep these concepts separate and out of the StateInstance object:
- EFMSOMB raw signals (emotion/feeling/mood/arousal) — they are evidence sources but not collapsed into State of Mind.
- Personality and long-term dispositions — stored as priors in `PersonProfile` / `SystemMemory` / PatternLearner.
- Habits and learned action mappings — they can reinforce states but remain in Learning modules and Habit structures.
- Memory entries — Memory can be referenced from `origin` but complete memory stores remain in `Memory` modules.
- Action selection logic (Competition, Arbitration) — StateModulator and other modulators should only modify tendency strengths.

---

## Deterministic first-pass checklist (delta from previous list)

Additions required by the clarification:
1. Treat `onset` and `triggers` as first-class provenance recorded on creation.
2. Treat `duration` as a property of the StateInstance, not a defining class-level distinction.
3. Provide deterministic `decay_step` and `evaluate_persistence` functions to move states between `active` and `recent` buckets.
4. Provide `recurrence_count` and simple thresholds for `reinforced` to signal Long-term Pattern emission (to learning modules).
5. Ensure `baseline` remains a separate target object or summary for recovery logic.

These keep the implementation deterministic and reviewable before any runtime changes are applied.

---

## Derived-label mechanism

Derived labels are not the state itself; they are shorthand labels produced from the underlying dimensions.

Examples:
- focused = high goal orientation + moderate attention + low overwhelm
- threatened = high threat sensitivity + elevated uncertainty + reduced agency
- defensive = high defensiveness + threat sensitivity + social withdrawal tendency
- confused = high uncertainty + reduced coherence + low confidence
- confident = high agency + low threat + high coherence

The derived label mechanism must be:
- explainable,
- deterministic,
- traceable to dimension values,
- and never treated as the only ground truth.

Each label should be generated from the multidimensional state, not assigned ad hoc by a single input. A label can be an interpretation of multiple dimensions rather than a direct variable.

This allows one underlying state to produce multiple labels at different levels of specificity:
- underlying configuration: goal-oriented + threat-sensitive + internally regulated
- derived labels: focused, guarded, determined, tense

These labels exist to support readability and interoperability, not to replace the underlying configuration.

---

## Interaction with EFMSOMB

EFMSOMB is the short-timescale affective and physiological layer. It provides immediate emotional evidence and arousal-like signals.

State of Mind should receive influence from EFMSOMB, but the model should not be reduced to EFMSOMB.

Examples:
- anger or fear may increase threat sensitivity
- calm or confidence may support agency and coherence
- fatigue or elevated arousal may reduce focus or increase overwhelm
- mood may sustain a state beyond a single event

Recommended boundary:
- EFMSOMB contributes evidence and short-term activation signals
- State of Mind integrates these into a more stable interpretation
- EFMSOMB remains separate from the orientation of the current psychological mode

In other words, EFMSOMB describes how the person is currently feeling; State of Mind describes how that feeling is being organized into a current mode of action.

---

## Interaction with Energy/Physiology

Energy and physiology should influence both intensity and persistence, but should not define the whole State of Mind.

Examples:
- depleted energy may increase confusion, withdrawal, or lower focus
- elevated arousal may increase urgency and threat salience
- recovery may permit stronger engagement and resilience
- illness, pain, or fatigue may shorten persistence and reduce confidence

Energy/physiology should be treated as context modifiers of State of Mind, not as a competing representation of it.

The model should allow physiological state to reduce the stability of a state or increase the decay rate of a sustained mode.

---

## Interaction with Needs/Goals

Needs and goals are important because they determine the motivational relevance of the current state.

Examples:
- a person who is highly focused on an important goal may sustain a goal-oriented state for days or weeks
- unmet needs can increase urgency or defensiveness
- social needs can increase withdrawal or social vigilance
- safety needs can increase threat sensitivity and defensive posture

Needs and goals should influence the state by increasing or decreasing salience, relevance, and persistence, but they do not become the state itself.

A sustained focus state is not just “goal present.” It reflects the pattern of how the person is currently operating in relation to that goal under current constraints.

---

## Interaction with Beliefs/Values

Beliefs and values are slower-moving interpretive filters and normative anchors.

Examples:
- a person who believes social evaluation is dangerous may be more likely to sustain defensiveness
- a person who values mastery may sustain focus under challenge
- values can increase coherence and persistence in a state by making it normatively meaningful

Beliefs and values should operate as priors, not as direct state labels.

They influence:
- which states are likely to be activated,
- how strongly a state persists,
- what the person interprets as relevant,
- which labels are considered appropriate or trustworthy.

These should remain distinct from the current State of Mind snapshot.

---

## Interaction with Personality/History

Personality and history should be treated as long-run predispositions that shape the probability and stability of certain states.

Examples:
- habitually cautious personality increases likelihood of defensive states
- persistent temperament increases sustained focus under challenge
- previous trauma may increase threat sensitivity in similar circumstances
- learning history may stabilize confidence or uncertainty patterns

These are not the same as current State of Mind; they are the base conditions that increase the likelihood of sustained states emerging.

The recommended architecture is:
- personality/history influence priors,
- current State of Mind is the active configuration,
- the relation is causal but not identical.

---

## Interaction with Perception/Appraisal/Expectations

This is the primary trigger path for State of Mind updates.

Perception answers: what is being noticed?
Appraisal answers: what does it mean?
Expectations answer: what is likely to happen next?

These feed into the current State of Mind by changing dimension values such as threat, uncertainty, agency, urgency, or focus.

Examples:
- a threat appraisal can increase defensiveness and threat sensitivity
- a blocked expectation can increase confusion or frustration
- a high-confidence appraisal can increase calm and agency
- a repeated pattern of blocked effort can sustain a withdrawn or defensive mode

State of Mind is therefore not independent of the interpretation stack. It is the integrative layer that turns interpretation into an operational mode.

---

## Interaction with BehavioralTendency and StateModulator

BehavioralTendency generation should remain independent of action selection. State of Mind should influence the tendency strength before competition, not choose or replace actions.

This is the key boundary:
- State of Mind modulates tendency intensity
- Competition resolves among existing candidates
- Arbitration chooses the final action

The existing deterministic architecture can evolve without breaking competition or arbitration by treating State of Mind as:
- a source of modulation metadata,
- an explanation layer,
- and a persistence-aware state summary.

StateModulator should remain a transparent, deterministic strength modifier. It should not directly generate actions or replace the state-label system in one step.

The model should preserve the existing principle that state is a modulation signal, not a decision function.

---

## Manual-state preservation

The architecture must preserve user- or system-supplied state-of-mind values without allowing them to be silently overwritten by inferred state.

This means the model should separately record:
- `manual_state`
- `manual_state_source`
- `inferred_states`
- `primary_inferred_state`
- `state_conflicts`
- `manual_override_reason`

Manual values should be preserved as a valid source of current state, but the system should also expose whether the inferred state agrees or disagrees with the manual input.

A deterministic first pass should treat manual values as authoritative when explicitly set, while still logging evidence and disagreement.

---

## Provenance/evidence design

Every state or derived label should expose evidence and temporal provenance.

A state record should contain references to:
- the source signal
- the evidence type
- the time it was observed
- the confidence in the signal
- the signal strength
- whether it was manual, inferred, or learned context

Example evidence record:

```python
{
  "type": "appraisal",
  "signal": "threat_assessment",
  "value": 0.82,
  "confidence": 0.74,
  "timestamp": "2026-08-14T12:10:00Z",
  "source": "perception_appraisal_expectations"
}
```

This is crucial for explainability and for detecting when a state is being sustained by weak or stale evidence.

The provenance layer should also record temporal history so the system can answer:
- how long the state has been active,
- which events are driving it,
- whether it is stable or decaying,
- whether the state is manual, inferred, or hybrid.

---

## Deterministic first-pass rules

Before implementing, the model should agree on a limited set of deterministic rules.

1. State of Mind is temporal and can persist.
2. Momentary emotion labels do not equal sustained State of Mind.
3. The same base dimension can exist across multiple time scales.
4. Multiple states may be active at once.
5. State labels are derived from underlying dimensions.
6. Persistence is based on duration, continuity, and evidence stability.
7. Intensity is separate from duration.
8. Manual state values are preserved and logged.
9. Inference is allowed to disagree with manual input and should log the conflict.
10. State Modulator only changes tendency strength; it does not select actions.
11. Competition and arbitration remain downstream of state modulation.
12. Personality/history are priors, not the current state itself.

These rules anchor the architecture while leaving room for later weighting and richer temporal modeling.

---

## Examples

### Example 1: angry right now
- trigger: unexpected insult
- appraisal: threatened or disrespected
- emotion: anger
- state dimension: threat sensitivity rises, agency may fall
- duration: seconds to minutes
- result: a brief emotional state with short persistence

This is a momentary condition, not necessarily a sustained State of Mind.

### Example 2: anxious throughout the day
- repeated uncertainty and low control
- moderate threat sensitivity persisted across several hours
- intensity remains stable but not extreme
- derived labels: anxious, guarded, tense

This is a sustained current state, not merely a single incident.

### Example 3: deeply focused on a goal for weeks
- repeated goal salience
- strong attention, high agency, low distraction
- persistent support from goals and previous success
- state persists across many decision cycles

This is a sustained State of Mind or persistent mode, not a single emotion.

### Example 4: generally becomes focused when pursuing important goals
- long-term pattern of state recurrence
- not the same as a current state snapshot
- better treated as a disposition or learned pattern

This belongs with personality/history or learned habit structure, though it can influence the current state.

---

## Edge cases

1. Contradictory states
   - Example: calm while defensive
   - Resolution: keep both active and record conflict; allow a primary label without deleting secondary evidence.

2. Persistent state with decreasing confidence
   - Example: focus remains active but evidence has weakened
   - Resolution: state remains active but decays and may become low-confidence.

3. Manual override conflicting with inferred state
   - Example: user sets “confident” while system infers “threatened”
   - Resolution: preserve both, mark discrepancy, and allow explanation.

4. Multiple triggers in rapid succession
   - Example: several events in one minute
   - Resolution: aggregate evidence over a short window and avoid overreacting to one signal.

5. State with no strong label
   - Example: low intensity, mixed evidence, uncertain orientation
   - Resolution: keep it active but labeled as ambiguous or low-confidence.

6. Long-term state that no longer fits current context
   - Example: a maintained defensive posture remains after the trigger disappears
   - Resolution: decay by temporal and contextual evidence rather than immediate removal.

7. State persists beyond a goal
   - Example: focus remains after the goal is complete
   - Resolution: maintain as a historical state but reduce its active relevance when the target no longer matters.

---

## Focused test plan

The specification should be validated with a test plan that does not require modifying the current implementation prematurely.

1. Temporary vs sustained distinction
   - verify a single angry response does not become a sustained mode without continuity
   - verify a multi-day focus pattern is distinguished from a brief attention spike

2. Manual preservation
   - verify explicit manual values are retained in state metadata
   - verify inferred states are logged separately

3. Multi-state coexistence
   - verify a state can be both defensive and focused in the same window
   - verify one primary label does not erase the secondary one

4. Decay and persistence
   - verify a state loses intensity when evidence disappears
   - verify a sustained state continues when supporting conditions remain

5. Evidence provenance
   - verify each state can answer which inputs supported it
   - verify dates and confidence are captured

6. Modulation boundary
   - verify StateModulator changes tendency strength without replacing competition or arbitration
   - verify action choice remains downstream

7. Long-term dispositions
   - verify personality/history can raise the probability of a sustained state without being treated as the current state itself

8. Deterministic compatibility
   - verify the existing architecture still produces competition results without expectation of direct state selection

---

## Migration strategy from the current label-based implementation

The migration should be incremental and backwards-compatible.

1. Keep the current dict-like `state_of_mind` field as the compatibility layer.
2. Treat the current labels as a simplified view of a richer structure.
3. Add a temporal state object or metadata wrapper, but do not force immediate replacement of existing state dictionaries.
4. Preserve current label names for deterministic compatibility, including `defensive`, `threatened`, `confused`, `focused`, `confident`, and others already used by the system.
5. Add a secondary representation for:
   - `state_name`
   - `primary_state`
   - `secondary_states`
   - `intensity`
   - `confidence`
   - `onset`
   - `duration`
   - `persistence`
   - `evidence`
   - `manual_status`
6. Keep `StateModulator` working against the current labels while the richer model is introduced beneath them.
7. Ensure Competition and Arbitration remain unchanged in function: they still select among tendencies and actions, while state only modulates the strengths.
8. Update inference and reporting layers before changing behavioral logic to ensure the state architecture becomes explainable and auditable.

This preserves the deterministic baseline while creating a path toward a fuller temporal State of Mind model.

---

## Design conclusion

The smallest coherent model is: a temporally-aware, multi-dimensional, multi-state representation that distinguishes:
- immediate conditions,
- sustained current states,
- and longer-term dispositions.

This model can represent both:
- “the person is angry right now”
- and “the person has been deeply focused on this goal for the last two months”

without confusing a short-lived emotion, a continuing internal mode, and a long-run psychological tendency.

The architecture should therefore treat State of Mind as a current configuration with evidence, duration, intensity, and temporal provenance, while retaining distinct roles for EFMSOMB, physiology, needs, goals, beliefs, values, personality, history, and expectation-based interpretation.

This keeps the current deterministic pipeline stable while giving PsyPredictor a principled path toward a richer and more realistic psychological model.

The architecture is now defined at the right boundary: State of Mind is a temporally-aware operating mode that summarizes current psychological configuration, not a direct action selector or a replacement for EFMSOMB, beliefs, goals, personality, or memory. The implementation work should continue only after that boundary is accepted and preserved.
