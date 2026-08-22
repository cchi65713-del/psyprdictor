# ARCHITECTURE_MAPPING.md

Purpose
-------
Map the canonical constructs from `ARCHITECTURE_PROFILE.md` to existing PsyPredictor modules and files. Note where constructs are implemented, where they are missing or under-specified, and where overlap/double-count risk appears.

Summary mapping
---------------

- Personality (traits)
  - Files: `person_state.py` (`personality` dict)
  - Notes: Implemented as `aggression`/`avoidant`. Good single location; ensure explicit prefixing to `trait_` and single-writer API.

- Values
  - Files: `person_state.py` (`values`) and `action_selection.propose_goal_directed` (reads values)
  - Notes: Present but informal; unify to `value_weights` and document owner APIs.

- Beliefs & Expectations
  - Files: `system_memory.py` (rules, beliefs), `perception_appraisal_expectations.py` (perception/expectation code), `prediction_fusion.py`
  - Notes: Beliefs currently exist in `system_memory` and perception code creates expectations; create canonical belief update API to avoid duplication.

- Needs / Motivations
  - Files: `person_state.py` (`needs`) and `action_selection.propose_goal_directed` (consumes needs)
  - Notes: Present but light; attach urgency semantics and goal origin metadata.

- Goals
  - Files: `person_state.py` (`goals`), `action_selection.propose_goal_directed` (produces goal-directed tendencies)
  - Notes: Goals exist as a field; recommend a `goal_manager` abstraction to own lifecycle and produce `BehavioralTendency` proposals.

- Identity / Self-concept
  - Files: `person_state.py` (`identity`) — minimal
  - Notes: Underdeveloped; expand to `identity_schema` (roles, standards) and use for goal constraints.

- Memory / Experience
  - Files: `memory.py`, `pattern_learner.py`, `experience.py`, `learning_bridge.py`
  - Notes: Good foundation; ensure `pattern_stats` is canonical and other modules read it rather than re-summarize.

- Habits
  - Files: `person_state.py` (`habit_strength`), `habit_formation.py`, `action_selection.propose_habitual`
  - Notes: Present and tested; enforce single-writer (`habit_formation.update_habit_strengths`) and prevent other modules from directly modifying `habit_strength`.

- Momentary State (emotion/appraisal/arousal/regulation/confidence)
  - Files: `person_state.py` (fields), `action_selection.propose_reactive`, `perception_appraisal_expectations.py`, `state_manager.py`
  - Notes: `state_of_mind` is overloaded. Split into canonical `state_*` fields and update callers.

Overlaps and double-counting hotspots
------------------------------------
- `state_of_mind` vs `emotion`/`feeling`/`mood` vs `confidence` (multiple fields used interchangeably) — consolidate.
- `history` vs `mem_episodic` vs `pattern_stats` — clarify that `memory` is canonical store and `pattern_stats` are derived summaries.
- `preferences` vs `values` vs `goals` — enforce naming and origin metadata so a `goal` shows `origin:value|need|identity`.
- `beliefs` written/read by multiple modules — funnel updates through a `BeliefUpdater` API in `system_memory.py`.

Files to edit (design proposals)
-------------------------------
- `person_state.py`: rename fields to canonical prefixes (e.g., `trait_personality`, `value_weights`, `need_state`, `identity_schema`, `habit_strength`, `state_*`) and add setters with ownership checks.
- `action_selection.py`: ensure it reads canonical fields and that `propose_*` functions generate `BehavioralTendency` with canonical `supporting_evidence` format.
- `habit_formation.py`: confirm it is the single writer to `person_state.habit_strength` and document its update rules.
- `pattern_learner.py` / `memory.py`: expose `get_pattern_stats` and ensure `BeliefUpdater` consumes it rather than ad-hoc reads elsewhere.
- `system_memory.py`: implement `BeliefUpdater.update_from_pattern(pattern_stats)` API and accept `state_manager` exports.

Immediate recommended non-code steps
-----------------------------------
1. Adopt `ARCHITECTURE_PROFILE.md` canonical names across the codebase with a short migration checklist.  
2. Add unit tests for single-writer properties and evidence deduplication.  
3. Draft a small `goal_manager` interface that consumes `value_weights`/`need_state`/`identity_schema` and emits `active_goals` with `origin` metadata.  

Next steps
----------
- If you want, I can (A) generate the `goal_manager` API spec + tests, or (B) open PR-like patches to update `person_state.py` field names and add setter APIs. Which would you prefer next?

Appendix: quick code anchors
--------------------------
- `person_state.py` — identity/personality/state fields
- `action_selection.py` — `propose_goal_directed`, `propose_habitual`, `propose_reactive`
- `habit_formation.py` — `update_habit_strengths`
- `pattern_learner.py` — `record_feedback`, `get_pattern`
- `memory.py` — `store`, `get_by_pattern_id`
- `competition.py` — normalization and competition contracts
- `learning_bridge.py` — execution → learning orchestration

End mapping.
