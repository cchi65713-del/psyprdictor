# PsyPredictor: Human/Person Model Research Plan

Goal
- Define what a computational person model should contain before finalizing the architecture.
- Keep the architecture hypothesis-driven instead of deriving it from EFMSOMB assumptions alone.

Decision rule
- Every proposed component must answer one question:
  - Does this component materially change how the same person interprets an event, forms goals, learns, or selects action?
- If not, it likely does not belong in the canonical person model.

Research focus areas
1. Identity / self-model
   - self-concept
   - personal identity vs social identity
   - self-image, self-esteem, ideal self
   - continuity over time

2. Stable dispositions
   - personality traits
   - trait stability vs situational change
   - trait influence on appraisal and action choice

3. Values and beliefs
   - values as priorities
   - beliefs as assumptions / expectations / causal models
   - belief strength and source
   - differences between values, beliefs, attitudes, and preferences

4. Needs and motivations
   - biological and psychological needs
   - motive hierarchies
   - needs vs goals
   - urgency / salience

5. Goals
   - short-term vs long-term goals
   - goal hierarchies
   - goal conflict and prioritization
   - self-regulation of goal pursuit

6. Affect and emotion
   - appraisal theory
   - emotion vs feeling vs mood
   - physiological arousal
   - action tendencies

7. Learning and memory
   - episodic memory
   - semantic memory
   - procedural memory / habits
   - memory retrieval and relevance
   - memory as a source of meaning and pattern

8. Habits and automatic behavior
   - habit loops
   - cue-response-reward structure
   - how habits compete with deliberate goals

9. Attention and perception
   - what is attended to
   - salience and bias
   - interpretation filters
   - perception as not identical to reality

10. Social and environmental context
   - relationships
   - norms
   - role identity
   - culture / group membership
   - environmental affordances and constraints

11. Expectations / prediction
   - prediction as a core way humans interpret events
   - expected outcomes, confidence, uncertainty
   - prediction error and adaptation

12. Decision and action selection
   - deliberative vs habitual vs reactive choice
   - competing influences from values, emotions, habits, and goals

13. Self-regulation and metacognition
   - control over attention, emotion, and behavior
   - monitoring of own state
   - confidence and error awareness

14. Adaptation and change over time
   - stable vs dynamic layers
   - learning over experience
   - how memory, identity, and goals co-evolve

Research output format
For each concept, capture:
- definition
- how it changes over time (stable, semi-stable, dynamic)
- how it influences interpretation/appraisal
- how it influences action/behavior
- whether it belongs in `PersonState`, `SystemMemory`, `GoalManager`, `Appraisal`, `ActionSelection`, or `Learning`
- whether it should be represented as a scalar, dict, list, event stream, or nested structure

Architecture comparison template
Human concept | Research view | PsyPredictor equivalent | Missing? | Modify? | Recommended home

Example rows:
- Identity / self-model | continuity over time | currently partial / undefined | yes | yes | `PersonState.identity` + `self-model`
- Personality | trait-level stability | `PersonState.personality` | partial | yes | `PersonState.core`
- Values | priorities guiding choices | `value_weights` / `values` | partial | yes | `PersonState.core.values`
- Beliefs | assumptions about world / self | `beliefs` | partial | yes | `PersonState.beliefs`
- Needs | urgency drivers | `need_state` | partial | maybe | `PersonState.state.needs`
- Goals | prioritized intentions | `active_goals` | partial | yes | `GoalManager` + `PersonState`
- Memory | episodic/semantic/procedural | `Memory` / `SystemMemory` | partial | yes | `memory` layer
- Appraisal | interpretation of event | absent/underdefined | yes | yes | new `Appraisal` layer
- Habit | automatic action path | `habit_strength` / `PatternLearner` | partial | yes | `Learning` + `PersonState.habit_strength`

Working hypothesis
The person model should be organized in layers:
1. Stable core
2. Semi-stable self-model and value system
3. Dynamic state
4. Learning / memory
5. Meta / regulation

This is a research-informed hypothesis, not final truth.

Immediate task
- Use this plan to compare each concept against the current repo and identify gaps.
- Only after that should we finalize `PersonState` and implement appraisal.

Deliverable after research pass
A final architecture summary that maps:
- what is necessary,
- what is optional,
- what should stay lightweight,
- and what belongs in each module.
