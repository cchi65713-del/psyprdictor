# Personal Context / Identity Attribution Layer

Status: specification only

## Purpose

The Personal Context Layer sits between Appraisal and Meaning Attribution in the PsyPredictor pipeline.

It answers the question:

> Why does this event matter so much to this person?

This layer does not make decisions and does not choose actions. It provides stable, person-specific context that Meaning Attribution uses to generate interpretation hypotheses.

The pipeline becomes:

Event
→ Perception
→ Appraisal
→ Personal Context
→ Meaning Attribution
→ StateManager
→ StateInference
→ StateModulation
→ Competition / Arbitration

## Core intent

Meaning Attribution asks:

> What could this event mean?

Personal Context asks:

> Why does this meaning matter to this specific person?

It introduces the missing human layer between raw evaluation and interpretation:

- history
- identity beliefs
- values
- goals
- relationship context
- sensitivity patterns
- self-narratives

These factors shape the salience and emotional weight of an event, but they do not directly decide behavior.

## Architectural role

### Inputs
- event / perception data
- appraisal frames
- current EFMSOMB state
- personal context memory
- self-report evidence
- relationship metadata

### Outputs
- a structured personal context snapshot for the specific event
- relevance weights for values/goals/history
- sensitivity flags for trauma-like or high-charge memories
- relationship-specific interpretation bias
- provenance references for downstream Meaning Attribution

### Non-decision rule
The Personal Context Layer must never:
- select actions
- assign final action weights
- rank actions
- override appraisals
- generate state labels directly

It only provides context that increases or decreases the plausibility of meaning interpretations.

---
## Design principles

### 1) Person-specific, not universal
The same event can mean different things to different people. This layer exists to represent that difference explicitly.

### 2) Historical and relationship-aware
The meaning of an event depends on:
- what the person has lived through
- what they believe about themselves
- who is speaking
- how much power or closeness the other person has

### 3) Explainable
Every context signal must be traceable back to a source:
- past memory
- previous event
- self-report
- current relation metadata
- current values/goals

### 4) Privacy-conscious
Sensitive personal histories, trauma-like memories, and self-reports must be stored with explicit provenance and careful access boundaries.

### 5) Weighted and uncertain
Not every past experience is equally relevant. Some are recent, salient, or repeated. Context weighting should be confidence-based rather than absolute.

---
## Layer summary

The Personal Context Layer produces a structured bundle such as:

- PersonalHistory
- IdentityBeliefs
- ValueProfile
- GoalState
- RelationshipContext
- SensitivityProfile
- SelfNarrative

This bundle is then passed to Meaning Attribution as one input alongside the appraisal and expectation data.

---
## Data structures

### 1) PersonalHistory
Represents a person’s relevant life context.

Required fields:
- id: str
- person_id: str
- event_id: Optional[str]
- timestamp: str
- category: str
- summary: str
- emotional_charge: float 0..1
- relevance_weight: float 0..1
- recurrence_count: int
- source: str  // memory, self_report, observation, learned pattern
- provenance: dict

Examples of history entries:
- repeated public criticism
- previous financial shame
- repeated success at work
- family rejection signals
- prior humiliating experiences

Important constraints:
- History is not treated as diagnosis.
- Trauma-like memories are represented as sensitive context, not clinical status.
- Repetition matters: a pattern can shape salience much more than a single event.

### 2) IdentityBelief
Represents stable self-concepts that influence meaning.

Required fields:
- id: str
- person_id: str
- belief: str
- belief_type: str  // e.g. competence, worth, respect, control, belonging
- confidence: float 0..1
- strength: float 0..1
- source: str
- provenance: dict

Example beliefs:
- "I am someone who succeeds"
- "I am not respected"
- "I must prove myself"
- "I am a burden"
- "People see me as weak"

These beliefs are not fixed facts. They are semi-stable internal scripts that affect how new events are interpreted.

### 3) ValueProfile
Represents enduring values that affect what matters.

Required fields:
- id: str
- person_id: str
- value: str
- importance: float 0..1
- source: str
- provenance: dict

Examples:
- independence
- respect
- achievement
- security
- belonging
- competence

A value profile does not directly produce action. It changes which interpretations feel important or threatening.

### 4) GoalState
Represents active goals and goal salience.

Required fields:
- id: str
- person_id: str
- goal: str
- priority: float 0..1
- status: str  // active, blocked, threatened, achieved
- relation_to_event: Optional[str]
- source: str
- provenance: dict

Examples:
- become financially independent
- protect relationships
- improve status
- avoid public shame
- prove myself

### 5) RelationshipContext
Represents who is involved and what that relationship means.

Required fields:
- id: str
- person_id: str
- target_role: str  // friend, family, authority, stranger, rival, partner, coworker
- relationship_strength: float 0..1
- perceived_power: float 0..1
- trust: float 0..1
- status_significance: float 0..1
- source: str
- provenance: dict

This is critical because the same insult from a stranger and from a parent will not carry equal meaning.

### 6) SensitivityProfile
Represents patterns that make events especially salient or destabilizing.

Required fields:
- id: str
- person_id: str
- sensitivity_type: str  // money, status, respect, exclusion, shame, control, failure
- sensitivity_level: float 0..1
- trigger_history_count: int
- source: str
- provenance: dict

Examples:
- money shame sensitivity
- status threat sensitivity
- being called lazy or useless

This layer should identify likely hot spots, not diagnosis.

### 7) SelfNarrative
Represents how a person narrates themselves in relation to the event.

Required fields:
- id: str
- person_id: str
- narrative: str
- confidence: float 0..1
- source: str
- provenance: dict

Examples:
- "I am someone who gets overlooked"
- "I am a late bloomer"
- "I must prove myself again and again"

Self-narratives are especially important because they shape meaning and emotional weight.

---
## Context snapshot model

For a given event, the Personal Context Layer produces a snapshot like:

```text
PersonalContextSnapshot
- person_id
- event_id
- appraisal_ids
- relevant_history_ids
- relevant_identity_beliefs
- active_values
- active_goals
- relationship_context
- sensitivity_flags
- self_report_refs
- confidence
- provenance
```

This snapshot is passed into Meaning Attribution as a structured context bundle.

---
## How context feeds Meaning Attribution

Meaning Attribution should consume personal context as weighted variables, not as direct action rules.

For example:

- If the person has strong goal `financial independence`, a money-based insult may raise `challenge` and `need_to_prove_self` likelihood.
- If the person has history of financial humiliation and low perceived control, the same insult may raise `humiliation`, `rejection`, and `inadequacy` likelihood.
- If the speaker is a trusted authority figure, the event may be interpreted as status threat or fear of judgment.
- If the speaker is a stranger or rival, the event may be interpreted as disrespect or social threat.

Important rule:

The Personal Context Layer does not create final meaning labels by itself.
It modulates the probability and emotional weight of candidate interpretations.

---
## Provenance requirements

Each context element must retain traceable provenance.

Required provenance fields:
- source_type: str
- source_id: str
- event_id: Optional[str]
- observation_id: Optional[str]
- appraisal_id: Optional[str]
- memory_ref: Optional[str]
- self_report_ref: Optional[str]
- created_timestamp: str
- confidence: float

This preserves the chain:

Event
→ Perception
→ Appraisal
→ Personal Context
→ Meaning Attribution
→ StateManager

The final MeaningFrame should carry references to:
- relevant personal context entries
- memory refs
- self-report refs
- relationship metadata

---
## Privacy considerations

The Personal Context Layer deals with highly personal and potentially sensitive material.

It must preserve the following guardrails:

### 1) Minimal retention
Only keep context entries needed for relevance and interpretation.

### 2) Sensitive memory classification
History entries can be tagged as:
- neutral
- sensitive
- high-charge
- trauma-like

The layer must not diagnose, label, or pathologize a person simply because a memory is associated with shame or fear.

### 3) Access boundaries
Context elements should be readable only by the context engine and relevant downstream interpretation modules, not by arbitrary action components.

### 4) Self-report boundaries
Self-reports should be stored as evidence, not absolute truth. They must be traceable and can be weighted lower than direct observation when conflicting with direct perception.

### 5) Explainability without exposure
The system may explain why a meaning was inferred without exposing raw private content beyond a controlled interpretation log.

---
## Self-report handling

Self-reports are important inputs to context, not final truth.

Examples:
- "I felt embarrassed but it motivated me."
- "This always humiliates me when people mention money."
- "I know I act tough, but this hurt."

Design rule:

Self-reports should enter the Personal Context Layer as evidence with:
- source = self_report
- confidence = variable
- accepted_as_truth = false by default
- provenance = original report + time + relation context
- corroboration_status = unverified / partially corroborated / corroborated

This keeps self-report data useful without giving it unquestioned authority.

---
## Relationship-specific meaning shifts

The same event can be interpreted differently depending on relationship context.

Examples:

### Stranger
- likely social threat
- possible disrespect
- less identity-bearing unless there is prior social salience

### Friend
- could be a test of loyalty or social acceptance
- may land as embarrassment or rejection depending on closeness

### Family member
- may activate shame, belonging, or worth beliefs more strongly
- may trigger long-standing identity scripts

### Authority figure
- may activate fear of judgment, status threat, or compliance pressure

### Rival
- may activate challenge, status defense, prove_self

Relationship context should be a weight on the interpretation, not an override.

---
## First human test case representation

This is the canonical scenario the layer is designed to explain.

### Event
> "Someone mocks a person for being poor."

### Person A
History:
- grew up poor
- values achievement
- wants financial independence
- previous success experiences

Identity beliefs:
- "I am someone who succeeds"
- "I need to prove myself"

Values:
- independence
- achievement
- respect

Goals:
- become financially independent
- improve status

Relationship context:
- speaker = stranger or social peer

Likely context snapshot:
- sensitive to money shame
- high achievement salience
- goal threat active
- relationship threat moderate
- previous success memory boosts challenge interpretation

Likely meaning output:
- challenge
- opportunity
- need_to_prove_self
- embarrassment
- motivation
- focus

### Person B
History:
- previous money trauma
- low perceived control
- repeated humiliation around money

Identity beliefs:
- "I am not respected"
- "I am not enough"
- "People see me as inferior"

Values:
- security
- respect
- belonging

Goals:
- avoid shame
- reduce vulnerability

Relationship context:
- speaker = peer or authority figure

Likely context snapshot:
- money shame sensitivity high
- control low
- shame memory pattern active
- status threat strong

Likely meaning output:
- humiliation
- rejection
- inadequacy
- sadness
- withdrawal

This is exactly the kind of person-specific interpretive difference the layer is meant to capture.

---
## Integration contract with Meaning Attribution

The layer should produce a structure similar to:

```text
PersonalContextSnapshot {
  person_id,
  event_id,
  appraisal_ids,
  relevant_history_ids,
  identity_beliefs,
  value_profile,
  active_goals,
  relationship_context,
  sensitivity_flags,
  self_report_refs,
  confidence,
  provenance
}
```

Meaning Attribution may then use it to adjust these properties:
- personal_relevance
- confidence of candidate interpretation
- affected_values
- activated_goals
- motivation_direction
- persistence_hint
- derived_state_suggestions

The Context Layer must not produce final meaning labels or action suggestions directly.

---
## Minimal invariants

The Personal Context Layer must preserve these invariants:

1. Same event + same appraisal can produce different meaning distributions for different people.
2. Relationship and personal history are required inputs for human-like meaning generation.
3. Identity beliefs and value salience are not diagnoses; they are structural self-models.
4. All context-based inferences require provenance.
5. Self-reports are supporting evidence, not absolute truth.
6. Context influences Meaning Attribution but never bypasses it.
7. This layer does not replace the appraiser or decision engine.

---
## What this layer adds to PsyPredictor

This layer moves the system from:

> Event → Interpretation → State

toward:

> Event → Relationship → History → Identity → Meaning → State

This is the point where PsyPredictor becomes personality-aware rather than merely event-reactive.

---
## Spec status

This is a design specification only.
No Python code, no runtime implementation, no action-selection logic.

This layer is intended to be the missing foundation for the next Meaning Attribution stage and future integrated behavior modeling.
