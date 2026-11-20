# F-Layer Design Artifact

Status: provisional final audit decision; stable specification for implementation review.
Scope: phenomenological felt-quality descriptors for the EFMSOMB taxonomy.

## 1. Architectural boundary

This layer is intentionally distinct from E, M, S, and B.

- E asks: What emotion is occurring?
- F asks: What does the state feel like from the inside?
- M asks: What background emotional tone is persisting over time?
- S asks: What mental/interpretive/attentional state is the person operating from?
- B asks: What is the person doing or selecting?

The guiding rule is simple:

> F is not a second emotion taxonomy. It is an orthogonal library of felt-quality descriptors that can be layered onto multiple E states.

---

## 2. Final F library (approved audit set)

The current audit accepts the following node set as the F-layer specification.

| ID | Final F node | Strict definition | What it is not | Example phenomenological wording | Possible E mappings | Boundary notes | Audit status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | Tension | A felt strain or pull in the body/mind, experienced as internal tightness, muscular load, or unresolved activation. | Not a general intensity measure; not a trigger; not an appraisal. | “My chest feels tight,” “I’m coiled,” “everything feels stretched.” | Fear, anxiety, anger, grief | Keep if framed as felt quality, not as a cause or action tendency. | ✅ Keep |
| F2 | Constriction | A subjective narrowing or closing of the self, perceptual field, or inner space; the sense of being boxed in or reduced. | Not a behavior or avoidance strategy; not “being scared” itself. | “I feel compressed,” “everything closes in,” “I can’t expand.” | Fear, shame, sadness, anger | Distinct from tension because it is narrowing/closing rather than merely strain. | ✅ Keep |
| F3 | Heaviness | A felt burden, weightedness, or drag that slows inner movement and makes the experience feel physically and emotionally loaded. | Not sadness by itself; not fatigue as a general bodily state. | “Everything feels weighted,” “I feel dragged down,” “there’s a load in me.” | Sadness, grief, guilt, exhaustion-like states | Keep as a phenomenological texture, not as a mood label. | ✅ Keep |
| F4 | Affective Numbing | Reduced responsiveness or emotional contact; a dampening or deadening of affective access that blunts feeling and reactivity. | Not flatness as a mood state per se; not the same as low arousal or boredom. | “I feel detached from my feelings,” “nothing is reaching me,” “it all feels muted.” | Grief, shock, trauma-linked states, prolonged fear | Reworded from a looser numbness label to emphasize dampened affective access. | ✅ Reword + keep |
| F5 | Warmth/Expansion | A felt opening, softening, or upward/broadening quality; sense of ease, radiance, or inner release. | Not social affection itself; not general positivity. | “I feel open,” “my chest expands,” “I’m softening.” | Joy, love, relief, affection | Distinct from E-level warmth because it characterizes the subjective felt texture. | ✅ Keep |
| F6 | Felt-pull / Subjective Imperative | An internal directional force: the sense that something is compelling, urgent, or action-leaning without yet being a fully articulated plan or explicit behavior. | Not an action; not a decision; not a motive by itself. | “I feel pulled toward it,” “I can’t ignore this,” “there is a strong inner push.” | Fear, urge-driven states, desire, compulsion, conflict | Reworded to emphasize felt compulsion rather than motivation or objective goal. | ✅ Reword + keep |
| F7 | Apprehensive Foreboding | A diffuse, looming anticipation of negative outcome, experienced as a sense that something bad is coming even before a precise threat is named. | Not a named emotion; not a trigger; not a full appraisal of danger. | “Something bad is coming,” “there is a dread in the air,” “I feel the sense of doom.” | Fear, anxiety, anticipatory grief | Reworded to make clear this is anticipatory affective atmosphere, not an E label. | ✅ Reword + keep |
| F8 | Agitation/Restlessness | A disturbed kinetic quality: inner turbulence, inability to settle, urge to move, discharge, or escalate. | Not a behavior output; not merely high arousal. | “I’m restless,” “I can’t settle,” “my system is buzzing.” | Anxiety, anger, excitement, fear | Keep as a felt-quality descriptor rather than a behavior pattern. | ✅ Keep |
| F9 | Emptiness/Hollowing | A void-like or depleted inner quality, often experienced as missingness, loss of pressure, or inner absence. | Not merely sadness; not a cognitive belief about lack. | “I feel hollow,” “there is a void,” “my inner space feels empty.” | Grief, sadness, loss, withdrawal | Distinct from low energy or fatigue; the key feature is internal vacancy. | ✅ Keep |
| F10 | Pressure/Surging-Heat | A rise of internal force, heat, and buildup that feels like pressure or escalation beneath the surface. | Not a behavioral outburst; not a full emotion; not a generic intensity metric. | “I feel hot under the skin,” “pressure is building,” “something is surging up.” | Anger, fear, panic, excitement | Maintain as one bodily felt-quality node rather than splitting into separate heat and pressure labels. | ✅ Keep |
| F12 | Depersonalization-style Detachment | A felt estrangement from the self, as if the person is observing from outside or the self feels strangely absent, diffuse, or not fully present. | Not mere calm; not general withdrawal; not just low engagement. | “It feels unreal,” “I’m watching myself from outside,” “I’m not fully here.” | Shock, trauma, panic, dissociation-linked states | Reworded to preserve the phenomenological boundary without importing psychiatric diagnosis. | ✅ Reword + keep |

### F11 status

| ID | Final disposition | Rationale |
| --- | --- | --- |
| F11 | Clarity/Focused-alertness → move to S | This is not a felt-quality descriptor in the same sense as the others; it is closer to interpretive/attentional organization and belongs in the S-layer. |

---

## 3. Boundary rules for implementation

The following are not valid F nodes when used as standalone F entries:

- intensity alone (e.g., high/low intensity)
- appraisal content (e.g., threat assessment, injustice, loss meaning)
- trigger/target labels (e.g., social rejection, betrayal, danger itself)
- behavior/action tendencies (e.g., avoidance, confrontation, withdrawal)
- physiology-only labels without phenomenological import (e.g., rapid heartbeat as a pure bodily event)
- emotion labels disguised as feeling labels (e.g., fear, anger, grief, joy)

A valid F node must describe the subjective felt quality of an ongoing state in a way that can be recognized across multiple emotional contexts.

---

## 4. Inter-layer examples

These examples show the intended separation:

- E = Fear
- F = Constriction + Tension + Apprehensive Foreboding
- M = Gloomy
- S = Threat-focused / narrowed attention
- B = Avoidance

This is cleaner than collapsing all five dimensions into one generic emotion bucket.

---

## 5. Audit verdict

The F-layer is internally coherent as a distinct phenomenological library.

The accepted set is intentionally narrow and stable:

- F1 Tension
- F2 Constriction
- F3 Heaviness
- F4 Affective Numbing
- F5 Warmth/Expansion
- F6 Felt-pull / Subjective Imperative
- F7 Apprehensive Foreboding
- F8 Agitation/Restlessness
- F9 Emptiness/Hollowing
- F10 Pressure/Surging-Heat
- F12 Depersonalization-style Detachment

The only rejected candidate for the F-layer is:

- F11 Clarity/Focused-alertness → moved to S

This should be treated as the current audited specification for implementation. The YAML version should be checked against this artifact before new F entries are added.
