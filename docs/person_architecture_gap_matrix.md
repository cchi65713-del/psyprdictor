# PsyPredictor: Architecture Gap Matrix

This matrix compares the current architecture against the human/person model questions we are trying to answer:

> What internal differences cause two people to interpret the same event differently, feel differently, remember it differently, form different habits, and choose different actions?

## Summary

The current repo already contains a strong foundation for many components, but the architecture is still partially shaped by EFMSOMB assumptions and heuristics. The most important missing step is to define the canonical person model before finalizing the layered architecture.

## Gap matrix

| Human/person concept | Research view | Current PsyPredictor equivalent | Status | Gap / implication | Recommended home |
|---|---|---|---|---|---|
| Identity / self-model | Continuity of self over time; self-concept; personal + social identity | `PersonState.identity`, `identity_schema`, `fill_actual_identity()` | Partial | Identity exists, but is not yet clearly separated from current state or self-concept structure | `PersonState.identity` + `self_model` |
| Personality | Stable trait-level tendencies | `PersonState.personality`, `trait_personality` | Partial | Personality is modeled but not yet fully integrated into appraisal or self-model | `PersonState.core.personality` |
| Values | Stable priorities shaping judgments and choices | `value_weights`, `values` | Partial | Values are used in goal generation but not yet as a first-class structured system | `PersonState.core.values` |
| Beliefs | Assumptions, expectations, interpretations | `PersonState.beliefs`, `SystemMemory.beliefs` | Partial | Good foundation, but beliefs need explicit distinction between explicit, implicit, and learned assumptions | `PersonState.beliefs` + `SystemMemory.beliefs` |
| Needs / motives | Urgency drivers and motivational state | `need_state`, `needs` | Partial | Needs are modeled and used for goals; could be refined into explicit motive hierarchy | `PersonState.state.needs` |
| Goals | Intentions and priorities | `active_goals`, `goals`, `GoalManager.generate_goals()` | Partial | Goal generation is active and plausible, but still simple and value/need-based | `GoalManager` + `PersonState.active_goals` |
| Emotion | Affective response to appraisal | `emotion`, `feeling`, `mood`, `state_emotion` | Partial | Emotion exists, but appraisal is not yet a first-class computational step | `PersonState.state.affect` / `emotion` |
| Appraisal | Interpretation of event relevance, congruence, coping, accountability | Not explicit; some fields exist (`state_appraisal`, `appraisal`) | Missing | This is the biggest architectural gap. The system currently mixes state and action heuristics without a formal appraisal layer | New `Appraisal` layer |
| Memory | Episodic, semantic, procedural knowledge | `Memory`, `SystemMemory.history`, `memory_refs`, `prediction_history` | Partial | Memory is present, but the structure is not yet explicit enough to distinguish episodic vs semantic vs procedural | `Memory` / `SystemMemory` / `PersonState.memory` |
| Habits | Automatic behavior cued by context | `habit_strength`, `habit_formation.py`, `PatternLearner` | Partial | Habit architecture is promising and already implemented, but still tied to learned pattern id heuristics | `Learning` + `PersonState.habit_strength` |
| Attention / perception | Salience filters and interpretation layer | `PersonState.perception`, `attention`, `context`, `trigger` | Partial | A perception layer exists, but it is not yet clearly defined as a gate before appraisal | `PersonState.state.perception` |
| Social / relational context | Roles, relationships, social identity, norms | `PersonState.identity[relationships]`, `SystemMemory.relationships`, `relationship` box | Partial | Good start, but relational meaning is shallow and not yet structured like a social graph | `PersonState.relationships` + `SystemMemory.relationships` |
| Expectations / prediction | Forecasts about future states and outcomes | `PredictionEngine`, `PredictionFusion`, `prediction_history` | Partial | Prediction is present, but not yet clearly integrated with identity-based expectations or appraisal | `Prediction` / `PersonState.prediction_history` |
| Self-regulation | Control over attention, emotion, behavior | `self_regulation`, `state_regulation`, `perceived_control`, `metacognition` | Partial | This is central to behavior selection but is not fully connected to appraisal or action choice | `PersonState.meta` / `metacognition` |
| Metacognition | Monitoring and reinterpreting own behavior | `Metacognition`, `state_meta_confidence` | Partial | Present but not yet central in the architecture | `Metacognition` + `PersonState.meta` |
| Learning / adaptation | Updating beliefs, habits, strategy over time | `PatternLearner`, `LearningBridge`, `SelfLearning`, `PatternAdaptation` | Partial | Good foundation, but learning is broad and still not organized into stable + dynamic layers | `Learning` layer |
| Decision / action selection | Deliberative vs habitual vs reactive choice | `ActionSelector`, `propose_goal_directed`, `propose_habitual`, `propose_reactive` | Partial | Good separation exists, but it still reads like an implementation scaffold rather than a complete decision architecture | `ActionSelection` |

## Most important missing architectural pieces

1. A formal appraisal layer
   - Current code does not cleanly create an interpretation of the event before emotion/action selection.
   - This is the clearest design gap.

2. A canonical person split
   - We need a clear distinction between:
     - stable core
     - semi-stable identity and values
     - dynamic state
     - memory/learning
     - self-regulation/meta

3. Clear identity continuity
   - The system can store memory and goals, but it still needs a strong model of "this is the same person across time".

4. Decision pipeline separation
   - Current pipeline is closer to:
     - context → EFMSOMB → action heuristics
   - It should become closer to:
     - perception → appraisal → goals/needs/values → emotion/state → action selection → learning

## Current architectural direction

The repo is already moving in the correct direction:

EFMSOMB
→ awareness + memory + environment
→ activation / pattern recognition
→ action selection
→ person model / identity layer
→ appraisal
→ behavior prediction

This is a healthy progression, but the missing transition is the explicit person model and appraisal layer.

## Recommendation

Do not finalize the architecture by guessing from the current modules alone. Instead, treat the current design as a working scaffold and use the research question as the anchor:

> What attributes of a person materially influence how they interpret an event, what they remember, what they learn, and what action they choose?

Only after answering that should we lock down:
- `PersonState`
- `SystemMemory`
- `GoalManager`
- `Appraisal`
- `ActionSelection`
- `Learning`
- `Metacognition`

## Bottom line

The current repo has a strong base, but the architecture is still in transition from a pattern/EFMSOMB system toward a more complete person model. The next necessary step is not more nested boxes; it is a better-defined person model and explicit appraisal pipeline.
