# EFMSOMB Canonical Box Taxonomy Design

Status: Draft specification only; not implemented.
Scope: Architecture reconciliation and taxonomy design for the original EFMSOMB + Box-in-Box concept.

This document treats the current 30-item vocabularies in `knowledge.py` as a starting seed inventory only. They are not assumed correct simply because they already exist.

The goal is to define the canonical contents of each box in the original model:

- E = Emotion
- F = Feeling
- M = Mood
- S = State of Mind
- B = Behavior

The design preserves the original Box-in-Box principle:

- `F2`
- `F2.6`
- `F2.6.1`
- `F2.6.1.4`
- `F2.6.1.4.4`

These represent progressively deeper semantic nodes inside a parent box. They are not just strings.

---

## 1. Design principles

1. Each category is a box tree, not a flat list.
2. Each box has an identity, a definition, and an activation signature.
3. Identity and intensity are separate.
   - Example: `E4 [0.82]` means the identity is `E4` and the activation strength is `0.82`.
4. Parent boxes define the broader semantic family.
5. Child boxes refine the parent with more specific semantic meaning.
6. Multiple branches may be active simultaneously.
7. Activation may persist over time, but persistence is a property of the state episode, not the identity alone.
8. The current flat label list is used as a seed inventory only; it will be normalized into a deeper, hierarchical taxonomy before implementation.

### Structural notation

- `E4` = canonical box identity
- `anger` = canonical human-readable name
- `E4 [0.82]` = node active, intensity 0.82
- `F2.6` = deeper semantic refinement inside `F2`
- `F2.6.1.4.4` = a nested semantic path, not a string alias

Pattern Recognition should eventually observe data such as:

- `E4 [0.82]`
- `F2.6 [0.71]`
- `M3 [0.54]`
- `S5.2 [0.67]`

and potentially multiple simultaneous active branches in one episode.

---

## 2. Category boundary rules

### E: Emotion
Emotion is an immediate affective response to a stimulus or appraisal. It is usually specific, target-linked, and time-bounded.

### F: Feeling
Feeling is the embodied or subjective felt quality beneath the emotion. It often describes what the experience feels like in the body or in the subjective sense.

The final audited F-layer design artifact is maintained in [F_LAYER_SPECIFICATION.md](F_LAYER_SPECIFICATION.md). This should be treated as the current implementation specification against which any YAML or runtime schema is checked.

### M: Mood
Mood is the background affective tone that persists longer than a discrete emotion. It colors the interpretation of events.

### S: State of Mind
State of Mind is the interpretive and regulatory posture of the moment. It describes how the person is organizing their attention, stance, and response strategy.

### B: Behavior
Behavior is the observable action or response pattern. It is not the same as emotion or state of mind; it is a signature of what has been enacted or selected.

---

## 3. Current seed inventory and design adjustments

The following seed inventories come from the existing project vocabulary and are treated as a starting point, not final truth.

### Conflicts to resolve before implementation

- Same concept appears across categories:
  - `calm` exists in F and M
  - `hope` / `hopeful` appears across E/F/M/S
  - `confused` appears in F/S
- Some behavior entries are action labels rather than abstract behavior family nodes.
  - Example: `Walk Away`, `Stay Silent`, `Make a Decision`
- Some feeling entries are more like states or beliefs than low-level subjective feelings.
- Some state-of-mind labels are more like attitudes or cognitive styles than actual state-of-mind nodes.
- Some current labels are not clearly nested or hierarchical.

The taxonomy design below preserves the original semantic separation while allowing hierarchical children under each top-level node.

---

## 4. E = Emotion taxonomy

### E-level semantic rule
Emotion is a discrete, reaction-centered, immediate affect label. It is usually a parent category for subtypes and intensifications.

### E root boxes (seed inventory)

1. E1 — Joy
   - Definition: positive affect associated with reward, safety, connection, or success.
   - Trigger: success, affection, recognition, relief, play, safety.
   - Intensity: 0.0–1.0; moderate-to-high if a major goal is realized.
   - Child concepts: delight, exhilaration, playful delight, contented joy.
   - Relationship: parent = broad positive affect; children = specific joyful modes.
   - Simultaneous activation: possible with relief or affection when layered.
   - Persistence: short-lived, but can persist during an episode.
   - Distinction: distinct from general mood `M` and from feeling `F` of being accepted or valued.

2. E2 — Sadness
   - Definition: affective response to loss, separation, disappointment, or irrecoverable setback.
   - Trigger: loss, exclusion, grief, failure, abandonment.
   - Intensity: 0.0–1.0; strong when loss feels personally significant.
   - Child concepts: grief, disappointment, loneliness, melancholy.
   - Relationship: parent = broad loss-related affect; children = specific sadness subtypes.
   - Simultaneous activation: can coexist with anger or shame.
   - Persistence: can persist over time and deepen into mood.
   - Distinction: differs from `F` feelings like lonely or disconnected.

3. E3 — Fear
   - Definition: anticipatory threat response to danger or uncertainty.
   - Trigger: danger, threat, unpredictability, humiliation context, social risk.
   - Intensity: 0.0–1.0; strong under acute threat.
   - Child concepts: panic, dread, vigilance fear, social fear.
   - Relationship: parent = threat response; children = target-specific fear forms.
   - Simultaneous activation: often co-occurs with vigilance and anxiety.
   - Persistence: can remain as a state of vigilance when risk remains salient.
   - Distinction: distinct from `S` state of mind `defensive` or `avoidant`.

4. E4 — Anger
   - Definition: affective response to offense, humiliation, infringement, or blocked goal.
   - Trigger: insult, disrespect, unfairness, obstruction, betrayal.
   - Intensity: 0.0–1.0; rises sharply when personal standards are violated.
   - Child concepts: irritation, resentment, outrage, indignation.
   - Relationship: parent = angry reaction; children = more specific forms and intensities.
   - Simultaneous activation: yes; anger can coexist with shame, sadness, or fear.
   - Persistence: can persist as mood or as a defensive state.
   - Distinction: not the same as `F` feeling disrespected; anger is the emotion, disrespect is the feeling.

5. E5 — Disgust
   - Definition: rejection response to contamination, moral violation, discomfort, or aversion.
   - Trigger: contamination, moral corruption, disgusted social behavior, revulsion.
   - Intensity: 0.0–1.0; often intense but selective.
   - Child concepts: moral disgust, sensory disgust, social disgust.
   - Relationship: parent = aversion; children = target-specific aversion forms.
   - Simultaneous activation: sometimes with contempt or anger.
   - Persistence: short-to-medium duration unless the stimulus remains salient.
   - Distinction: different from contempt; disgust is aversion, contempt is social superiority.

6. E6 — Surprise
   - Definition: sudden affective response to unexpected events.
   - Trigger: sudden event, revelation, interruption, novelty.
   - Intensity: 0.0–1.0; often short-lived but high amplitude.
   - Child concepts: startle, amazement, shock, delight in surprise.
   - Relationship: parent = unexpectedness; children = subtype by valence.
   - Simultaneous activation: possible with joy, fear, or confusion.
   - Persistence: usually transient.
   - Distinction: surprise is an event response, not a mood.

7. E7 — Excitement
   - Definition: positive arousal associated with momentum, novelty, or anticipation.
   - Trigger: opportunity, challenge, stimulation, social interest.
   - Intensity: 0.0–1.0; high when the perceived value is strong.
   - Child concepts: energized anticipation, thrill, playful excitement.
   - Relationship: parent = positive high-arousal state; children = mode of excitement.
   - Simultaneous activation: yes, often alongside hope or curiosity.
   - Persistence: can persist as a response episode.
   - Distinction: distinct from mood `M` like energized or buoyant.

8. E8 — Love
   - Definition: warm attachment, care, and connection toward another or a valued target.
   - Trigger: attachment, affection, closeness, trust, belonging.
   - Intensity: 0.0–1.0; may be deep and stable.
   - Child concepts: romantic love, familial love, compassionate love.
   - Relationship: parent = attachment; children = relationship-specific forms.
   - Simultaneous activation: possible with gratitude, relief, joy.
   - Persistence: often persistent over time.
   - Distinction: love is an emotion of attachment, not merely a felt state (F) of being accepted.

9. E9 — Affection
   - Definition: gentle positive affect associated with warmth, care, and closeness.
   - Trigger: touch, reassurance, caring behavior, familiarity.
   - Intensity: 0.0–1.0; often moderate-to-high in close relationships.
   - Child concepts: tenderness, fondness, warmth, attachment.
   - Relationship: parent = benign warmth; children = relationship style variations.
   - Simultaneous activation: common with safety and calm.
   - Persistence: can persist across episodes.
   - Distinction: narrower than love; more situational and relationally warm.

10. E10 — Grief
   - Definition: affective response to irrecoverable loss or profound absence.
   - Trigger: death, separation, loss of role or identity, rupture.
   - Intensity: 0.0–1.0; often high and sustained.
   - Child concepts: bereavement, mourning, emptiness, longing.
   - Relationship: parent = loss response; children = specific loss expressions.
   - Simultaneous activation: can coexist with sadness, anger, numbness.
   - Persistence: often prolonged.
   - Distinction: distinct from sadness by depth and irreversibility.

11. E11 — Anxiety
   - Definition: future-oriented worry or anticipatory threat activation.
   - Trigger: uncertainty, risk, social evaluation, impending loss.
   - Intensity: 0.0–1.0; can become intense and escalating.
   - Child concepts: uncertainty anxiety, social anxiety, existential anxiety.
   - Relationship: parent = anticipatory unease; children = source-specific forms.
   - Simultaneous activation: yes, often with fear or vigilance.
   - Persistence: can persist as mood-like background unease.
   - Distinction: differs from fear by future orientation and uncertainty.

12. E12 — Frustration
   - Definition: emotion triggered by blocked goal pursuit or repeated interference.
   - Trigger: repeated obstacles, delays, unmet effort, frustration with others.
   - Intensity: 0.0–1.0; rises with near misses and repeated blockages.
   - Child concepts: impatience, irritation, resistance, urge to act.
   - Relationship: parent = obstructed effort; children = subtypes by source and tone.
   - Simultaneous activation: often with anger or irritation.
   - Persistence: moderate; can become a mood if repeated.
   - Distinction: not the same as general mood `irritable`.

13. E13 — Irritation
   - Definition: low-grade aversive emotion caused by nagging or low-level nuisance.
   - Trigger: petty annoyances, interruption, repetition, noise, intrusion.
   - Intensity: 0.0–1.0; usually moderate.
   - Child concepts: vexation, annoyance, impatience.
   - Relationship: parent = nuisance-induced response; children = more specific annoyance forms.
   - Simultaneous activation: yes, often with frustration.
   - Persistence: typically short-lived, but can escalate.
   - Distinction: lower intensity than anger but more diffuse.

14. E14 — Resentment
   - Definition: sustained anger related to repeated unfairness or unaddressed grievance.
   - Trigger: recurring injury, unfair treatment, ignored boundary, burden.
   - Intensity: 0.0–1.0; can build over time.
   - Child concepts: bitterness, grievance, long-form offendedness.
   - Relationship: parent = grievance emotion; children = more specific forms.
   - Simultaneous activation: yes, often with sadness or contempt.
   - Persistence: strong persistence over time.
   - Distinction: unlike momentary anger, resentment is cumulative and stored.

15. E15 — Guilt
   - Definition: negative self-evaluative emotion triggered by a moral or relational breach.
   - Trigger: wrongdoing, failure to repair, perceived harm to others.
   - Intensity: 0.0–1.0; can be moderate-to-high.
   - Child concepts: remorse, self-reproach, shameful guilt.
   - Relationship: parent = self-blame emotion; children = specific self-evaluative forms.
   - Simultaneous activation: can coexist with shame or sadness.
   - Persistence: moderate; may lead to repair or self-punishment.
   - Distinction: self-focused, unlike shame which is more identity-focused.

16. E16 — Shame
   - Definition: self-conscious emotion centered on perceived defect or social failure.
   - Trigger: exposure, humiliation, criticism, failure, public inadequacy.
   - Intensity: 0.0–1.0; often intensely painful.
   - Child concepts: humiliation, self-consciousness, social shame.
   - Relationship: parent = self-conscious threat; children = more specific shame experiences.
   - Simultaneous activation: often with sadness, guilt, anger, or withdrawal.
   - Persistence: can become a self-protective state.
   - Distinction: more identity-based than guilt; guilt is about what was done, shame is about who one is.

17. E17 — Pride
   - Definition: positive self-evaluative emotion triggered by achievement or integrity.
   - Trigger: accomplishment, virtue, mastery, value-consistent action.
   - Intensity: 0.0–1.0; moderate-to-high when identity is affirmed.
   - Child concepts: dignified pride, achievement pride, moral pride.
   - Relationship: parent = status/virtue affirmation; children = different sources of pride.
   - Simultaneous activation: can coexist with joy or relief.
   - Persistence: can persist through self-concept updates.
   - Distinction: not the same as self-confidence in `F` or `S`.

18. E18 — Relief
   - Definition: rapid reduction in threat or uncertainty after a feared outcome is avoided or resolved.
   - Trigger: danger passes, conflict resolves, obligation ends.
   - Intensity: 0.0–1.0; usually strong when tension was high.
   - Child concepts: release, reassurance relief, discharge relief.
   - Relationship: parent = threat release; children = specific release types.
   - Simultaneous activation: common with gratitude, joy, or calm.
   - Persistence: short-lived but powerful.
   - Distinction: differs from contentment or calm; relief is release from threat.

19. E19 — Hope
   - Definition: positive future-oriented emotion linked to possibility and agency.
   - Trigger: opportunity, progress, meaningful change, the possibility of repair.
   - Intensity: 0.0–1.0; high when possibility feels credible.
   - Child concepts: optimism, hopeful anticipation, future trust.
   - Relationship: parent = prospective positive affect; children = way hope is directed.
   - Simultaneous activation: often with excitement or relief.
   - Persistence: can stabilize into mood or expectation.
   - Distinction: future-oriented and action-enabling, not simply mood.

20. E20 — Despair
   - Definition: affective collapse triggered by hopelessness or irreversible failure.
   - Trigger: helplessness, lost agency, no way forward, repeated defeat.
   - Intensity: 0.0–1.0; can be severe and pervasive.
   - Child concepts: hopelessness, exhaustion, surrender, numb despair.
   - Relationship: parent = loss of future possibility; children = specific forms of hopelessness.
   - Simultaneous activation: can coexist with sadness or numbness.
   - Persistence: can become a sustained emotional tone.
   - Distinction: not simply low mood; includes hopelessness and loss of future agency.

21. E21 — Envy
   - Definition: affective response to another’s valued possession or status perceived as lacking for self.
   - Trigger: comparison, status advantage, desired object or role.
   - Intensity: 0.0–1.0; strongest under compare-and-lack conditions.
   - Child concepts: resentful envy, admiration-driven envy, status envy.
   - Relationship: parent = comparison-based desire; children = target-specific forms.
   - Simultaneous activation: often with frustration or resentment.
   - Persistence: moderate; can become a mood if unresolved.
   - Distinction: differs from admiration or jealousy by focus on lacking what another has.

22. E22 — Jealousy
   - Definition: threatened attachment emotion triggered by perceived rival attention or loyalty loss.
   - Trigger: rival, social exclusion, perceived loss of attachment.
   - Intensity: 0.0–1.0; high in attachment-based social threat conditions.
   - Child concepts: relational jealousy, competitive jealousy, insecurity jealousy.
   - Relationship: parent = attachment threat; children = specific rival contexts.
   - Simultaneous activation: often with fear, anger, or insecurity.
   - Persistence: can persist over relational uncertainty.
   - Distinction: attachment-focused; envy is comparison-focused.

23. E23 — Contempt
   - Definition: social emotion of devaluation and superiority toward another.
   - Trigger: moral failure, disrespect, fraud, incompetence, social violation.
   - Intensity: 0.0–1.0; moderate-to-high if target is judged beneath self.
   - Child concepts: disdain, mockery, disgusted contempt.
   - Relationship: parent = devaluation; children = moral or social variants.
   - Simultaneous activation: common with disgust or anger.
   - Persistence: can persist if target remains devalued.
   - Distinction: differs from disgust, which is aversion; contempt is devaluation.

24. E24 — Admiration
   - Definition: positive affect oriented toward another’s excellence or virtue.
   - Trigger: competence, virtue, skill, moral quality, admirable behavior.
   - Intensity: 0.0–1.0; strongest when the value is personally important.
   - Child concepts: respect admiration, awe admiration, talent admiration.
   - Relationship: parent = positive social evaluation; children = source-specific appreciation.
   - Simultaneous activation: can coexist with inspiration, hope, or warmth.
   - Persistence: can become a continuing value orientation.
   - Distinction: positive social evaluation, not mere liking.

25. E25 — Amazement
   - Definition: intense surprise with a positive or wondrous quality.
   - Trigger: extraordinary event, discovery, marvel, exceptional success.
   - Intensity: 0.0–1.0; can spike sharply.
   - Child concepts: wonder, awe, thrill, astonishment.
   - Relationship: parent = surprise with wonder; children = valence-specific wonder modes.
   - Simultaneous activation: often with excitement or joy.
   - Persistence: usually short-lived.
   - Distinction: differs from routine surprise by high positive wonder.

26. E26 — Curiosity
   - Definition: interest-driven exploratory urge to learn or understand.
   - Trigger: novelty, uncertainty, question, need to understand.
   - Intensity: 0.0–1.0; often moderate, can become high when meaning matters.
   - Child concepts: exploratory curiosity, information curiosity, social curiosity.
   - Relationship: parent = knowledge-seeking affect; children = target-specific inquiry.
   - Simultaneous activation: common with excitement and hope.
   - Persistence: can remain active when information gap remains.
   - Distinction: not a state of mind alone; it is an affective pull toward exploration.

27. E27 — Empathy
   - Definition: affective resonance with another person’s emotional experience.
   - Trigger: another’s pain, joy, grief, need, or vulnerability.
   - Intensity: 0.0–1.0; rises with closeness or emotional salience.
   - Child concepts: compassionate empathy, emotional contagion, attunement.
   - Relationship: parent = emotional resonance; children = type of attunement.
   - Simultaneous activation: common with compassion and concern.
   - Persistence: can persist in a social interaction or relationship.
   - Distinction: differs from emotional contagion by conscious recognition and attunement.

28. E28 — Compassion
   - Definition: caring emotional response to another’s pain or suffering.
   - Trigger: suffering, need, vulnerability, helplessness in others.
   - Intensity: 0.0–1.0; strong if suffering is salient and personal.
   - Child concepts: tenderness, care, protective concern.
   - Relationship: parent = caring response; children = specific caring forms.
   - Simultaneous activation: often with empathy, sadness, or help-seeking behavior.
   - Persistence: moderate; may activate a helping response.
   - Distinction: compassion is action-supportive care, not merely shared feeling.

29. E29 — Embarrassment
   - Definition: self-conscious negative affect triggered by social exposure or mistake.
   - Trigger: social blunder, visible shame, awkwardness, attention.
   - Intensity: 0.0–1.0; often moderate-to-high.
   - Child concepts: social awkwardness, fluster, self-conscious exposure.
   - Relationship: parent = social self-exposure; children = specific expressions.
   - Simultaneous activation: common with shame or anxiety.
   - Persistence: usually short-lived unless the event remains salient.
   - Distinction: differs from shame by being strongly situational and socially triggered.

30. E30 — Anticipation
   - Definition: emotionally charged expectation of a meaningful future event.
   - Trigger: upcoming event, expected reward or threat, looming change.
   - Intensity: 0.0–1.0; becomes strong with significance or uncertainty.
   - Child concepts: excited anticipation, anxious anticipation, preparatory anticipation.
   - Relationship: parent = expectation-linked affect; children = valence and meaning variants.
   - Simultaneous activation: common with hope, fear, excitement, or anxiety.
   - Persistence: can persist until the event resolves.
   - Distinction: anticipation is future-oriented and not identical to anxiety or excitement alone.

---

## 5. F = Feeling taxonomy

### F-level semantic rule
Feeling is the embodied, subjective, immediate felt quality of the current experience. It is often more body- or quality-centered than emotion.

### F root boxes (seed inventory)

1. F1 — Loved
   - Definition: felt sense of being warmly attached and accepted.
   - Trigger: reassurance, affection, relationship safety.
   - Intensity: 0.0–1.0.
   - Child concepts: cherished, secure, accepted.
   - Relationship: parent = relational warmth; children = deeper forms of security/attachment.
   - Simultaneous activation: yes, with safety and calm.
   - Persistence: can persist as an esteem or attachment experience.
   - Distinction: feeling-level, not the same as emotion `E8 Love`.

2. F2 — Cherished
   - Definition: felt sense of being valued as uniquely important.
   - Trigger: explicit appreciation, singled-out care, belonging.
   - Intensity: 0.0–1.0.
   - Child concepts: treasured, specifically admired, protected.
   - Relationship: parent = special-value feeling; children refine the source and quality.
   - Simultaneous activation: yes, often with trust and warmth.
   - Persistence: can persist when the person feels personally valued.
   - Distinction: more specific than general acceptance or love.

3. F3 — Accepted
   - Definition: felt permission to exist without exclusion or rejection.
   - Trigger: inclusion, non-judgment, belonging, social welcome.
   - Intensity: 0.0–1.0.
   - Child concepts: welcomed, included, tolerated, nonjudged.
   - Relationship: parent = inclusion; children = forms of social acceptance.
   - Simultaneous activation: yes, with safety and connection.
   - Persistence: can stabilize into a secure relational mood.
   - Distinction: differs from admiration or respect.

4. F4 — Rejected
   - Definition: feeling of being excluded, devalued, or not wanted.
   - Trigger: exclusion, dismissal, social rejection, neglect.
   - Intensity: 0.0–1.0.
   - Child concepts: abandoned, excluded, dismissed, unchosen.
   - Relationship: parent = social exclusion; children = specific exclusion experiences.
   - Simultaneous activation: yes, often with sadness or shame.
   - Persistence: can become a stable social wound.
   - Distinction: stronger than feeling ignored; rejection is existential and relational.

5. F5 — Valued
   - Definition: felt recognition that what one contributes matters.
   - Trigger: appreciation, recognition, respect, meaningful contribution.
   - Intensity: 0.0–1.0.
   - Child concepts: useful, respected, appreciated, seen.
   - Relationship: parent = contribution-recognition; children = source-specific recognition.
   - Simultaneous activation: yes, with security or pride.
   - Persistence: can persist across a work or relationship episode.
   - Distinction: distinct from being loved or accepted.

6. F6 — Appreciated
   - Definition: felt sense of being recognized for worth or effort.
   - Trigger: thanks, praise, acknowledgments, reciprocity.
   - Intensity: 0.0–1.0.
   - Child concepts: recognized, seen, thanked, affirmed.
   - Relationship: parent = recognition; children = different recognition modalities.
   - Simultaneous activation: yes, with gratitude and pride.
   - Persistence: usually moderate.
   - Distinction: more conscious than generic warmth.

7. F7 — Ignored
   - Definition: sense of being overlooked or left out of notice.
   - Trigger: being unheard, unseen, unresponded to, not consulted.
   - Intensity: 0.0–1.0.
   - Child concepts: discounted, bypassed, overlooked, omitted.
   - Relationship: parent = low social salience; children = forms of omission.
   - Simultaneous activation: common with sadness or anger.
   - Persistence: can grow into chronic dismissal.
   - Distinction: differs from merely busy or externally distracted.

8. F8 — Unseen
   - Definition: felt sense that one is not perceived as real, significant, or present.
   - Trigger: emotional neglect, invisibility, being overlooked in a relationship.
   - Intensity: 0.0–1.0.
   - Child concepts: invisible, not recognized, not heard, not understood.
   - Relationship: parent = invisibility; children = forms of social non-recognition.
   - Simultaneous activation: often with loneliness or shame.
   - Persistence: can be durable if recurring.
   - Distinction: stronger than being ignored; it is identity-level invisibility.

9. F9 — Safe
   - Definition: felt sense of protection, non-threat, and low vulnerability.
   - Trigger: secure environment, trusted person, stable context.
   - Intensity: 0.0–1.0.
   - Child concepts: protected, secure, settled, unthreatened.
   - Relationship: parent = low-threat felt condition; children = specific senses of security.
   - Simultaneous activation: yes, with calm and trust.
   - Persistence: can remain for a long time if conditions remain stable.
   - Distinction: not simply absence of fear; it is an embodied felt security.

10. F10 — Threatened
   - Definition: felt sense of current or impending danger.
   - Trigger: attack, conflict, humiliation, criticism, intimidation.
   - Intensity: 0.0–1.0.
   - Child concepts: vulnerable, unsafe, exposed, under siege.
   - Relationship: parent = felt danger; children = target-specific threat forms.
   - Simultaneous activation: common with fear and vigilance.
   - Persistence: can persist across a confrontation episode.
   - Distinction: feeling-level, not merely state-of-mind `defensive`.

11. F11 — Comforted
   - Definition: felt relief and soothing from care, reassurance, or regulation.
   - Trigger: soothing behavior, empathy, safety, guidance.
   - Intensity: 0.0–1.0.
   - Child concepts: soothed, reassured, held, calmed.
   - Relationship: parent = regulation via support; children = soothing forms.
   - Simultaneous activation: yes, with calm and trust.
   - Persistence: moderate.
   - Distinction: differs from general safety because it is direct soothing.

12. F12 — Lonely
   - Definition: felt absence of connection or belonging.
   - Trigger: isolation, disconnection, no one to turn to, emotional separation.
   - Intensity: 0.0–1.0.
   - Child concepts: isolated, alienated, abandoned, disconnected.
   - Relationship: parent = relational deprivation; children = forms of social separation.
   - Simultaneous activation: common with sadness and low connection.
   - Persistence: can become mood-like if enduring.
   - Distinction: social absence, not merely low energy.

13. F13 — Connected
   - Definition: felt sense of relatedness, mutual belonging, and reciprocal presence.
   - Trigger: support, understanding, shared activity, reliable contact.
   - Intensity: 0.0–1.0.
   - Child concepts: attuned, close, understood, in sync.
   - Relationship: parent = relational bonding; children = dimensions of mutuality.
   - Simultaneous activation: yes, with trust and warmth.
   - Persistence: can sustain social confidence and cooperation.
   - Distinction: feeling-level counterpart to social connection.

14. F14 — Disconnected
   - Definition: felt separation, lack of attunement, or emotional distance.
   - Trigger: conflict, silence, emotional mismatch, interpersonal distance.
   - Intensity: 0.0–1.0.
   - Child concepts: distant, out-of-sync, emotionally absent, estranged.
   - Relationship: parent = relational discontinuity; children = specific forms of distance.
   - Simultaneous activation: common with loneliness, distrust, or numbness.
   - Persistence: can become sustained relational state.
   - Distinction: not the same as being alone physically.

15. F15 — Confident
   - Definition: felt capacity to act without excessive doubt.
   - Trigger: readiness, competence, mastery, support.
   - Intensity: 0.0–1.0.
   - Child concepts: capable, grounded, assured, self-possessed.
   - Relationship: parent = self-efficacy experience; children = more specific confidence states.
   - Simultaneous activation: yes, with calm or assertive state of mind.
   - Persistence: moderate; can become trait-like only through repeated success.
   - Distinction: not the same as external status or skill level.

16. F16 — Insecure
   - Definition: feeling of vulnerability, uncertainty, or unstable worth.
   - Trigger: criticism, comparison, doubt, inconsistent support.
   - Intensity: 0.0–1.0.
   - Child concepts: self-doubting, unstable, exposed, uncertain.
   - Relationship: parent = unstable self-worth; children = more specific insecurity forms.
   - Simultaneous activation: common with anxiety or shame.
   - Persistence: can be prolonged and recurrent.
   - Distinction: more subjective than actual objective risk.

17. F17 — Capable
   - Definition: felt ability to handle a task or challenge.
   - Trigger: mastery, skill, preparation, support from experience.
   - Intensity: 0.0–1.0.
   - Child concepts: competent, effective, skilled, resourceful.
   - Relationship: parent = efficacy; children = task-specific confidence.
   - Simultaneous activation: possible with calm or confidence.
   - Persistence: moderate-to-high with repeated competence.
   - Distinction: different from self-worth or pride.

18. F18 — Powerless
   - Definition: felt lack of agency or ability to influence outcomes.
   - Trigger: control loss, coercion, helplessness, passivity.
   - Intensity: 0.0–1.0.
   - Child concepts: trapped, overwhelmed, unable, constrained.
   - Relationship: parent = agency deficit; children = specific forms of constraint.
   - Simultaneous activation: common with despair or resignation.
   - Persistence: can grow into learned helplessness.
   - Distinction: not simply low effort; it is reduced agency.

19. F19 — Hopeful
   - Definition: felt sense that positive change is possible.
   - Trigger: progress, support, possibility, meaningful approach.
   - Intensity: 0.0–1.0.
   - Child concepts: optimistic, open, future-oriented, trusting.
   - Relationship: parent = possibility-positive felt state; children = future-oriented variants.
   - Simultaneous activation: yes, with anticipation or optimism.
   - Persistence: can sustain action and commitment.
   - Distinction: feeling-level version of future possibility.

20. F20 — Hopeless
   - Definition: felt absence of positive future or viable agency.
   - Trigger: repeated failure, no path forward, collapse in meaning.
   - Intensity: 0.0–1.0.
   - Child concepts: defeated, closed-off, resigned, ineffective.
   - Relationship: parent = future collapse; children = forms of resignation.
   - Simultaneous activation: common with despair and withdrawal.
   - Persistence: can become chronic mood-like state.
   - Distinction: differs from tiredness; it includes no possibility.

21. F21 — Optimistic
   - Definition: felt tendency to expect good outcomes or workable possibilities.
   - Trigger: progress, support, favorable interpretation, positive expectation.
   - Intensity: 0.0–1.0.
   - Child concepts: buoyant, future-trusting, resiliently hopeful.
   - Relationship: parent = positive future expectation; children = subtype by resilience.
   - Simultaneous activation: common with excitement or hope.
   - Persistence: medium; can color interpretation.
   - Distinction: expectation orientation rather than pure mood.

22. F22 — Discouraged
   - Definition: felt reduction in confidence or hope after setback.
   - Trigger: failure, criticism, setback, lack of progress.
   - Intensity: 0.0–1.0.
   - Child concepts: deflated, let down, diminished, stalled.
   - Relationship: parent = setback effect; children = forms of reduced motivation.
   - Simultaneous activation: often with sadness or frustration.
   - Persistence: moderate; may become mood-like.
   - Distinction: more about reduced confidence than loss of agency.

23. F23 — Calm
   - Definition: felt ease, steadiness, and low reactivity.
   - Trigger: safety, regulation, equilibrium, reduced threat.
   - Intensity: 0.0–1.0.
   - Child concepts: settled, centered, grounded, quiet.
   - Relationship: parent = low-reactivity feeling; children = states of ease and steadiness.
   - Simultaneous activation: yes, with safety and comfort.
   - Persistence: can persist as a mood or baseline.
   - Distinction: differs from emotional positivity; calm is low arousal and balance.

24. F24 — Overwhelmed
   - Definition: felt experience of excessive demand or inability to process enough at once.
   - Trigger: too many demands, high complexity, acute stress, emotional flooding.
   - Intensity: 0.0–1.0.
   - Child concepts: overloaded, flooded, crushed, overrun.
   - Relationship: parent = demand overload; children = specific overload reports.
   - Simultaneous activation: common with fear, helplessness, or panic.
   - Persistence: can be acute or lasting if stress remains.
   - Distinction: mostly a felt overload rather than simply a mood.

25. F25 — Respected
   - Definition: felt sense of being treated as worthy, valid, and non-diminished.
   - Trigger: fairness, regard, respectful treatment, dignity.
   - Intensity: 0.0–1.0.
   - Child concepts: dignified, honored, considered, treated fairly.
   - Relationship: parent = dignity experience; children = specific respect modalities.
   - Simultaneous activation: yes, with value, confidence, and calm.
   - Persistence: moderate to high when respect is consistent.
   - Distinction: differs from valued by focusing on dignity and regard.

26. F26 — Disrespected
   - Definition: felt sense of being diminished, demeaned, or morally downgraded.
   - Trigger: insult, mockery, contempt, ignored dignity.
   - Intensity: 0.0–1.0.
   - Child concepts: demeaned, humiliated, insulted, shamed.
   - Relationship: parent = dignity violation; children = specific ways respect is damaged.
   - Simultaneous activation: common with anger, shame, and defensive action.
   - Persistence: can be durable if the offense is repeated.
   - Distinction: this is a feeling layer; `E4 Anger` is the emotional response to it.

27. F27 — Understood
   - Definition: felt recognition that one’s inner reality is seen and grasped.
   - Trigger: empathic listening, accurate reflection, attunement.
   - Intensity: 0.0–1.0.
   - Child concepts: heard, grasped, mirrored, attuned.
   - Relationship: parent = recognition of inner reality; children = specific forms of attunement.
   - Simultaneous activation: yes, with connection and safety.
   - Persistence: moderate to high with attuned relationships.
   - Distinction: differs from being accepted; it is comprehension of inner reality.

28. F28 — Misunderstood
   - Definition: felt sense that one is not accurately seen or grasped.
   - Trigger: invalidation, wrong assumptions, dismissal, misreading.
   - Intensity: 0.0–1.0.
   - Child concepts: dismissed, misread, distorted, not heard.
   - Relationship: parent = misattunement; children = specific forms of distortion.
   - Simultaneous activation: common with frustration, loneliness, or shame.
   - Persistence: can become entrenched if chronic.
   - Distinction: differs from ignored by the quality of misreading, not just non-attention.

29. F29 — Satisfied
   - Definition: felt completion, enough-ness, or fulfillment in a current state.
   - Trigger: need resolution, success, enoughness, restored balance.
   - Intensity: 0.0–1.0.
   - Child concepts: fulfilled, content, complete, enough.
   - Relationship: parent = fulfillment; children = specific felt states of closure.
   - Simultaneous activation: yes, with calm or joy.
   - Persistence: moderate.
   - Distinction: differs from happiness because it can be specific and earned.

30. F30 — Unfulfilled
   - Definition: felt lack, incompletion, or inability to satisfy a meaningful need.
   - Trigger: unmet desire, blocked purpose, lack, contradiction.
   - Intensity: 0.0–1.0.
   - Child concepts: empty, starved, yearning, unsatisfied.
   - Relationship: parent = need deficit; children = specific deficits in desire or meaning.
   - Simultaneous activation: common with longing, frustration, or despair.
   - Persistence: can become a chronic gap state.
   - Distinction: a felt deficit, not a purely cognitive goal state.

---

## 6. M = Mood taxonomy

### M-level semantic rule
Mood is the background affective tone that colors perception across time. It is broader, slower, and less tied to a single trigger than emotion.

### M root boxes (seed inventory)

1. M1 — Cheerful
   - Definition: light, buoyant background tone associated with ease and social openness.
   - Trigger: low stress, positive social context, favorable events.
   - Intensity: 0.0–1.0.
   - Child concepts: lively, sparkly, lighthearted.
   - Relationship: parent = positive background tone; children = variants of lightness.
   - Simultaneous activation: yes, with warmth or sociability.
   - Persistence: moderate-to-high.
   - Distinction: not the same as a discrete emotion of joy.

2. M2 — Joyful
   - Definition: sustained positive affective resonance and open-heartedness.
   - Trigger: meaningful success, connection, meaning, reward.
   - Intensity: 0.0–1.0.
   - Child concepts: radiant, celebratory, uplifted.
   - Relationship: parent = strong positive ambient tone; children = intensities and expressions.
   - Simultaneous activation: common with optimism and sociability.
   - Persistence: can last through a social or success episode.
   - Distinction: mood-level positivity extending beyond one discrete joy event.

3. M3 — Playful
   - Definition: background tone of ease, spontaneity, and low threat.
   - Trigger: humor, novelty, social ease, creativity.
   - Intensity: 0.0–1.0.
   - Child concepts: light, animated, curious, teasing.
   - Relationship: parent = low-stakes permissive affect; children = different playful modes.
   - Simultaneous activation: yes, with curiosity or excitement.
   - Persistence: moderate.
   - Distinction: not the same as pure excitement.

4. M4 — Energetic
   - Definition: background tone of mobilization and forward momentum.
   - Trigger: agency, purpose, challenge, stimulation.
   - Intensity: 0.0–1.0.
   - Child concepts: activated, driven, aroused, mobilized.
   - Relationship: parent = high-drive tone; children = forms of mobilization.
   - Simultaneous activation: often with excitement, hope, or purpose.
   - Persistence: medium.
   - Distinction: differs from emotion `E7 Excitement` by duration and breadth.

5. M5 — Motivated
   - Definition: sustained drive toward action or achievement.
   - Trigger: meaningful goal, competence, values alignment.
   - Intensity: 0.0–1.0.
   - Child concepts: tenacious, goal-focused, directed, purpose-driven.
   - Relationship: parent = action orientation; children = different forms of drive.
   - Simultaneous activation: common with optimism and activated mood.
   - Persistence: moderate-to-high.
   - Distinction: not merely arousal; it includes goal orientation.

6. M6 — Optimistic
   - Definition: general tendency to expect good outcomes and workable future paths.
   - Trigger: context richness, progress, support, prior success.
   - Intensity: 0.0–1.0.
   - Child concepts: hopeful, trusting, resilient optimism.
   - Relationship: parent = positive expectation baseline; children = forms of future trust.
   - Simultaneous activation: yes, with hope and anticipation.
   - Persistence: sustained if conditions remain favorable.
   - Distinction: future-oriented and interpretive, not a single momentary emotion.

7. M7 — Peaceful
   - Definition: background tone of low conflict, integration, and non-reactivity.
   - Trigger: safety, steadiness, resolution, low social threat.
   - Intensity: 0.0–1.0.
   - Child concepts: settled, restful, soothed, harmonized.
   - Relationship: parent = low-volatility tone; children = modes of ease.
   - Simultaneous activation: yes, with calm and safety.
   - Persistence: often moderate-to-high.
   - Distinction: more stable than simple calm.

8. M8 — Calm
   - Definition: base tone of reduced urgency and attenuation of arousal.
   - Trigger: safety, sufficient resources, emotional regulation.
   - Intensity: 0.0–1.0.
   - Child concepts: centered, steady, quiet, unhurried.
   - Relationship: parent = low-reactivity background; children = forms of balance.
   - Simultaneous activation: yes, with safety and self-regulation.
   - Persistence: can be stable if the environment remains secure.
   - Distinction: feeling-level and mood-level calm are not identical.

9. M9 — Relaxed
   - Definition: low-stakes, low-tension background tone with body ease.
   - Trigger: rest, safety, quiet, time away from demand.
   - Intensity: 0.0–1.0.
   - Child concepts: loose, easy, unstrained, restful.
   - Relationship: parent = reduced pressure; children = variants of ease.
   - Simultaneous activation: yes, with calm and safety.
   - Persistence: moderate.
   - Distinction: body-relaxed mood differs from cognitive calm.

10. M10 — Content
   - Definition: stable satisfaction with the present state and no strong need to change it.
   - Trigger: enoughness, belonging, stability, meaningful routine.
   - Intensity: 0.0–1.0.
   - Child concepts: settled, satisfied, grounded, at ease.
   - Relationship: parent = current-state acceptance; children = forms of sufficiency.
   - Simultaneous activation: yes, with satisfaction and calm.
   - Persistence: moderate-to-high.
   - Distinction: differs from pure calm by positive enoughness.

11. M11 — Neutral
   - Definition: low-leaning baseline without strong positive or negative coloration.
   - Trigger: ordinary context, no strong personal relevance.
   - Intensity: 0.0–1.0.
   - Child concepts: baseline, uncolored, balanced, flat.
   - Relationship: parent = low-affect baseline; children = neutral variants.
   - Simultaneous activation: possible with no strong feeling or emotion.
   - Persistence: baseline state.
   - Distinction: not absence of affect but low salience affect.

12. M12 — Focused
   - Definition: stable attentional and cognitive orientation toward a task or target.
   - Trigger: meaningful objective, challenge, priority, absence of distraction.
   - Intensity: 0.0–1.0.
   - Child concepts: locked in, concentrated, task-absorbed.
   - Relationship: parent = attention bias; children = specific attention structures.
   - Simultaneous activation: possible with motivation and low emotional noise.
   - Persistence: medium.
   - Distinction: this is partly state-of-mind, not pure mood.

13. M13 — Curious
   - Definition: ambient openness to novelty and exploration.
   - Trigger: novelty, unresolved question, exploratory context.
   - Intensity: 0.0–1.0.
   - Child concepts: exploratory, wondering, interested, engaged.
   - Relationship: parent = openness to discovery; children = target-specific inquiry modes.
   - Simultaneous activation: yes, with playfulness or anticipation.
   - Persistence: can sustain inquiry episodes.
   - Distinction: mood-like openness; not the same as discrete curiosity emotion in E.

14. M14 — Hopeful
   - Definition: stable future-oriented leaning toward constructive possibility.
   - Trigger: progress, trust, opportunities, supports, resilience.
   - Intensity: 0.0–1.0.
   - Child concepts: resilient, encouraged, forward-looking, expectant.
   - Relationship: parent = positive future expectation; children = different optimistic stances.
   - Simultaneous activation: yes, with anticipation or optimism.
   - Persistence: moderate-to-high.
   - Distinction: mood-level future trust, not a single event emotion.

15. M15 — Irritable
   - Definition: reactive, low-threshold background tone of annoyance.
   - Trigger: stress, interruption, repeated intrusions, fatigue.
   - Intensity: 0.0–1.0.
   - Child concepts: quick-to-frustrate, prickly, restless, impatient.
   - Relationship: parent = low-tolerance affective tone; children = variants of irritability.
   - Simultaneous activation: common with frustration and defensive state of mind.
   - Persistence: moderate.
   - Distinction: broader than isolated emotion `E13 Irritation`.

16. M16 — Anxious
   - Definition: lingering anticipatory tension and concern.
   - Trigger: uncertainty, threat, obligations, social risk.
   - Intensity: 0.0–1.0.
   - Child concepts: uneasy, tense, preoccupied, worried.
   - Relationship: parent = sustained worry tone; children = subtype and source variations.
   - Simultaneous activation: common with vigilance and uncertainty.
   - Persistence: can become a sustained mood.
   - Distinction: mood-level unease differs from single anxiety episode.

17. M17 — Restless
   - Definition: background tone of incomplete activation, need to move or act.
   - Trigger: unresolved tension, high stimulation, confinement, urgency.
   - Intensity: 0.0–1.0.
   - Child concepts: unsettled, agitated, fidgety, energized-but-unstable.
   - Relationship: parent = unresolved kinetic activation; children = forms of agitation.
   - Simultaneous activation: common with anxiety or impatience.
   - Persistence: can remain if the cause is unresolved.
   - Distinction: not pure arousal; includes need to move and relieve tension.

18. M18 — Tense
   - Definition: background strain, vigilance, and susceptibility to activation.
   - Trigger: threat, uncertainty, conflict, social risk, pressure.
   - Intensity: 0.0–1.0.
   - Child concepts: braced, guarded, on-edge, rigid.
   - Relationship: parent = sustained strain; children = forms of guarding.
   - Simultaneous activation: common with fear, anger, and defensive state of mind.
   - Persistence: moderate-to-high in stress periods.
   - Distinction: more structural and persistent than a discrete emotion of fear.

19. M19 — Gloomy
   - Definition: persistent low, heavy, pessimistic emotional tone.
   - Trigger: disappointment, loss, prolonged low support, hopeless context.
   - Intensity: 0.0–1.0.
   - Child concepts: dim, heavy, low-energy bleak outlook.
   - Relationship: parent = sustained low tone; children = shades of bleakness.
   - Simultaneous activation: common with sadness and hopelessness.
   - Persistence: can continue over time.
   - Distinction: broader and less event-specific than sadness.

20. M20 — Melancholic
   - Definition: reflective, inward, wistful background tone.
   - Trigger: longing, loss, memory, reflection, absence.
   - Intensity: 0.0–1.0.
   - Child concepts: wistful, inward, yearning, nostalgic.
   - Relationship: parent = inward sadness tone; children = reflective variants.
   - Simultaneous activation: yes, with sadness or withdrawal.
   - Persistence: moderate.
   - Distinction: more reflective than simply sad.

21. M21 — Low
   - Definition: subdued, reduced-energy background tone marked by lesser activation.
   - Trigger: fatigue, depletion, disappointment, low support.
   - Intensity: 0.0–1.0.
   - Child concepts: depleted, flat, drained, diminished.
   - Relationship: parent = low activation, low momentum; children = subtypes of depletion.
   - Simultaneous activation: common with hopelessness or exhaustion.
   - Persistence: moderate.
   - Distinction: not identical to sadness or depression; it is a low-energy baseline.

22. M22 — Exhausted
   - Definition: sustained low-energy, depleted mood state.
   - Trigger: prolonged effort, overload, grief, stress.
   - Intensity: 0.0–1.0.
   - Child concepts: depleted, burned out, drained, empty.
   - Relationship: parent = depletion mood; children = forms of depletion.
   - Simultaneous activation: often with low motivation or numbness.
   - Persistence: can last through episodes.
   - Distinction: energy deficit, not merely sadness.

23. M23 — Tired
   - Definition: baseline reduction in motivation and responsiveness due to fatigue.
   - Trigger: overwork, insufficient rest, stress, depletion.
   - Intensity: 0.0–1.0.
   - Child concepts: worn down, sluggish, heavy, worn out.
   - Relationship: parent = fatigue mood; children = types of tiredness.
   - Simultaneous activation: common with low drive and irritability.
   - Persistence: moderate.
   - Distinction: not the same as emotional sadness or low mood.

24. M24 — Frustrated
   - Definition: sustained affective tone of obstruction and resistance.
   - Trigger: repeated blockage, interference, unsuccessful effort.
   - Intensity: 0.0–1.0.
   - Child concepts: blocked, constrained, thwarted, burned-out frustration.
   - Relationship: parent = repeated barrier mood; children = subtypes of obstruction.
   - Simultaneous activation: common with anger and impatience.
   - Persistence: medium to long when obstacles continue.
   - Distinction: more prolonged than a single emotion of frustration.

25. M25 — Agitated
   - Definition: internal restlessness and tension that accelerates response readiness.
   - Trigger: conflict, urgency, overhead, unresolved pressure.
   - Intensity: 0.0–1.0.
   - Child concepts: keyed-up, unsettled, hyper-alert, tense.
   - Relationship: parent = high arousal background; children = arousal variants.
   - Simultaneous activation: common with fear or anger.
   - Persistence: moderate if stress remains.
   - Distinction: not identical to anxiety; it is more kinetic and unsettled.

26. M26 — Withdrawn
   - Definition: reduced social engagement and inward orientation.
   - Trigger: conflict, shame, pain, overload, social threat.
   - Intensity: 0.0–1.0.
   - Child concepts: shut down, distant, guarded, self-protective.
   - Relationship: parent = reduced engagement; children = specific withdrawal modes.
   - Simultaneous activation: common with sadness, shame, or numbness.
   - Persistence: moderate-to-high if the context remains threatening.
   - Distinction: a mood-like state of inwardness, not necessarily a behavior itself.

27. M27 — Social
   - Definition: background tone of connection, sociability, and warmth toward others.
   - Trigger: relational ease, inclusion, enjoyment of company.
   - Intensity: 0.0–1.0.
   - Child concepts: affiliative, warm, talkative, cooperative.
   - Relationship: parent = social openness; children = forms of social ease.
   - Simultaneous activation: yes, with connection and trust.
   - Persistence: can be sustained across an exchange.
   - Distinction: a social orientation, not simply one emotion or one behavior.

28. M28 — Reflective
   - Definition: background pace of inward consideration and meaning-making.
   - Trigger: unresolved question, memory, insight, contemplation.
   - Intensity: 0.0–1.0.
   - Child concepts: thoughtful, meditative, contemplative, introspective.
   - Relationship: parent = inward processing mode; children = modes of reflection.
   - Simultaneous activation: common with sadness, curiosity, and self-evaluation.
   - Persistence: moderate.
   - Distinction: more cognitive and inward than purely emotional.

29. M29 — Confident
   - Definition: sustained background feeling of personal capacity and trust in self.
   - Trigger: competence, prior success, stability, secure identity.
   - Intensity: 0.0–1.0.
   - Child concepts: assured, grounded, poised, self-trusting.
   - Relationship: parent = stable self-efficacy tone; children = variants of assurance.
   - Simultaneous activation: yes, with calm or pride.
   - Persistence: often moderate-to-high.
   - Distinction: mood-level baseline of competence.

30. M30 — Unsettled
   - Definition: background tone of unease, doubt, and unresolved tension.
   - Trigger: unpredictability, anxiety, stress, life change.
   - Intensity: 0.0–1.0.
   - Child concepts: unstable, uneasy, alert, not at rest.
   - Relationship: parent = unresolved tension tone; children = forms of discomfort.
   - Simultaneous activation: common with anxiety, restlessness, or caution.
   - Persistence: medium to prolonged.
   - Distinction: more diffuse than momentary worry.

---

## 7. S = State of Mind taxonomy

### S-level semantic rule
State of Mind describes how the person is presently orienting themselves: interpretively, cognitively, and behaviorally. It is not just feeling; it is a mode of organizing experience.

### S root boxes (seed inventory)

1. S1 — Focused
   - Definition: state of selective attention and reduced distraction.
   - Trigger: meaningful task, high relevance, goal focus, reduced noise.
   - Intensity: 0.0–1.0.
   - Child concepts: deep focus, task-locked, absorbed, concentrated.
   - Relationship: parent = attention orientation; children = more specific attention modes.
   - Simultaneous activation: yes, with motivation and calm.
   - Persistence: medium.
   - Distinction: more cognitive than mood; can coexist with calm or high effort.

2. S2 — Confused
   - Definition: state of uncertainty about meaning or next step.
   - Trigger: ambiguity, inconsistency, missing information, conflicting expectations.
   - Intensity: 0.0–1.0.
   - Child concepts: uncertain, disoriented, not-yet-clarified.
   - Relationship: parent = ambiguity state; children = more specific confusion modes.
   - Simultaneous activation: can coexist with anxiety or low confidence.
   - Persistence: moderate depending on ambiguity.
   - Distinction: state-of-mind; it does not equal an emotion or feeling alone.

3. S3 — Curious
   - Definition: exploratory state of openness to learning and discovery.
   - Trigger: novelty, information gap, questions, active inquiry.
   - Intensity: 0.0–1.0.
   - Child concepts: question-seeking, inquisitive, exploratory.
   - Relationship: parent = inquiry orientation; children = specific learning behaviors.
   - Simultaneous activation: yes, with playfulness or openness.
   - Persistence: can continue while the question remains active.
   - Distinction: distinct from mere mood curiosity.

4. S4 — Determined
   - Definition: state of strong commitment to a course of action despite obstacles.
   - Trigger: mission, purpose, value alignment, challenge.
   - Intensity: 0.0–1.0.
   - Child concepts: resolute, committed, single-minded, goal-locked.
   - Relationship: parent = action commitment; children = forms of resolve.
   - Simultaneous activation: yes, with motivation and focus.
   - Persistence: moderate-to-high.
   - Distinction: stronger than mere habit; it is a driving state mode.

5. S5 — Creative
   - Definition: state of flexible, integrative, possibility-rich thinking.
   - Trigger: novel problem, art, design, brainstorming, open-ended complexity.
   - Intensity: 0.0–1.0.
   - Child concepts: imaginative, associative, divergent, exploratory.
   - Relationship: parent = possibility-generating mode; children = creativity styles.
   - Simultaneous activation: possible with curiosity and openness.
   - Persistence: moderate.
   - Distinction: not identical to mood or emotion; it is a cognitive orientation.

6. S6 — Analytical
   - Definition: state of deliberate, model-building reasoning.
   - Trigger: problem-solving, evaluation, planning, evidence review.
   - Intensity: 0.0–1.0.
   - Child concepts: systematic, evidence-seeking, procedural, data-oriented.
   - Relationship: parent = reasoning mode; children = forms of analysis.
   - Simultaneous activation: can coexist with focus or caution.
   - Persistence: moderate.
   - Distinction: task-oriented reasoning rather than emotional regulation.

7. S7 — Reflective
   - Definition: state of inward processing and meaning-making.
   - Trigger: self-evaluation, memory, unresolved conflict, learning.
   - Intensity: 0.0–1.0.
   - Child concepts: contemplative, introspective, thoughtful.
   - Relationship: parent = inward processing mode; children = forms of thoughtfulness.
   - Simultaneous activation: common with sadness or meaning-making.
   - Persistence: moderate.
   - Distinction: cognitive/meaning-making state rather than mood alone.

8. S8 — Open-minded
   - Definition: state of cognitive receptivity and low rigidity.
   - Trigger: dialogue, new information, disagreement, learning situation.
   - Intensity: 0.0–1.0.
   - Child concepts: receptive, flexible, non-defensive, exploratory.
   - Relationship: parent = cognitive flexibility; children = openness variations.
   - Simultaneous activation: yes, with curiosity and trust.
   - Persistence: moderate.
   - Distinction: different from simple being agreeable or agreeable behavior.

9. S9 — Closed-minded
   - Definition: state of rigidity, low receptivity, and resistance to disconfirming evidence.
   - Trigger: threat, ego threat, fixed beliefs, strong resistance.
   - Intensity: 0.0–1.0.
   - Child concepts: rigid, dismissive, guarded, defensive.
   - Relationship: parent = cognitive resistance; children = specific resistance modes.
   - Simultaneous activation: common with defensiveness or contempt.
   - Persistence: can last if beliefs feel threatened.
   - Distinction: cognitive state, not mere behavior.

10. S10 — Grounded
   - Definition: state of steady centeredness and contact with reality and self.
   - Trigger: regulation, self-awareness, time, clarity.
   - Intensity: 0.0–1.0.
   - Child concepts: centered, stable, anchored, embodied.
   - Relationship: parent = stabilizing orientation; children = specific versions of presence.
   - Simultaneous activation: yes, with calm and safety.
   - Persistence: moderate-to-high.
   - Distinction: strong anchoring state rather than simple calm.

11. S11 — Hopeful
   - Definition: state of expectancy that positive movement is possible.
   - Trigger: opportunity, repair, support, future possibility.
   - Intensity: 0.0–1.0.
   - Child concepts: positive-expectant, solutions-focused, upward-oriented.
   - Relationship: parent = future orientation; children = constructive expectation modes.
   - Simultaneous activation: yes, with optimism and anticipation.
   - Persistence: moderate.
   - Distinction: state-level expectancy, not a simple emotion.

12. S12 — Defensive
   - Definition: state of protective self-regulation against perceived threat or attack.
   - Trigger: insult, challenge, threat, unfairness, vulnerability.
   - Intensity: 0.0–1.0.
   - Child concepts: guard-up, counterattack, withdrawal, blame-shifting.
   - Relationship: parent = self-protection posture; children = distinct defensive strategies.
   - Simultaneous activation: yes, with anger, shame, or hypervigilance.
   - Persistence: moderate; can become chronic if threat remains salient.
   - Distinction: not merely a single emotion; it is a mode of organization and response.

13. S13 — Distracted
   - Definition: state of reduced focus due to competing internal or external stimuli.
   - Trigger: noise, stress, worry, overload, emotional interference.
   - Intensity: 0.0–1.0.
   - Child concepts: scattered, fragmented, attention-split.
   - Relationship: parent = attention fragmentation; children = differing distraction types.
   - Simultaneous activation: yes, with overwhelm or anxiety.
   - Persistence: moderate.
   - Distinction: not the same as a passive mood.

14. S14 — Judgmental
   - Definition: state of evaluating others or situations through fixed evaluative filters.
   - Trigger: threat, offense, moral difference, need for certainty.
   - Intensity: 0.0–1.0.
   - Child concepts: critical, condemning, evaluative, socially filtering.
   - Relationship: parent = evaluative stance; children = forms of assessment.
   - Simultaneous activation: can coexist with contempt or anger.
   - Persistence: moderate.
   - Distinction: cognitive bias state, not just emotion.

15. S15 — Resistant
   - Definition: state of opposing, blocking, or refusing an external or internal push.
   - Trigger: pressure, coercion, contradiction, imposed direction.
   - Intensity: 0.0–1.0.
   - Child concepts: oppositional, refusal-oriented, pushback, countering.
   - Relationship: parent = pushback orientation; children = different refusal strategies.
   - Simultaneous activation: yes, with anger or anger-like states.
   - Persistence: moderate.
   - Distinction: not identical to behavior alone; it is a stance of resistance.

16. S16 — Stressed
   - Definition: state of overloaded regulation in which coping demands exceed resources.
   - Trigger: pressure, demand, threat, uncertainty, time constraints.
   - Intensity: 0.0–1.0.
   - Child concepts: pressured, overloaded, strained, compressed.
   - Relationship: parent = resource strain; children = overload subtypes.
   - Simultaneous activation: yes, with anxiety, irritability, or low focus.
   - Persistence: medium to long if stress continues.
   - Distinction: broader than a single emotion.

17. S17 — Overloaded
   - Definition: state in which processing demands exceed manageable capacity.
   - Trigger: complexity, information load, too many tasks, emotional flooding.
   - Intensity: 0.0–1.0.
   - Child concepts: flooded, overwhelmed, overloaded, maxed-out.
   - Relationship: parent = demand-capacity mismatch; children = specific overload types.
   - Simultaneous activation: yes, with confusion and overwhelm feelings.
   - Persistence: can remain until demand drops.
   - Distinction: process-level state, not a discrete emotion.

18. S18 — Empathetic
   - Definition: state of attunement to another person's emotional reality.
   - Trigger: relational closeness, emotional disclosure, social suffering.
   - Intensity: 0.0–1.0.
   - Child concepts: attuned, caring, emotionally aware, listening.
   - Relationship: parent = social attunement mode; children = forms of empathic attunement.
   - Simultaneous activation: yes, with compassion and connection.
   - Persistence: moderate.
   - Distinction: differs from emotion `E27 Empathy` by being a relational orienting mode.

19. S19 — Reassured
   - Definition: state of reduced threat and increased trust in the present situation.
   - Trigger: reassurance, support, evidence of safety, strength restoration.
   - Intensity: 0.0–1.0.
   - Child concepts: soothed, stabilized, comforted, trusting.
   - Relationship: parent = threat reduction current mode; children = specific restoration forms.
   - Simultaneous activation: yes, with calm and safety.
   - Persistence: moderate.
   - Distinction: a regulation state rather than pure emotion.

20. S20 — Numb
   - Definition: state of reduced affective access or emotional shut-down.
   - Trigger: overload, trauma, shutdown, shock, prolonged pain.
   - Intensity: 0.0–1.0.
   - Child concepts: disconnected, flattened, shut down, dissociated.
   - Relationship: parent = reduced emotional access; children = forms of damping.
   - Simultaneous activation: yes, with withdrawal or helplessness.
   - Persistence: moderate to high.
   - Distinction: not just low mood; it is reduced emotional availability and access.

21. S21 — Aware
   - Definition: state of clear perception of self, others, and context.
   - Trigger: attention, reflection, evidence, caution.
   - Intensity: 0.0–1.0.
   - Child concepts: present, attentive, self-aware, context-aware.
   - Relationship: parent = perception mode; children = different awareness types.
   - Simultaneous activation: yes, with focus and regulation.
   - Persistence: moderate.
   - Distinction: not identical to mood or emotion.

22. S22 — Unaware
   - Definition: state of reduced sensitivity to context, self, or others.
   - Trigger: distraction, dissociation, overwhelm, narrow attention.
   - Intensity: 0.0–1.0.
   - Child concepts: preoccupied, inattentive, missing cues, not fully present.
   - Relationship: parent = low perception state; children = attention deficits.
   - Simultaneous activation: common with overload or confusion.
   - Persistence: moderate.
   - Distinction: a state of reduced awareness, not a feeling of emptiness alone.

23. S23 — Alert
   - Definition: state of readiness to pick up relevant cues and respond quickly.
   - Trigger: threat, novelty, uncertainty, important signal.
   - Intensity: 0.0–1.0.
   - Child concepts: vigilant, ready, scanning, watchful.
   - Relationship: parent = cue sensitivity; children = specific vigilance forms.
   - Simultaneous activation: yes, with tension or vigilance.
   - Persistence: medium.
   - Distinction: more orienting than fear itself.

24. S24 — Cautious
   - Definition: state of slowed action and careful evaluation before proceeding.
   - Trigger: uncertainty, risk, social sensitivity, prior harm.
   - Intensity: 0.0–1.0.
   - Child concepts: careful, guarded, risk-aware, measured.
   - Relationship: parent = risk-sensitive decision posture; children = specific caution styles.
   - Simultaneous activation: yes, with vigilance and low trust.
   - Persistence: moderate.
   - Distinction: not the same as fear; it is deliberate restraint.

25. S25 — Decisive
   - Definition: state of ready action with reduced hesitation and stable choice.
   - Trigger: sufficient information, confidence, urgency, clarity.
   - Intensity: 0.0–1.0.
   - Child concepts: assertive, direct, clear, action-ready.
   - Relationship: parent = choice orientation; children = specific types of decisiveness.
   - Simultaneous activation: yes, with confidence and focus.
   - Persistence: moderate.
   - Distinction: differs from action behavior `B` because it is a current decision posture, not the action itself.

26. S26 — Indecisive
   - Definition: state of hesitation or difficulty choosing among options.
   - Trigger: ambiguity, fear of wrong choice, overload, conflicting values.
   - Intensity: 0.0–1.0.
   - Child concepts: hesitant, stalled, unresolved, frozen.
   - Relationship: parent = decision paralysis; children = variants of indecision.
   - Simultaneous activation: common with confusion, anxiety, and overwhelm.
   - Persistence: moderate.
   - Distinction: state-of-mind of slow choice, not action itself.

27. S27 — Accepting
   - Definition: state of non-resistance and willingness to include what is present.
   - Trigger: reality, loss, uncertainty, compassionate stance.
   - Intensity: 0.0–1.0.
   - Child concepts: resigned, consenting, receptive, non-fighting.
   - Relationship: parent = absence of resistance; children = specific acceptance modes.
   - Simultaneous activation: yes, with calm and groundedness.
   - Persistence: moderate.
   - Distinction: differs from passive compliance and from pure emotion.

28. S28 — Avoidant
   - Definition: state of reducing contact, exposure, or engagement to protect from threat or discomfort.
   - Trigger: discomfort, shame, fear, conflict, overload.
   - Intensity: 0.0–1.0.
   - Child concepts: distancing, withdrawing, disengaging, minimizing risk.
   - Relationship: parent = protective disengagement; children = avoidance strategies.
   - Simultaneous activation: common with defensive, withdrawn, or threatened states.
   - Persistence: moderate-to-high if the threat remains.
   - Distinction: a strategic orientation rather than a simple behavior.

29. S29 — Observant
   - Definition: state of increased field awareness and careful monitoring.
   - Trigger: social sensitivity, risk context, pattern detection, situational curiosity.
   - Intensity: 0.0–1.0.
   - Child concepts: attentive, watchful, monitoring, tactically aware.
   - Relationship: parent = observational posture; children = contexts of attention.
   - Simultaneous activation: yes, with alertness or caution.
   - Persistence: moderate.
   - Distinction: differs from pure vigilance by being more interpretive and less threat-driven.

30. S30 — Patient
   - Definition: state of delaying action while keeping steadiness and tolerance.
   - Trigger: complexity, negotiation, time, strategic delay, waiting.
   - Intensity: 0.0–1.0.
   - Child concepts: composed, tolerant, waiting, slow-to-react.
   - Relationship: parent = delay-with-stability posture; children = patience variants.
   - Simultaneous activation: yes, with calm or caution.
   - Persistence: moderate.
   - Distinction: not a mood alone; it is a strategic state of waiting and regulation.

---

## 8. B = Behavior taxonomy

### B-level semantic rule
Behavior is the observable action or response signature. It is not the same as the underlying affect; rather, it captures the external expression, selection, or enacted pattern.

### B root boxes (seed inventory)

1. B1 — Smile
   - Definition: positive social expression of ease or warmth.
   - Trigger: affection, safety, humor, relief, successful social connection.
   - Intensity: 0.0–1.0.
   - Child concepts: soft smile, warm smile, nervous smile, confident smile.
   - Relationship: parent = affiliative expressive action; children = variants by context and emotional tone.
   - Simultaneous activation: possible with `B20 Celebrate`, `B14 Listen`, or `B11 Negotiate` in complex contexts.
   - Persistence: usually brief.
   - Distinction: observable expression, not an emotion.

2. B2 — Laugh
   - Definition: socially expressive response to humor, relief, joy, or shared ease.
   - Trigger: joke, amusement, tension release, joy.
   - Intensity: 0.0–1.0.
   - Child concepts: genuine laugh, nervous laugh, warm laugh.
   - Relationship: parent = expression of amusement or relief; children = different social forms.
   - Simultaneous activation: possible with `B20 Celebrate` or `B9 Reach Out`.
   - Persistence: brief. 
   - Distinction: differs from general social engagement because it is specifically humor/relief-linked.

3. B3 — Cry
   - Definition: expression of grief, sadness, relief, or emotional overwhelm.
   - Trigger: loss, pain, relief, intense emotional saturation.
   - Intensity: 0.0–1.0.
   - Child concepts: tears of grief, tears of relief, tears of overwhelm.
   - Relationship: parent = emotional discharge; children = context-specific forms.
   - Simultaneous activation: can coexist with `B23 Withdraw`, `B18 Hide Emotions`, or `B17 Seek Reassurance`.
   - Persistence: brief-to-medium.
   - Distinction: expressive discharge, not a single emotion label.

4. B4 — Shout
   - Definition: loud, forceful expression often tied to urgency, anger, or overwhelm.
   - Trigger: frustration, threat, conflict, excitement, surprise.
   - Intensity: 0.0–1.0.
   - Child concepts: protest shout, alarm shout, angry shout.
   - Relationship: parent = loud expression of urgency; children = causes and social contexts.
   - Simultaneous activation: yes, with confrontation or escalation.
   - Persistence: brief but intense.
   - Distinction: not all loud vocalization is the same as `B24 Confront`.

5. B5 — Argue
   - Definition: verbal contestation or defense of a position.
   - Trigger: disagreement, threat to identity, need to be heard.
   - Intensity: 0.0–1.0.
   - Child concepts: challenge, rebuttal, insistence, debate.
   - Relationship: parent = disputation; children = contestation modes.
   - Simultaneous activation: yes, with `B24 Confront` or `B25 Defend`.
   - Persistence: moderate.
   - Distinction: behavior-level contestation, not just anger.

6. B6 — Help
   - Definition: supportive action oriented toward another's need or difficulty.
   - Trigger: observed suffering, need, responsibility, empathy.
   - Intensity: 0.0–1.0.
   - Child concepts: assist, soothe, guide, repair.
   - Relationship: parent = supportive action; children = forms of helping.
   - Simultaneous activation: common with compassion and empathy.
   - Persistence: depends on need and relationship.
   - Distinction: action vs emotional alignment.

7. B7 — Avoid
   - Definition: movement away from a trigger or source of discomfort.
   - Trigger: threat, shame, conflict, exhaustion, overload.
   - Intensity: 0.0–1.0.
   - Child concepts: keep distance, disengage, sidestep, evade.
   - Relationship: parent = avoidance strategy; children = forms of escape from a trigger.
   - Simultaneous activation: yes, with `B10 Withdraw`, `B23 Hide Emotions`.
   - Persistence: can become habitual.
   - Distinction: strategic withdrawal differs from physical withdrawal behavior.

8. B8 — Stay Silent
   - Definition: withholding verbal response while monitoring context.
   - Trigger: conflict, threat, confusion, respect, caution.
   - Intensity: 0.0–1.0.
   - Child concepts: restraint, listening silence, shut-down silence.
   - Relationship: parent = non-response strategy; children = forms of controlled silence.
   - Simultaneous activation: common with caution or avoidance.
   - Persistence: moderate.
   - Distinction: differs from `B10 Withdraw` by staying present but withheld.

9. B9 — Withdraw
   - Definition: reduction of engagement and distance from the social or situational field.
   - Trigger: shame, overwhelm, threat, shutdown, rejection.
   - Intensity: 0.0–1.0.
   - Child concepts: pull back, retreat, disengage, physically move away.
   - Relationship: parent = distancing action; children = social or physical retreat modes.
   - Simultaneous activation: yes, with avoidant state-of-mind or social withdrawal.
   - Persistence: depends on the threat or pain source.
   - Distinction: behavioral output of avoidant stance.

10. B10 — Study
   - Definition: deliberate information gathering and analysis before acting.
   - Trigger: ambiguity, complexity, learning, problem-solving.
   - Intensity: 0.0–1.0.
   - Child concepts: inspect, research, read, investigate.
   - Relationship: parent = inquiry action; children = forms of data acquisition.
   - Simultaneous activation: yes, with `S6 Analytical` or `S1 Focused`.
   - Persistence: medium.
   - Distinction: action-oriented inquiry, not just curiosity.

11. B11 — Work
   - Definition: task-driven action toward goal completion or role performance.
   - Trigger: duty, objective, productivity, responsibility.
   - Intensity: 0.0–1.0.
   - Child concepts: focus work, organized work, effort work, problem work.
   - Relationship: parent = productive action; children = domain-specific action forms.
   - Simultaneous activation: yes, with goal-directed and task-focused states.
   - Persistence: moderate-to-high depending on task demands.
   - Distinction: not equivalent to a persistent mood or personality trait.

12. B12 — Walk Away
   - Definition: physically or socially moving away from a triggering context.
   - Trigger: threat, conflict, overload, insult, exhaustion.
   - Intensity: 0.0–1.0.
   - Child concepts: leave the room, exit the interaction, disengage, postpone.
   - Relationship: parent = withdrawal action; children = forms of exit.
   - Simultaneous activation: yes, with avoidance or self-protection.
   - Persistence: usually brief but can be strategic.
   - Distinction: behavior-level exit, separate from internal state `S28 Avoidant`.

13. B13 — Listen
   - Definition: attentive receptivity to another person's communication.
   - Trigger: need to understand, relational repair, respect, learning.
   - Intensity: 0.0–1.0.
   - Child concepts: active listening, hearing, validating listening.
   - Relationship: parent = receptive action; children = forms of listening.
   - Simultaneous activation: yes, with empathy or understanding.
   - Persistence: moderate dependent on conversation.
   - Distinction: social action, not just absorption in thought.

14. B14 — Ask Questions
   - Definition: effort to clarify, understand, or request meaning.
   - Trigger: uncertainty, confusion, curiosity, need for alignment.
   - Intensity: 0.0–1.0.
   - Child concepts: clarifying questions, exploratory questions, boundary questions.
   - Relationship: parent = inquiry action; children = function-specific inquiry types.
   - Simultaneous activation: common with `S3 Curious` or `S2 Confused`.
   - Persistence: moderate.
   - Distinction: action of inquiry, not purely cognitive state.

15. B15 — Apologize
   - Definition: verbal or behavioral repair following wrongdoing or hurt.
   - Trigger: harm, error, offense, conflict repair.
   - Intensity: 0.0–1.0.
   - Child concepts: sincere apology, performative apology, repair apology.
   - Relationship: parent = repair behavior; children = modes of making amends.
   - Simultaneous activation: yes, with guilt, shame, or accountability states.
   - Persistence: brief but socially meaningful.
   - Distinction: unlike `B16 Negotiate`; it focuses on repair rather than mutual agreement.

16. B16 — Negotiate
   - Definition: process of seeking mutual agreement or workable compromise.
   - Trigger: conflict, shared needs, mutual benefit, dispute resolution.
   - Intensity: 0.0–1.0.
   - Child concepts: collaborative negotiation, boundary negotiation, concession negotiation.
   - Relationship: parent = mutual-problem-solving action; children = types of bargaining.
   - Simultaneous activation: common with `S25 Decisive`, `S8 Open-minded`, or calm states.
   - Persistence: medium.
   - Distinction: different from confrontation; it seeks mutual solution.

17. B17 — Take a Break
   - Definition: pause from a conflict or task to restore regulation.
   - Trigger: overload, anger, conflict, exhaustion, too much demand.
   - Intensity: 0.0–1.0.
   - Child concepts: leave the room, step back, pause, reset.
   - Relationship: parent = procedural self-regulation action; children = different pause strategies.
   - Simultaneous activation: yes, with `S12 Defensive` or `S16 Stressed`. 
   - Persistence: brief-to-medium.
   - Distinction: restorative pause, not avoidance as a permanent stance.

18. B18 — Hide Emotions
   - Definition: controlling expression of private affect to maintain social safety or control.
   - Trigger: shame, vulnerability, conflict, social risk, public exposure.
   - Intensity: 0.0–1.0.
   - Child concepts: mask, suppress, contain, regulate display.
   - Relationship: parent = emotion regulation by concealment; children = display-control modes.
   - Simultaneous activation: common with shame, anxiety, and guarded state-of-mind.
   - Persistence: medium.
   - Distinction: expression control, not the underlying emotion itself.

19. B19 — Express Emotions
   - Definition: outwardly communicating affect to self or others.
   - Trigger: need to release, communicate, build connection, be authentic.
   - Intensity: 0.0–1.0.
   - Child concepts: verbal expression, crying, showing anger, releasing tears.
   - Relationship: parent = emotional expression; children = styles of disclosure.
   - Simultaneous activation: can coexist with `B6 Help`, `B13 Listen`, or `B3 Cry`.
   - Persistence: brief-to-medium.
   - Distinction: open expression of affect, not the emotion identity itself.

20. B20 — Celebrate
   - Definition: outward acknowledgment and enjoyment of success or connection.
   - Trigger: achievement, group success, appreciation, relief.
   - Intensity: 0.0–1.0.
   - Child concepts: encourage, cheer, affirm, mark success.
   - Relationship: parent = recognition of success; children = social expression forms.
   - Simultaneous activation: common with joy and relief.
   - Persistence: brief.
   - Distinction: social performance of success rather than internal emotion alone.

21. B21 — Reflect
   - Definition: engaged inward processing of the situation, self, or meaning.
   - Trigger: ambiguity, self-evaluation, learning, regret, integration.
   - Intensity: 0.0–1.0.
   - Child concepts: self-review, processing, integrating, analyzing.
   - Relationship: parent = inward processing action; children = reflection styles.
   - Simultaneous activation: yes, with `S7 Reflective` or `M28 Reflective`.
   - Persistence: medium.
   - Distinction: action-oriented thought rather than a static state.

22. B22 — Vent
   - Definition: external release of emotion or frustration through expression.
   - Trigger: anger, hurt, pressure, overload, need for discharge.
   - Intensity: 0.0–1.0.
   - Child concepts: complain, rant, verbal release, pressure-release.
   - Relationship: parent = emotional discharge; children = style of release.
   - Simultaneous activation: yes, with agitation or frustration.
   - Persistence: brief to medium.
   - Distinction: release behavior, not a deeper emotional category.

23. B23 — Reach Out
   - Definition: seeking support, connection, or reassurance from another.
   - Trigger: threat, loneliness, fear, need for reassurance, desire to connect.
   - Intensity: 0.0–1.0.
   - Child concepts: ask for help, contact, confide, seek support.
   - Relationship: parent = support-seeking action; children = communication strategies.
   - Simultaneous activation: yes, with empathy or connection.
   - Persistence: depends on social need and response.
   - Distinction: action to gain relational support, not merely wanting support.

24. B24 — Confront
   - Definition: direct challenge of person, behavior, or issue.
   - Trigger: boundary violation, disrespect, accusation, unfair treatment.
   - Intensity: 0.0–1.0.
   - Child concepts: challenge, assert boundary, call out, issue direct statement.
   - Relationship: parent = direct challenge; children = modes of opposition.
   - Simultaneous activation: common with anger or defensive states.
   - Persistence: medium.
   - Distinction: behavior that may follow `E4 Anger` or `S12 Defensive` but is not equivalent to them.

25. B25 — Defend
   - Definition: protective action to preserve self, role, value, or relationship.
   - Trigger: attack, accusation, threat, challenge to identity.
   - Intensity: 0.0–1.0.
   - Child concepts: protect, explain, counter, set boundary, argue for self.
   - Relationship: parent = self-protection action; children = self-protective modes.
   - Simultaneous activation: yes, with `S12 Defensive` and `E4 Anger`.
   - Persistence: moderate.
   - Distinction: action-level defense, not the emotional or state-of-mind root.

26. B26 — Agree
   - Definition: accepting another’s proposal, position, or request without strong opposition.
   - Trigger: fairness, trust, reduced threat, collaborative relationship.
   - Intensity: 0.0–1.0.
   - Child concepts: consent, confirmation, concession, acceptance.
   - Relationship: parent = assent; children = different forms of agreement.
   - Simultaneous activation: yes, with trust, calm, or social safety.
   - Persistence: depends on the situation.
   - Distinction: observable action of assent, not a mood or feeling.

27. B27 — Disagree
   - Definition: signaling non-consent or opposition to another’s view or action.
   - Trigger: value conflict, differing interpretation, boundary tension.
   - Intensity: 0.0–1.0.
   - Child concepts: refuse, rebut, object, challenge.
   - Relationship: parent = non-assent action; children = dissent types.
   - Simultaneous activation: common with judgmental state, concern, or confrontation.
   - Persistence: depends on the disagreement and relation.
   - Distinction: not the same as general conflict or state-of-mind.

28. B28 — Cooperate
   - Definition: coordinated action toward mutual objective or shared goal.
   - Trigger: shared goal, trust, negotiated agreement, supportive context.
   - Intensity: 0.0–1.0.
   - Child concepts: collaborate, coordinate, share tasks, coordinate effort.
   - Relationship: parent = aligned action; children = pairwise or group forms.
   - Simultaneous activation: yes, with empathy and social connection.
   - Persistence: moderate depending on shared objective.
   - Distinction: action-level collaboration rather than trust alone.

29. B29 — Seek Reassurance
   - Definition: requesting confirmation or comfort to reduce uncertainty.
   - Trigger: insecurity, fear, ambiguity, anxiety, fear of loss.
   - Intensity: 0.0–1.0.
   - Child concepts: ask for confirmation, check in, ask for validation.
   - Relationship: parent = reassurance-seeking behavior; children = social support strategies.
   - Simultaneous activation: common with uncertainty, insecurity, or anxiety.
   - Persistence: depends on whether reassurance is received.
   - Distinction: behavioral method of reducing uncertainty rather than only internal emotion.

30. B30 — Make a Decision
   - Definition: arrive at a concrete choice after evaluation or urgency.
   - Trigger: need to act, clear option set, pressure, commitment necessity.
   - Intensity: 0.0–1.0.
   - Child concepts: choose, commit, decide, finalize.
   - Relationship: parent = decision action; children = specific choice strategies.
   - Simultaneous activation: yes, with decisive state-of-mind and goal orientation.
   - Persistence: brief to medium depending on the decision process.
   - Distinction: action outcome, not the same as `S25 Decisive` state-of-mind.

---

## 9. Pattern Recognition and the identity-vs-strength rule

The design must preserve a strict separation:

- `E4` is a box identity
- `0.82` is activation strength
- `anger` is the canonical name
- a deeper node such as `F2.6.1.4.4` is a more specific semantic box identity

Pattern recognition should eventually observe:

- node identity
- node strength
- sequence
- breadth of simultaneously active nodes
- context
- person identity
- timing / duration

### Example pattern observation

A person may display the following within one episode:

- `E4 [0.82]` — anger identity, strong activation
- `F2.6 [0.71]` — a deeper feeling node under the broader family of disrespect / loss of dignity
- `M3 [0.54]` — mood background under playful/inward/strained conditions depending the taxonomy refinement
- `S5.2 [0.67]` — a deeper state-of-mind pattern inside a defensive or guarded mode

This is read as:

- identity of the active nodes
- strength of activation
- multiple simultaneous activations
- nested semantic branches each with their own activation value

This is not the same as storing a flat string path alone.

---

## 10. Canonical parent-child semantics for recursive nesting

The parent-child relation should be explicit:

- Parent box = broader conceptual category
- Child box = more specific branch within that category
- Deeper child = a more precise semantic refinement of the parent concept
- Example: `F2 → F2.6 → F2.6.1 → F2.6.1.4 → F2.6.1.4.4`

This should be read as:

- `F2` = the broad family
- `F2.6` = a first refinement of that family
- `F2.6.1` = a more specific semantic variant
- `F2.6.1.4` = still more precise
- `F2.6.1.4.4` = highly specific semantic node

The path encodes hierarchy, not just names.

Multiple child nodes may be active at once under the same parent, especially when a person is experiencing layered or mixed affective states.

---

## 11. Summary of conflicts between existing vocabulary and the Box-in-Box concept

1. Current vocabulary is flat and list-based.
   - The original concept expects recursive boxes, not a flat inventory.

2. Some labels overlap across categories.
   - Example: `calm`, `hope`, `curious`, `reflective`, `confident` appear in more than one category.

3. Some entries blur category boundaries.
   - For example, `State of Mind` labels are sometimes closer to action tendencies or personality dispositions than to a true mental state channel.

4. Some behavior labels are concrete actions, not abstract behavior families.
   - `Walk Away`, `Stay Silent`, `Make a Decision` are actions, but original Box-in-Box semantics expect canonical semantic boxes with nested subtypes.

5. The current system does not distinguish identity from activation strength.
   - This is fundamental to the original concept and must be preserved in the design.

6. Simultaneous multiple activations are not represented as first-class events.
   - The existing system only stores flat lists or paths and does not model a true multi-branch state graph.

---

## 12. Final design recommendation before implementation

The current taxonomy should be treated as a seed list, not as final canonical content.

The next actual implementation step should be:

1. normalize and merge the current 30-item inventories into a canonical hierarchy,
2. formally define parent-child relations for each category,
3. define the rules for node identity vs activation strength,
4. then create the recursive Box implementation and memory encoding around that structure.

This document intentionally stops before any implementation. It is a design specification only.
