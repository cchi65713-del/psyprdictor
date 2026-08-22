# State of Mind Review

## Purpose

This review critically examines the proposed State of Mind architecture against the actual PsyPredictor implementation. It distinguishes what already exists in the project from what is proposed but not yet implemented.

This document does not modify any Python files or existing logic. It is a design critique and recommended architecture review.

---

## 1. What information should be allowed to influence State of Mind?

The current architecture already supports the following as relevant input sources:

### Already present and relevant
- `emotion`
- `feeling`
- `mood`
- `state_of_mind` (existing field)
- `arousal`
- `self_regulation`
- `awareness`
- `context`
- `environment`
- `trigger`
- `goals`
- `needs`
- `values`
- `personality`
- `habit_strength`
- `active_patterns`
- `history`
- `memory_refs`
- `behavior`

### Relevant but currently weakly connected
- `perception`
- `attention`
- `appraisal`
- `expectations`
- `beliefs`
- `confidence`
- `perceived_control`

### Should be allowed to influence State of Mind in the design
These fields should be permitted to contribute to State of Mind inference because they describe the person's current context and internal regulatory posture:
- `emotion`
- `feeling`
- `mood`
- `arousal`
- `self_regulation`
- `awareness`
- `context`
- `environment`
- `state_of_mind` (existing value as an input or prior state)
- `goals`
- `needs`
- `values`
- `behavior`
- `history`
- `habit_strength`

### Should not be treated as direct sources of State of Mind by default
The system should not treat all observable data as a direct source of State of Mind. The following are not good primary drivers unless explicitly designed for that purpose:
- raw action labels
- final selected action
- learned pattern IDs alone
- unrelated system memory entries
- environment text without interpretation
- personality structure alone
- long-term identity markers unless they are explicitly being used as context

This is important: State of Mind should be an internal state summary, not a proxy for every other variable in the system.

---

## 2. What information should NOT directly determine State of Mind?

These should not directly determine State of Mind without interpretation:

### A. The final action itself
The final chosen action is an outcome, not a cause. It should not define the person's state.

### B. The winning competition result
Competition outputs should not be used as raw evidence for State of Mind unless the system explicitly records that the decision was made under a given state.

### C. SystemMemory rule strings alone
SystemMemory stores beliefs and rules, but those are not the same as the person's current state. They may contribute as contextual evidence, but not directly define State of Mind by themselves.

### D. Long-term identity traits unless explicitly treated as context
Identity and personality are slower-moving, not immediate state.

### E. A single raw external signal without interpretation
Examples:
- a trigger alone
- a single environment label alone
- a single emotion label without context
- a single value or need without considering current regulation

These are inputs to inference, not the state itself.

---

## 3. How should Emotion, Feeling, Mood, State of Mind, Awareness, Perception, Appraisal, and Expectations relate to each other?

These components should be treated as a layered structure, not as interchangeable names.

### Existing architecture relation
The current code already clearly separates:
- `emotion`
- `feeling`
- `mood`
- `state_of_mind`
- `awareness`
- `perception`
- `appraisal`
- `expectations`

This is useful and should be preserved.

### Recommended conceptual relationship

1. Perception
   - What the person notices.
   - Input to interpretation.

2. Appraisal
   - How the person interprets what they noticed.
   - This is the bridge between external situation and internal meaning.

3. Expectations
   - What the person anticipates will happen.
   - Shapes urgency and preparedness.

4. Emotion
   - Immediate affective response to that interpretation.

5. Feeling
   - Subjective experience of that affect.

6. Mood
   - Broader background tone over time.

7. Awareness
   - Meta-awareness of what is happening internally and externally.

8. State of Mind
   - The current higher-order operating mode that integrates emotion, mood, appraisal, awareness, and context into a functional mode of engagement.

### Important distinction
Emotion, feeling, and mood are about valence and affective quality.
State of Mind is about interpretation and mode of engagement.

That distinction is essential and should remain explicit.

---

## 4. Can multiple states exist simultaneously?

Yes, but only if the architecture is designed to support it.

The current implementation stores `state_of_mind` as a dictionary, which already suggests multiple states are possible.

This is the most compatible design because it allows:
- defensive + threatened
- calm + focused
- confused + overwhelmed
- defensive + confused

That is more realistic than forcing a single label.

### Recommended position
Multiple simultaneous states should be allowed in the model, but only in a structured and explainable way.

The system should distinguish:
- primary state
- secondary states
- inactive states
- contradictory states

This supports multiple states without collapsing complexity into a single label.

---

## 5. Should states have intensity/strength?

This is not currently required by the architecture, but it is likely useful.

The key issue is not whether states can have intensity, but whether the architecture can express it without creating hidden complexity.

### Recommended position
The design should allow intensity, but it should not be forced immediately.

That means:
- initial format: dict of active states
- optional future extension: state strength / confidence / weight

This preserves current architecture while leaving room for more nuanced inference later.

### Why this matters
Different internal states can coexist, but not all are equally strong.

Example:
- defensive = high
- overwhelmed = moderate
- calm = low

This should be representable eventually without forcing the whole system into a numeric vector today.

---

## 6. How should contradictory states be represented?

Contradictory states are likely to occur in realistic human behavior.

Examples:
- defensive + calm
- threatened + confident
- overwhelmed + focused
- confused + determined

The architecture should not silently resolve contradictions prematurely.

### Recommended approach
Represent contradictions explicitly as multiple active states rather than collapsing them into a single winner.

The system should record:
- which states are active
- which are contradictory
- which one is currently dominant or primary
- which evidence supports each state

### Do not force a single label too early
The current architecture is better suited to multiple simultaneous states because it already uses a dict-like container.

---

## 7. Should State of Mind be an input, an inferred result, or both?

It should be both.

### Input
It should be manually settable from tests, scenario setup, or external simulation.

### Inferred result
It should also be inferred from current variables when enough information is available.

### Why both is correct
This is consistent with the current architecture:
- `PersonState` already has a `state_of_mind` field
- the system already accepts it through `update_efmsomb`
- proposal systems already read it in a minimal way

This means the architecture already expects State of Mind to be part of a dynamic mental model, not just a static tag.

---

## 8. How should manually supplied State of Mind interact with an inferred State of Mind?

Manual and inferred values should not be treated as mutually exclusive or conflicting by default.

### Recommended design
- manual value is treated as explicit user/simulation input
- inferred value is treated as a model-derived interpretation
- both should be stored separately
- the system should show when they agree or conflict
- a final active state should be resolved only after comparison

Recommended fields:
- `state_of_mind` (current active or final state)
- `state_of_mind_manual` (directly supplied input)
- `state_of_mind_inferred` (derived internal estimate)
- `state_of_mind_conflict` or `state_of_mind_disagreement` (if set differs)

This is preferable to overwriting one with the other without traceability.

---

## 9. What should happen when the system does not have enough information to infer a state?

The system should avoid fabricating certainty.

### Recommended behavior
- maintain the existing explicit state if one is known
- leave the inferred state empty or `unknown`
- record which evidence was missing
- avoid forcing a guess

This is especially important because the current architecture already distinguishes between raw observations and higher-order interpretation.

### Good fallback states
- `unknown`
- `neutral`
- `mixed`
- `insufficient_data`

The exact label should be explicit, but not too speculative.

This prevents overconfidence and keeps State of Mind explainable.

---

## 10. How can State of Mind influence BehavioralTendencies without becoming an action-selection system?

This is the most important design boundary.

### Correct role
State of Mind should modulate tendency strength before competition, not decide the action itself.

### Requirements
It should:
- read the current internal mode
- adjust tendency strength only
- preserve the original tendency structure
- keep the action identity intact
- leave arbitration and competition logic in place
- remain transparent and explainable

### Incorrect role
State of Mind must not:
- directly select an action
- directly replace the proposal system
- directly produce final winner labels
- collapse multiple subsystem tendencies into one choice

This is similar to a pre-competition filter or modulation pass. It may change relative intensity, but it should not replace the existing action competition architecture.

---

## 11. What information should be recorded so we can later explain exactly why a State of Mind was inferred?

To support later explanation, the system must record evidence rather than just a final label.

### Minimum explainability record
- current `emotion`
- current `feeling`
- current `mood`
- current `arousal`
- current `self_regulation`
- current `awareness`
- current `context`
- current `environment`
- `trigger`
- active `goals`
- `values`
- `needs`
- current `behavior`
- active `habit_strength`
- any relevant `state_of_mind` input already present
- the inference method or rule that selected the state
- whether the state was manually supplied or inferred
- which states were contradictory or competing

### Recommended later extension
- `inference_confidence`
- `state_evidence` list
- `state_conflicts`
- `state_primary` / `state_secondary`
- `source_of_state` (manual, inferred, both)

This ensures the system can answer: why was this state inferred, and on what evidence?

---

## 12. Architectural risks or contradictions in the current design

### Risk 1: State of Mind is currently underspecified
The current field exists, but the architecture does not yet define what it means operationally.

### Risk 2: Confusion between affect and state
Emotion, feeling, mood, and State of Mind are conceptually distinct, but the current code often uses them interchangeably in a minimal way.

### Risk 3: state_of_mind is too easy to overwrite
The current `PersonState.update_efmsomb` allows direct assignment without a clear distinction between manual input and inferred output.

### Risk 4: Not enough separation between inference and action generation
The proposal systems already read `state_of_mind` in a minimal way, which is useful, but that risks turning State of Mind into a hidden action-selection heuristic.

### Risk 5: Unclear handling of multiple active states
The architecture allows dicts but does not define how to resolve multiple simultaneous states.

### Risk 6: Ambiguous role of awareness
Awareness is not the same as State of Mind, but it can influence perception and appraisal. The current architecture does not yet state how strongly it should feed into State of Mind.

### Risk 7: No explicit differentiation between "what the person feels" and "what the person is prepared to do"
This is the main conceptual boundary the design must preserve.

### Risk 8: Proposed modulation can become action selection if not constrained
If State of Mind starts directly choosing between actions, it will bypass the existing architecture. It must remain a strength modulation layer, not a replacement for competition.

---

## Recommended final architecture

The recommended final architecture for a future implementation is:

```text
PersonState
  ↓
EFMSOMB Layer
  ├── Emotion
  ├── Feeling
  ├── Mood
  ├── Behavior
  └── State of Mind
         ↓
  Context + appraisal + expectations + awareness + arousal + regulation
         ↓
  State Inference Layer
  ├── manual state input
  ├── inferred state estimate
  └── state conflict/consistency tracking
         ↓
  StateModulator
  └── modulates BehavioralTendency strength only
         ↓
  CompetitionEngine
         ↓
  Arbitration
         ↓
  DecisionResult
```

### Final recommendation
The best architecture is:
- keep `state_of_mind` as a dict-like multi-state representation;
- allow both manual and inferred values;
- preserve EFMSOMB separation explicitly;
- use State of Mind as a modulation layer, not as an action selector;
- record all evidence used for inference;
- keep the final decision pipeline intact.

This is the most compatible architecture with the rest of the project and the most faithful to the existing implementation.
