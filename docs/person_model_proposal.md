# PsyPredictor: Canonical Person Model Proposal

Purpose
- Pause further nested-box architecture changes and define a canonical human/person model.
- Provide a compact schema and an explicit appraisal pipeline that maps directly to the existing code.

High-level goals
- Separate stable vs semi-stable vs dynamic information.
- Provide a minimal, testable schema for `PersonState` and a clear appraisal function signature.
- Map existing repo fields to the schema to guide incremental refactor.

Canonical model (summary)
1. Stable core (traits, identity core)
   - `core.person_id` (str)
   - `core.name` (str)
   - `core.personality` (dict of trait->float) — stable dispositions (Big Five-style)
   - `core.values` (dict id->weight) — prioritized value space (Schwartz-style categories optional)
   - `core.moral_identity` / `core.standards` (list)

2. Semi-stable constructs (change slowly over time)
   - `beliefs`:
     - `beliefs.explicit` (list of strings or structured beliefs)
     - `beliefs.implicit_tags` (list)
   - `long_term_goals` (list of goal objects)
   - `identity.self_concept` (multi-dimensional self-schemas)
   - `relationships` (list of {id,role,closeness, valence})

3. Dynamic state (moment-to-moment)
   - `state.needs` (dict need->urgency 0-1)
   - `state.arousal` (float)
   - `state.affect` (valence/arousal or discrete labels)
   - `state.emotion` (list of emotion descriptors)
   - `state.attention` (tags, focus weight)
   - `state.context` (short description / environment tags)
   - `state.intentions` / `action_tendencies`

4. Learning/memory systems
   - `memory.episodic` (list of experiences with timestamps, tags, dimensions)
   - `memory.semantic` (concept map, schemas)
   - `habit_strength` (pattern_id -> {action: strength})
   - `prediction_history` (for expectation updates)

5. Meta / control
   - `meta.perceived_control` (float)
   - `meta.self_regulation` (float)
   - `meta.confidence` (float)
   - `metacognition` (capabilities, prior success records)

Appraisal pipeline (function spec)
- Signature:
  - `appraise(perception: dict, person: PersonState) -> AppraisalResult`
- Inputs:
  - `perception`: raw event tags, sensory cues, environment descriptors
  - `person`: canonical person model (core, beliefs, values, needs, memory, relationships)
- Process (composition):
  1. Relevance: compute how event maps to `state.needs`, `core.values`, and `long_term_goals`.
  2. Congruence: evaluate consistency with goals/values/standards/identity.
  3. Accountability / causal attribution: determine blame/credit using `beliefs` and `relationships`.
  4. Coping potential: use `meta.perceived_control` + `meta.self_regulation` + memory-based analogs.
  5. Normative significance: compare against `core.standards` / social norms.
  6. Combine to produce an `appraisal` object: `{relevance, congruence, attribution, coping_potential, normative_significance}`.
  7. Map appraisal -> `emotion` (labels or probabilities) + `action_tendencies` (scored list).
- Outputs:
  - `AppraisalResult`: appraisal object, emotion labels/confidence, action_tendencies (action->score), reasoning tokens.

Mapping to existing code (quick)
- `person_state.py` -> central `PersonState` (already contains many fields). Proposed: reorganize into `core`, `beliefs`, `state`, `memory`, `meta` sub-objects.
- `goal_manager.py` -> aligns with `generate_goals(value_weights, need_state, identity_schema)` but should accept `person.core` and `person.state` to compute better priorities.
- `system_memory.py` -> provides beliefs/values/history; continue using as global store, but add typed events for `episodic` vs `state_learning`.
- `action_selection.py` -> implements scoring; replace heuristics with call to `appraise()` + `assess_tendency()` for final adjustment.

Migration plan (incremental)
1. Add `docs/person_model_proposal.md` (this document).
2. Add a small `appraisal.py` module with `appraise()` stub and unit tests (accept current `PersonState` shape, return standard `AppraisalResult`).
3. Update `person_state.py` to expose new aliases (`person_state.core`, `person_state.state`, but keep legacy fields until migration complete).
4. Update `goal_manager` to accept `PersonState` or `person.core` directly and include belief-based boosts.
5. Replace parts of `action_selection` to call `appraise()` and then apply `SystemMemory.assess_tendency()`.
6. Run tests and iterate.

Testing & validation
- Add unit tests for `appraise()` covering: relevance to needs, congruence with values, coping potential effects, and mapping to emotions/action tendencies.
- Add property-based tests ensuring `generate_goals()` priority correlates with high-urgency needs + value weight + identity boosts.

Next steps I will take (if you approve)
- Implement `appraisal.py` stub and unit tests.
- Add `PersonState` alias shims to ease migration.

---

File created: `docs/person_model_proposal.md` — review and tell me which parts to expand or change.