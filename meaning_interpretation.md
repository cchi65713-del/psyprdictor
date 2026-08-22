# Meaning Attribution Layer — Architecture Specification

Status: draft

## Scope
This document specifies the Meaning Attribution Layer (MAL) to sit between
`Appraisal` and `StateManager` in the PsyPredictor pipeline. It is an
interpretive, non-decisional component: it converts appraisal/expectation
signals plus personal context into explicit, traceable meaning structures
(`MeaningFrame`s) that can be persisted, reinforced, and consumed by
`StateManager` to create richer internal StateInstances.

## Placement in pipeline
Perception → Appraisal → Meaning Attribution → StateManager → StateInference → StateModulation → Tendencies → Competition → Arbitration

## Principles & Constraints
- Non-decisional: MAL must not select or rank actions, nor directly alter
  Competition/Arbitration behavior.
- Provenance-preserving: every MeaningFrame records its source references
  (perception id, appraisal frame id, expectation/prediction ids, memory refs).
- Person-specific: interpretations must consider `person_state` (goals, values,
  personality, history) and current EFMSOMB signals but not deterministically
  force outcomes.
- Multi-interpretation: MAL must represent multiple simultaneous candidate
  meanings with confidence scores rather than picking one.
- Persistence hints: MAL can mark meaning as transient or candidate for longer
  persistence; persistence decisions are implemented by `StateManager`.

## Core data model: MeaningFrame
MeaningFrame: a single interpretive hypothesis about what an event means to
a person. Minimal required fields:

- `id: str` — unique identifier
- `timestamp: str` — ISO timestamp when frame was generated
- `source: str` — origin of the frame (e.g., `appraisal`, `expectation`, `memory`)
- `supporting_appraisals: List[str]` — appraisal frame ids used as support
- `supporting_expectations: List[str]` — expectation/prediction ids used as support
- `supporting_memory_refs: List[str]` — memory ids or refs consulted
- `interpretation: str` — compact label for the interpretation (e.g., `challenge`, `humiliation`, `opportunity`)
- `interpretation_alternatives: List[Tuple[str, float]]` — other candidate labels with confidence (label, score 0-1)
- `personal_relevance: float` — 0..1 scalar indicating significance to this person
- `affected_values: List[str]` — e.g., `['status','competence','security']`
- `activated_goals: List[str]` — goal ids or short keywords likely activated
- `motivation_direction: Optional[str]` — e.g., `approach`, `avoid`, `prove_self`
- `predicted_self_view_change: Optional[str]` — short description like `I am incompetent` or `I can improve`
- `confidence: float` — 0..1 overall confidence in this frame
- `persistence_hint: str` — one of `transient` | `sustained` | `persists`
- `derived_state_suggestions: Dict[str, Any]` — optional hints for `StateManager`, e.g. `{"activate": ["embarrassment","motivation"], "dims": {"motivation":0.6}}`
- `evidence_snippets: List[Dict]` — raw evidence excerpts (text of utterance, appraisal dims) for explainability
- `provenance: Dict` — full structured refs: perception id, appraisal frame id(s), expectation ids, memory refs

## MeaningResult
Returned by the `interpret()` function. Contains:

- `meaning_frames: List[MeaningFrame]`
- `aggregate_relevance: float` — summary 0..1 relevance across frames
- `primary_meaning: Optional[str]` — highest-confidence interpretation (for reporting only)
- `conflicts: List[str]` — short descriptions of meaning conflicts (if any)
- `insufficient_data: bool`

## Deterministic rule sketch (first-pass)
MAL will use deterministic, explainable rule mapping from appraisal+
expectations + person context → candidate interpretations. Rules are
additive and conservative (produce alternatives with confidence scores). Example
rule patterns:

- Appraisal label `threat` + `social_threat >= 0.7` + utterance contains
  insult words → candidate interpretations: `humiliation (0.9)`, `challenge (0.6)`, `social_rejection (0.5)`.
- Appraisal `threat` + high `goal_relevance` + person.values contains `career` →
  increase `personal_relevance` and promote `proving_self`/`motivation` suggestions.
- Expectation `confrontation` probability >= 0.5 → increase `personal_relevance` and
  favor `defensiveness`/`proactive defense` alternatives.
- Memory lookup: similar past events with `embarrassment` label → raise persistence_hint to `sustained`.

Rules should produce `derived_state_suggestions` rather than authoritative
state labels: `StateManager` remains responsible for creating/reinforcing
StateInstances based on those suggestions plus other evidence.

## Representing uncertainty
- Each MeaningFrame carries a `confidence` (0..1) and `interpretation_alternatives`.
- Downstream components must accept multiple simultaneous frames and weigh them
  using (`personal_relevance` × `confidence` × recurrence) when deciding
  reinforcement. MAL does not collapse alternatives into single truth.

## Persistence & reinforcement semantics (guidance)
- `persistence_hint` instructs `StateManager` how to treat derived evidence:
  - `transient` — evidence decays normally with trigger disappearance
  - `sustained` — reduce decay rate; more likely to be reinforced into memory
  - `persists` — explicit forgetting required; candidate for long-term memory
- Repeated, consistent MeaningFrames (same interpretation + high relevance)
  increment a recurrence counter and can be promoted into sustained states
  via `StateManager.reinforce_state_to_memory()`.

## Multiple/coexisting meanings
MAL must support simultaneous, even conflicting, MeaningFrames. Example:
`['humiliation', 'challenge']` can both appear with different confidences and
different derived_state_suggestions; `StateManager` may create coexisting
StateInstances (e.g., `sadness` + `motivation`).

## Interaction with current State of Mind and personal history
- MAL must consult `person_state` (current `state_of_mind`, `goals`, `values`,
  `personality`, `memory` references) to bias interpretation (not override it).
- The same appraisal will produce different MeaningFrames for different
  `person_state`s; MAL should output confidence-weighted alternatives.

## Boundaries/Definitions (explicit)
- Event: external occurrence (e.g., utterance, push, environmental change).
- Perception: sensory/processing layer that extracts observations from event.
- Appraisal: deterministic interpretation of perceptual cues into labeled
  frames with dimension scores (e.g., `threat`, `opportunity`).
- Meaning (MeaningFrame): personal significance attributed to an appraisal;
  links appraisal to personal values, goals, predicted self-view change,
  and motivation direction.
- Emotion/Feeling/Mood (EFMSOMB): low-level affective variables (arousal,
  valence, mood tags). These are inputs to MAL and outputs of `StateManager`.
- State of Mind: the multi-state snapshot maintained by `StateManager` (set of
  `StateInstance`s with intensity/duration/provenance).
- Motivation: direction and intensity of goal-directed drives derived from
  meanings and states (e.g., `approach` vs `avoid`), expressed as suggestions
  but not as actions.
- Goal: existing personal goal objects in `person_state` that can be activated
  by meanings.
- Behavioral tendency: pressures produced by proposal subsystems and modulated
  by states (handled downstream of MAL).
- Final action: output of Competition/Arbitration after modulation and
  selection.

## Concrete example: "Someone embarrasses you publicly because you don't have money"
### Appraisal produced:
- AppraisalFrame(label=`threat`, dimensions: social_threat=0.95, goal_relevance=0.8, valence=-0.9)

### MAL produces multiple MeaningFrames (examples):

Path A (withdrawal):
- MeaningFrame:
  - interpretation: `humiliation`
  - interpretation_alternatives: [("humiliation",0.9),("rejection",0.6),("challenge",0.2)]
  - personal_relevance: 0.8 (status/esteem affected)
  - affected_values: [`esteem`,`belonging`]
  - activated_goals: [`avoid_public_shame`]
  - motivation_direction: `withdraw`
  - derived_state_suggestions: {"activate": ["embarrassment","sadness"], "dims": {"sadness":0.7}}
  - persistence_hint: `sustained` if person history includes past shaming events

Path B (prove-yourself):
- MeaningFrame:
  - interpretation: `challenge` ("I need to prove myself")
  - interpretation_alternatives: [("challenge",0.8),("humiliation",0.4)]
  - personal_relevance: 0.7
  - affected_values: [`competence`,`achievement`]
  - activated_goals: [`improve_financial_status`,`prove_self`] 
  - motivation_direction: `approach` / `prove_self`
  - derived_state_suggestions: {"activate": ["motivation","focus"], "dims": {"motivation":0.6,"attention":0.7}}
  - persistence_hint: `transient` unless reinforced by memory or goals

Path C (confront):
- MeaningFrame:
  - interpretation: `social_disrespect` → `anger`
  - personal_relevance: 0.6
  - activated_goals: [`protect_reputation`]
  - motivation_direction: `approach` / `defend`
  - derived_state_suggestions: {"activate": ["anger","defensive"], "dims": {"threat":0.7}}

All three frames exist concurrently; each includes provenance back to the
appraisal frame id and the original perception id. `StateManager` may use the
`derived_state_suggestions` to create `embarrassment`, `sadness`, `motivation`,
`focus`, and `defensive` StateInstances, with initial intensities guided by
the `dims` and `personal_relevance`.

## Provenance structure (minimum required fields)
Every MeaningFrame must include a `provenance` object with at least:

- `perception_ids: List[str]` — perceptions used
- `appraisal_frame_ids: List[str]` — appraisal frames used
- `expectation_ids: List[str]` — supporting predictions
- `memory_refs: List[str]` — optional historical matches
- `meaning_frame_id: str` — the MeaningFrame's own id
- `created_timestamp: str` — ISO timestamp

When MAL produces EvidenceRecords for `StateManager`, each EvidenceRecord's
`ref` must reference the `meaning_frame_id` to keep the causal chain:

perception.id → appraisal.frame.id → meaning_frame.id → state_instance.id → tendency/competition logs

## APIs (spec only, no implementation)
Provide a pure, deterministic function:

`interpret(appraisal: Appraisal, expectations: Expectations, person_state: PersonState, system_memory=None) -> MeaningResult`

This function MUST NOT modify `person_state`.

Optional helper (side-effect allowed, but separate):

`apply_meanings_to_person(person_state: PersonState, meaning_result: MeaningResult) -> List[EvidenceRecord]`

- Appends `MeaningFrame`s to `person_state.meanings` and returns EvidenceRecords
  that the DecisionEngine will pass to `StateManager.create_or_update_from_trigger`.

## Testing & validation plan (spec-level)
- Unit tests for `interpret()` using the recorded embarrassment trace:
  - Verify multiple MeaningFrames produced (humiliation, challenge, disrespect).
  - Check `derived_state_suggestions` contains `motivation`+`focus` suggestions for Path B.
- Integration (read-only) verification: run the existing DecisionEngine pipeline
  with `interpret()` inserted (not implemented here) and confirm StateManager
  receives evidence referrals with ref -> meaning_frame.id and that coexisting
  states emerge.

## Open architectural questions (to resolve before implementation)
1. Persistence policy: who decides promotion from `transient` → `sustained` → `persists`? MAL should recommend but `StateManager` must implement final policy. Define thresholds and memory signals for promotion.
2. Granularity of `interpretation` taxonomy: how many canonical labels do we support initially? Choose a small, well-defined set first.
3. Conflict resolution vs coexistence: when should MAL/caller prefer coexisting frames vs merging into a composite meaning? Define heuristics for composite frames.
4. Memory lookup cost & indexing: how will MAL efficiently query personal history/memory for similar events? Consider a simple tag-based index for the first pass.
5. Testing coverage: which dialogue corpus or synthetic cases will validate broad coverage (cultural & personality variance)?
6. Privacy & storage: how long do we store MeaningFrames and memory-linked evidence? Who may inspect them?

## Next steps (after spec approval)
1. Finalize canonical interpretation taxonomy and persistence policy.
2. Implement `meaning_interpretation.py` skeleton with `MeaningFrame` dataclass and deterministic `interpret()` that returns `MeaningResult` (read-only). Add unit tests using the embarrassment trace.
3. Integrate DecisionEngine to call `interpret()` and convert MeaningFrames to EvidenceRecords consumed by `StateManager` (non-destructive integration guarded by feature flag).

Do not modify `StateManager`, `DecisionEngine`, `StateModulation`, `Competition`, or `Arbitration` in this specification step.

---
End of Meaning Attribution Layer specification (draft).

## Finalized decisions (taxonomy + mapping)
The following concrete decisions finalize the six open architectural items identified
in the review. These are intended to be stable defaults for the first implementation
and can be expanded later with versioning.

### 1) Initial Meaning taxonomy
Keep a deliberately small, extensible taxonomy separated into groups.

- Social meanings:
  - `humiliation`
  - `embarrassment`
  - `rejection`
  - `disrespect`
  - `social_threat`

- Self-related meanings:
  - `failure`
  - `inadequacy`
  - `loss_of_status`
  - `self_doubt`

- Action-oriented meanings:
  - `challenge`
  - `opportunity`
  - `need_to_prove_self`
  - `need_to_protect_self`

- Interpretive direction (meta-labels):
  - `approach`
  - `avoidance`
  - `defense`
  - `withdrawal`

- Special token: `unknown` / `uncertain` for cases with low confidence.

Notes: these are interpretation labels only, not emotions or states. `MeaningFrame`
`interpretation` must always be one of these canonical labels (or `unknown`).

### 2) Meaning → StateManager contract
Preserve the chain: `MeaningFrame` → `EvidenceRecord` → `StateManager` → `StateInstance`.

Contract rules:

- When converting a MeaningFrame to EvidenceRecord(s), set `EvidenceRecord.ref = MeaningFrame.id`.
- Each EvidenceRecord `signal` should use a suggested state label (not an interpretation label) drawn from a small set of state-dimension keywords (see below).
- EvidenceRecord `value` may contain a `dimensions` dict with numeric hints in `[0,1]`.
- Meaning attribution MUST NOT directly construct `StateInstance` objects; it only emits EvidenceRecords.

Allowed state dimension keys (initial set) and their ranges [0,1]:

- `motivation` (0..1)
- `attention` / `focus` (0..1)
- `sadness` (0..1)
- `embarrassment` (0..1)
- `anger` (0..1)
- `defensive` (0..1)
- `threat` (0..1)
- `confidence` (0..1)

Mapping guidance example:

- MeaningFrame `interpretation = 'challenge'` may create EvidenceRecord with `signal='motivation'` and `value={'motivation':0.6,'attention':0.7}`.
- MeaningFrame `interpretation = 'humiliation'` may create EvidenceRecord with `signal='embarrassment'` and `value={'embarrassment':0.7,'sadness':0.5}`.

### 3) Confidence model
Deterministic confidence in a MeaningFrame must be computed in [0,1] using the following components (weighted sum normalization):

- `appraisal_support` (0..1): based on how strongly appraisal dimensions match the interpretation.
- `expectation_support` (0..1): evidence from Expectations predictions supporting the interpretation.
- `personal_relevance` (0..1): derived from `person_state.goals/values/personality` alignment.
- `memory_support` (0..1): result from memory query (see contract below).
- `current_state_support` (0..1): whether current `person_state.states` or EFMSOMB make the interpretation more likely.
- `self_report_support` (0..1): if a self-report exists matching the interpretation.

Combine via normalized weighted sum:

confidence = clamp(0,1, (w1*appraisal_support + w2*expectation_support + w3*personal_relevance + w4*memory_support + w5*current_state_support + w6*self_report_support) / (w1+w2+w3+w4+w5+w6))

Default weights (initial): w1=3, w2=2, w3=2, w4=1.5, w5=1.5, w6=3

Important: `confidence` is the model's belief that the interpretation label is the best description; it is NOT the `intensity` of any resulting state. `derived_state_suggestions` include separate numeric `dims` for guiding `StateManager` intensity.

### 4) Memory interaction (query contract)
MAL must use a limited, controlled memory query interface. The API contract:

`find_related_meanings(tags: List[str], person_id: str, time_window_seconds: Optional[int], limit: int=5) -> List[MemoryMatch]`

`MemoryMatch` contains: `memory_id`, `matching_tags`, `timestamp`, `relevance_score`.

Rules:
- MAL may call this API with small `limit` (e.g., 3) and reasonably small `time_window_seconds` when needed. Memory results only contribute `memory_support` and `persistence_hint` adjustments; they do not override appraisal inputs.

### 5) Self-report handling
Self-report payload must include:

- `source='self_report'`
- `reported_interpretation` (one of taxonomy labels)
- `reported_feelings` (optional list)
- `timestamp`
- `confidence` (0..1)
- `context` (free text/metadata)
- `timing` flag: `during_event` | `retrospective`

Handling rules:
- Treat self-report as high-evidence but not authoritative. Map `self_report.confidence` into `self_report_support` and use weight w6 in the confidence model.
- Always preserve provenance: mark MeaningFrame provenance with `self_report_id` and `timing`.

### 6) Persistence / retention
Differentiate record lifecycle states:

- `active`: MeaningFrame actively influences current interpretation/state; used to generate EvidenceRecords.
- `inactive`: MeaningFrame no longer influences states but remains stored for lineage.
- `archived`: persisted long-term for learning/analytics; may be compressed.

Promotion rules (high-level):
- New MeaningFrame initial `persistence_hint` drives `active` behavior (`transient` default).
- Repeated MeaningFrames with consistent interpretation, high `personal_relevance`, and memory matches increment a recurrence counter; if recurrence >= N (default N=3) within time window T (default T=30 days), recommend `sustained`.
- Archive policy: After `inactive` for retention_period (configurable, default 90 days), move to `archived` compressed representation.

## Critical validation scenario (explicit)
Event: "Someone publicly embarrasses the person about money."

System outputs (simultaneously):
- MeaningFrames: `humiliation` (0.9), `challenge` (0.7), `need_to_prove_self` (0.6)
- EvidenceRecords emitted (ref -> meaning_frame.id):
  - `signal='embarrassment', value={'embarrassment':0.7,'sadness':0.5}`
  - `signal='motivation', value={'motivation':0.6,'attention':0.7}`
  - `signal='defensive', value={'defensive':0.3,'anger':0.4}`

After external trigger disappears:
- `MeaningFrame` instances may remain `active` per `persistence_hint` and recurrence.
- `StateManager` decides decay rates; meaning-derived evidence may continue to reinforce states until they decay or are explicitly revised.

## Remaining unresolved questions
- exact numeric thresholds for recurrence promotion (`N`, `T`) and archive periods (policy decisions).
- canonical goal id schema and how `activated_goals` link into existing `person_state.goals` objects.
- performance budget for MAL memory queries and caching strategy.
- storage & privacy policy scoping for archived MeaningFrames.

Update complete: taxonomy and mapping decisions are recorded here and can guide the read-only skeleton implementation.
