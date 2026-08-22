# State of Mind Runtime API (Deterministic Design)

Purpose: define a minimal, deterministic runtime API and data model that implements the revised State of Mind architecture. This document is design-only — no Python changes are made here.

**Principles**
- A `StateInstance` represents the current psychological configuration (what the person is configured to interpret and do) and includes provenance and evidence. Temporal aspects (duration, persistence, decay, reinforcement) are properties of the instance, not the state's definition.
- Multiple `StateInstance`s may be active concurrently.
- Deterministic, explicit functions operate on `StateInstance`s. No hidden probabilistic inference is required for the first pass.
- Manual overrides are authoritative and preserved.

---

**I. Runtime object structures**

- `EvidenceRecord` (single source entry)

```python
EvidenceRecord = {
    "id": str,               # unique id
    "source": str,           # 'appraisal'|'perception'|'efmsomb'|'expectation'|'memory'|'manual'
    "signal": str,           # e.g. 'threat', 'voice_volume', 'goal_change'
    "value": float|str|dict, # numeric or structured evidence
    "confidence": float,     # 0..1
    "timestamp": ISO8601_str,
    "ref": Optional[str],    # optional pointer to object in other module
}
```

- `StateInstance` (canonical runtime unit)

```python
StateInstance = {
    "id": str,                  # unique identifier
    "canonical_name": Optional[str], # optional derived label (e.g., 'focused')
    "dimensions": {             # numeric map; each 0..1
        "attention": 0.0,
        "goal_relevance": 0.0,
        "motivation": 0.0,
        "threat": 0.0,
        "arousal": 0.0,
        "agency": 0.0,
        "self_regulation": 0.0,
        ...
    },
    "intensity": 0.0,           # normalized (0..1), derived from dimensions
    "confidence": 0.0,          # 0..1 explainability/confidence
    "onset": ISO8601_str,
    "first_onset": ISO8601_str, # first time the same state appeared (for recurrences)
    "last_update": ISO8601_str,
    "duration_seconds": float,  # computed
    "decay_rate": float,        # property (not definition) used by decay_step
    "recurrence_count": int,
    "persistence_tag": "brief|sustained|persistent", # convenience
    "triggers": [               # list of EvidenceRecord ids or small refs
        EvidenceRecord, ...
    ],
    "origin": {                 # provenance of initial cause
        "cause_type": "emotion|event|goal|memory|physiology|manual",
        "cause_ref": Optional[str],
        "cause_timestamp": ISO8601_str,
    },
    "maintaining_factors": ["goal:save_money", "rule:avoid_shame"],
    "influenced_by": ["state_id", ...], # list of StateInstance ids that influenced this state
    "influences": ["state_id", ...],    # list of StateInstance ids this state influences
    "reinforced": False,        # property set by evaluate_persistence
    "manual": False,
    "manual_reason": Optional[str],
    "evidence": [EvidenceRecord, ...],
}
```

- `PersonState.states` container (placed inside `PersonState` but design-only here)

```python
PersonState.states = {
    "active": [StateInstance, ...],
    "recent": [StateInstance, ...],
    "baseline": {"dimensions": {...}, "last_update": ISO8601},
}
```

---

**II. Final API signatures (deterministic functions)**

Note: these are pure functions or methods on a `StateManager` and must not alter arbitration/competition behavior.

1. create_state_from_trigger(trigger, appraisal, efmsomb, person_state) -> StateInstance
- Purpose: create an emergent StateInstance given new trigger evidence.
- Behavior: builds dimensions from appraisal + efmsomb signals, sets `onset==now`, appends initial EvidenceRecord(s), sets `first_onset==onset`, `recurrence_count=1`, `last_update==onset`, `manual=False` unless forced.

2. update_state_with_evidence(state: StateInstance, evidence: EvidenceRecord) -> StateInstance
- Purpose: incorporate new evidence into an existing state.
- Behavior: append evidence, update `dimensions`, recompute `intensity` & `confidence`, set `last_update`, increment `recurrence_count` as appropriate.

3. merge_compatible_evidence(states: List[StateInstance], new_evidence: EvidenceRecord) -> List[StateInstance]
- Purpose: merge or route evidence to matching StateInstance(s). Does not collapse states into a single label; it attaches evidence to multiple matching states when appropriate.

4. create_or_update_from_trigger(trigger, person_state) -> (created_states, updated_states)
- Purpose: convenience function invoked when a trigger arrives. Calls `create_state_from_trigger` and attempts to match/merge into existing active states.

5. evaluate_persistence(state: StateInstance, person_state, system_memory) -> StateInstance
- Purpose: deterministically decide whether `reinforced` should be set and to adjust `decay_rate` and `persistence_tag` based on maintaining_factors, recurrence_count, and priors. If `reinforced` becomes True, reduce `decay_rate`.

6. decay_step(state: StateInstance, now_timestamp) -> StateInstance
- Purpose: reduce `intensity` as evidence ages. If intensity drops below `min_active_threshold`, move to `recent`.

7. return_toward_baseline(state: StateInstance, baseline, now_timestamp) -> StateInstance
- Purpose: deterministic function that, when insufficient evidence remains, reduces dimensions toward baseline dimensions over a fixed recovery time constant.

8. reinforce_state_to_memory(state: StateInstance, memory_manager) -> None
- Purpose: when `recurrence_count` crosses a threshold, create a Learning/Pattern event in Memory (not replace the state). Returns nothing but records external artifact.

9. derive_labels_from_dimensions(state: StateInstance) -> List[str]
- Purpose: deterministically map dimension thresholds and rules to human-friendly derived labels; does not replace canonical `dimensions`.

10. handle_manual_override(person_state, state_or_dimensions, reason) -> StateInstance
- Purpose: set `manual=True`, `manual_reason`, and treat as authoritative until cleared.

11. resolve_contradictions(states: List[StateInstance]) -> List[StateInstance]
- Purpose: produce an explainable conflict report (do not collapse states). Returns same states with `conflict_info` metadata appended.

12. propagate_influence(source_state: StateInstance, target_state: StateInstance, influence_map: Dict[str, float]) -> (StateInstance, StateInstance)
- Purpose: deterministically apply bounded dimensional influence from `source_state` to `target_state` without merging them. `influence_map` maps source dimensions to multipliers/weights that adjust the target's dimensions (e.g., `{"motivation": 0.2}` increases target motivation by `source.intensity * 0.2`). Records the relation by appending `source_state.id` to `target_state.influenced_by` and `target_state.id` to `source_state.influences`.


---

**III. State lifecycle**

1. Trigger arrival -> Perception -> Appraisal -> EFMSOMB.
2. `create_or_update_from_trigger` invoked.
   - It identifies which existing states are compatible (dimension overlap) and updates them; for unmatched evidence it creates new StateInstance(s).
3. While active, `update_state_with_evidence` increments `recurrence_count` and `evidence` records.
4. Each decision cycle or periodic tick, call `evaluate_persistence` and `decay_step`.
   - `evaluate_persistence` may set `reinforced=True` and lower `decay_rate`.
   - `decay_step` reduces `intensity` when evidence is stale.
5. If `intensity < removal_threshold`, move the state to `recent` and record `last_active`.
6. If `recurrence_count` surpasses `reinforcement_threshold`, call `reinforce_state_to_memory` to emit a learning event (do not convert the state into personality; instead, update Memory/Priors).

---

**IV. Dimension model and interaction rules**

Core numeric dimensions (first-pass minimal set):
- `attention` (0..1) — available focus on stimuli/task
- `goal_relevance` (0..1) — importance of current goal to the agent
- `motivation` (0..1) — drive to act toward goal
- `threat` (0..1) — appraisal of threat or risk
- `arousal` (0..1) — physiological activation
- `agency` (0..1) — perceived control/efficacy
- `self_regulation` (0..1) — ability to regulate impulses
- `coherence` (0..1) — internal consistency / confidence

Interaction rules (deterministic):
- `intensity := weighted_sum(dimensions, weights)` normalized into [0..1]. Weights chosen per label-derivation rules.
- `confidence` computed from evidence count and evidence average confidence.
- When two dimensions change antagonistically (e.g., high threat but high agency), both dimensions maintain values; derived labels reflect combinations rather than reducing either.

Label derivation examples (deterministic rules):
- Derived label `focused` if:
  - `attention >= 0.6` AND `goal_relevance >= 0.6` AND `motivation >= 0.5` AND `arousal <= 0.85`.
- Derived label `defensive` if:
  - `threat >= 0.6` AND (`arousal >= 0.5` OR `self_regulation <= 0.4`).
- Derived label `confused` if:
  - `coherence <= 0.3` AND `attention <= 0.4` AND `confidence <= 0.4`.

Derived labels are for readability and reporting only — they do not replace `dimensions` or `intensity`.

---

**V. Provenance model**

- Each StateInstance must keep `evidence[]` (EvidenceRecord) and `triggers[]` with cause reference.
- EvidenceRecord fields are defined above; they must include `timestamp`, `confidence`, and `ref` when referencing appraisal/expectation object IDs.
- The `origin` sub-object must state `cause_type`, `cause_ref`, and `cause_timestamp`.
- Provenance must answer: who/what triggered the state, when, which evidence sustained it, whether the original cause is still present, and what events changed it.

---

**VI. Deterministic first-pass rules**

Configurable constants (first-pass defaults):
- `EVIDENCE_STALE_WINDOW = 30` seconds (window after which single evidence begins to decay)
- `DECAY_EVAL_INTERVAL = decision_cycle_seconds` (e.g., per decision)
- `REINFORCEMENT_RECURRENCE_THRESHOLD = 3` occurrences within `REINFORCEMENT_WINDOW_SECONDS = 86400` (1 day)
- `MIN_ACTIVE_INTENSITY = 0.10` (below which state moves to `recent`)
- `PERSISTENCE_TAG_THRESHOLDS = {brief: <600s, sustained: 600..604800, persistent: >604800}`

Deterministic update rules:
- On new evidence, `update_state_with_evidence` recomputes `dimensions` and `intensity` immediately.
- `decay_step` reduces intensity per `intensity := intensity * exp(-decay_rate * elapsed_seconds)` or simple linear step if exponentials are undesired.
- `evaluate_persistence` sets `reinforced=True` if `recurrence_count >= threshold`; when `reinforced=True` reduce `decay_rate := decay_rate * 0.5`.
- `derive_labels_from_dimensions` is pure deterministic mapping.

Conflict handling:
- Do not collapse states. `resolve_contradictions` produces a `conflict_info` object containing types (`coexistence`, `opposition`, `support`) and a textual explanation. Arbitration is unaffected.

---

**VII. Test plan (deterministic unit tests)**

Minimal set of tests to validate API before implementation:
1. create_state_from_trigger: supply a mock appraisal/efmsomb -> expect StateInstance with onset==now, evidence added, intensity>0.
2. Sudden state decay: create emergent state with high intensity, run `decay_step` with no evidence -> intensity decreases and eventually moves to `recent`.
3. Reinforcement: apply matching evidence 3 times within window -> `recurrence_count` increments and `evaluate_persistence` sets `reinforced=True` and lowers `decay_rate`.
4. Multiple states: create two overlapping StateInstance (focused and defensive) -> both remain active and `resolve_contradictions` reports coexistence.
5. Return to baseline: with no evidence and weak maintaining_factors, call `return_toward_baseline` and confirm dimensions move toward baseline.
6. Manual override: call `handle_manual_override` and assert `manual=True` preserved until cleared.
7. Label derivation: set dimension vectors matching `focused` rule -> derived labels include `focused`.
8. Influence propagation: create `embarrassment` -> `motivation` influence mapping so that `embarrassment` evidence creates a `motivated` state via `propagate_influence`; verify `embarrassment` intensity can decay to zero while `motivated` intensity remains >0 and decays independently or is reinforced by separate evidence.

---

**VIII. Migration plan from current label-based StateModulator**

Goals: backward compatibility, minimal code churn, staged rollout.

Step 0: Do not change Python yet — design only.
Step 1: Add `PersonState.states` compatibility layer (read-only view) that mirrors current `state_of_mind` labels to `StateInstance` views for reporting.
Step 2: Keep `StateModulator` reading `person_state.state_of_mind` until API is implemented — mapping function `state_of_mind_label -> StateInstance.dimensions` provides compatibility mapping.
Step 3: Implement deterministic APIs in a `StateManager` module; tests validate API behavior.
Step 4: Gradually change `StateModulator` to read from `PersonState.states['active']` and prefer `dimensions/intensity` when available; keep fallback to label-based map.
Step 5: When stable, deprecate direct label writes to `person_state.state_of_mind`; continue to accept manual overrides into `PersonState.states`.

---

Status: API drafted. Waiting for approval to implement Python modules.
