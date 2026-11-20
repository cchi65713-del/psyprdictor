# EFMSOMB E-Layer SME Review Package

## Source of truth
- File reviewed: [efmsomb_emotion_taxonomy_v1_proposed.yaml](efmsomb_emotion_taxonomy_v1_proposed.yaml)
- Taxonomy version: 1.1.0
- Status: PROPOSED
- Canonical base layer: E
- Canonical emotions: E1–E30
- Current Level-2 node count: 71
- Metadata Level-2 count: 71
- Historical baseline note: The historical 78-node v1.0.0 baseline was not recoverable from accessible project artifacts; no missing nodes were inferred.

## Review scope
This package is read-only and intended for subject-matter review. It preserves the YAML as the source of truth and does not change the taxonomy, registry, runtime implementation, or any other files.

## Classification legend
- Clear E: likely a genuine intrinsic emotion subtype or form
- Borderline but acceptable: within E but merits SME review for overlap or wording
- Likely outside E: may be more appraisal, behavior, motivation, physiology, or context than an intrinsic emotion subtype

## Summary matrix

| Canonical emotion | Level-2 ID | Current label | Current definition | Boundary status | Review prompt |
|---|---|---|---|---|---|
| E1 Joy | E1.1 | Social reward | Joy arising from social acceptance, connection, or belonging. | Clear E | Does this read as an intrinsic joy subtype or as a social trigger? |
| E1 Joy | E1.2 | Achievement/competence joy | Joy tied to accomplishments, mastery, or competence signals. | Clear E | Acceptable as a joy subtype? |
| E1 Joy | E1.3 | Sensory/hedonic pleasure | Joy deriving from immediate sensory pleasure or hedonic experiences. | Clear E | Acceptable as a joy subtype? |
| E2 Sadness | E2.1 | Loss-focused sadness | Sadness primarily centered on bereavement or separation. | Clear E | Is this distinct enough from general sadness? |
| E2 Sadness | E2.2 | Disappointment | Sadness from unmet expectations. | Borderline but acceptable | Is disappointment best treated as sadness form or a separate appraisal-based state? |
| E2 Sadness | E2.3 | Low-arousal sadness | A low-energy affective quality accompanying sadness (affective energy level). | Borderline but acceptable | Is this a mood-like tone rather than a sadness subtype? |
| E3 Fear | E3.1 | Immediate threat fear | Fear in response to an acute, present danger. | Clear E | Acceptable as a fear subtype? |
| E3 Fear | E3.2 | Future-oriented threat mode | Anticipatory fear oriented toward potential future threat (distinct from anxiety label). | Clear E | Acceptable as a fear mode distinct from anxiety? |
| E3 Fear | E3.3 | Social-evaluation fear | Fear centered on negative social judgment or evaluation. | Clear E | Distinct from shame or social anxiety? |
| E4 Anger | E4.1 | Injustice/violation anger | Anger characterized by perceived unfairness, insult, or violation of an important boundary. | Clear E | Acceptable as anger subtype? |
| E4 Anger | E4.2 | Target-directed anger | Anger experienced as self-directed, other-directed, or system-directed, differing in the emotional object while remaining a single anger form rather than a separate appraisal. | Clear E | Does this remain a form of anger rather than a target appraisal? |
| E4 Anger | E4.3 | Acute vs sustained anger | Anger experienced as either a brief flare or a sustained grievance, differing in temporal unfolding rather than in valence, target, or trigger. | Clear E | Is the temporal distinction sufficiently emotion-internal? |
| E5 Disgust | E5.1 | Core/physical disgust | Disgust linked to contamination or revulsion. | Clear E | Acceptable as the core disgust subtype? |
| E5 Disgust | E5.2 | Moral/social disgust | Disgust in response to moral violations or social transgressions. | Clear E | Distinct enough from moral contempt or shame? |
| E5 Disgust | E5.3 | Social-avoidant disgust | Aversion prompting distancing from people or behaviors. | Borderline but acceptable | Boundary concern: this can read as a distancing behavior tendency rather than a pure disgust form. |
| E6 Surprise | E6.1 | Valence-tagged surprise | Surprise distinguished by subsequent valence (pleasant vs unpleasant). | Borderline but acceptable | Is valence tagging a subtype of surprise or just an attribute? |
| E6 Surprise | E6.2 | Expectation-violation / novelty appraisal | Surprise grounded in novelty or expectation violation. | Borderline but acceptable | Is this still an emotion subtype or more an appraisal frame? |
| E7 Excitement | E7.1 | Anticipatory excitement | Excitement tied to expected upcoming reward or event. | Clear E | Acceptable as excitement subtype? |
| E7 Excitement | E7.2 | Consummatory enjoyment | High-arousal enjoyment at the point of reward consumption. | Clear E | Acceptable as an excitement form? |
| E8 Love | E8.1 | Attachment/commitment | Affective bond characterized by long-term attachment and commitment feelings. | Clear E | Acceptable as love subtype? |
| E8 Love | E8.2 | Passionate | High-arousal romantic or intense affiliative affect. | Clear E | Distinct from attraction or desire? |
| E8 Love | E8.3 | Care orientation | Concern and protective affect toward others. | Clear E | Acceptable as a love form rather than caregiving motivation? |
| E9 Affection | E9.1 | Warm liking | Pleasant social warmth and fondness. | Clear E | Distinct enough from E8 love? |
| E9 Affection | E9.2 | Friendly goodwill | Benevolent social orientation toward others. | Borderline but acceptable | Boundary concern: strong social orientation can read as a social attitude more than a distinct affective form. |
| E9 Affection | E9.3 | Tenderness | Gentle affective softening often toward vulnerability. | Clear E | Distinct from compassion and care? |
| E10 Grief | E10.1 | Acute bereavement reaction | Immediate, intense grief following a major loss. | Clear E | Acceptable as the core grief form? |
| E11 Anxiety | E11.1 | Anticipatory anxiety | Anxiety characterized by a forward-looking tension about possible future threat or uncertainty, experienced as diffuse apprehension rather than as a discrete external trigger. | Clear E | Acceptable as an anxiety form? |
| E11 Anxiety | E11.3 | Uncertainty sensitivity | Heightened affective response to ambiguous or uncertain contexts. | Likely outside E | Boundary concern: uncertainty sensitivity is primarily a cognitive/processing sensitivity rather than an intrinsic anxiety form. |
| E12 Frustration | E12.1 | Acute goal-block frustration | Frustration from immediate blocking of goals. | Clear E | Acceptable as a frustration subtype? |
| E12 Frustration | E12.2 | Repetitive/minor obstruction | Low-level, chronic frustration from frequent minor obstacles. | Clear E | Distinct enough from irritation? |
| E13 Irritation | E13.1 | Sensory irritation | Irritation from sensory annoyances (noise, discomfort). | Clear E | Acceptable as an irritation subtype? |
| E13 Irritation | E13.2 | Cognitive irritation | Irritation due to interruptions or cognitive friction. | Borderline but acceptable | Is this more appraisal/cognitive than emotion-internal? |
| E13 Irritation | E13.3 | Persistent annoyance | Low-grade ongoing irritation. | Clear E | Acceptable as the chronic irritation form? |
| E14 Resentment | E14.1 | Accumulated grievance | Resentment arising from a history of perceived slights. | Borderline but acceptable | Boundary concern: this emphasizes grievance history and appraisal more than a distinct emotional quality. |
| E14 Resentment | E14.2 | Moral indignation strand | Resentment linked to moral violation appraisals. | Borderline but acceptable | Is this too appraisal-heavy for E? |
| E14 Resentment | E14.3 | Relational bitterness | Resentment focused on long-term relational bitterness. | Clear E | Acceptable as a relational resentment subtype? |
| E15 Guilt | E15.1 | Agentive guilt | Guilt experienced as a self-attributed burden when the person feels personally causally responsible for harm, emphasizing agency as part of the emotion’s felt form. | Clear E | Is agency-based guilt distinct enough from other guilt forms? |
| E15 Guilt | E15.2 | Reparative guilt | Guilt characterized by an affective orientation toward restoring a perceived interpersonal or moral imbalance caused by one's actions. | Borderline but acceptable | Boundary concern: the reparative orientation is affectively meaningful, but it can drift toward moral-action restoration rather than the core guilt form. |
| E16 Shame | E16.1 | Exposure shame | Shame tied to fear of being seen or exposed. | Borderline but acceptable | Boundary concern: the exposure trigger can read as a contextual fear frame more than the shame form itself. |
| E16 Shame | E16.2 | Core self-devaluation | Shame involving negative global self-evaluation. | Clear E | Distinct enough from self-esteem or identity shame? |
| E16 Shame | E16.3 | Social vs private shame context | Distinction of shame experienced publicly versus privately. | Likely outside E | Boundary concern: public vs private is primarily contextual rather than an intrinsic shame form. |
| E17 Pride | E17.1 | Achievement pride | Pride tied to personal or group accomplishments. | Clear E | Acceptable as a pride subtype? |
| E17 Pride | E17.2 | Collective/group pride | Pride experienced as part of a group's accomplishments or identity. | Clear E | Distinct enough from self-pride? |
| E17 Pride | E17.3 | Hubristic vs healthy pride | Distinction between self-aggrandizing pride and modest, achievement-based pride. | Borderline but acceptable | Is this more evaluative than emotion-internal? |
| E18 Relief | E18.1 | Threat-resolution relief | Relief felt when a previously present threat or danger is removed. | Clear E | Acceptable as relief subtype? |
| E19 Hope | E19.1 | Goal-directed hopeful expectation | Hope tied to actionable goals and expectations. | Borderline but acceptable | Is this still emotion-internal or is it more goal/agency orientation? |
| E19 Hope | E19.2 | Passive wishfulness | Low-agency wishful anticipation. | Borderline but acceptable | Boundary concern: this sits close to longing and wishing, making it more a wish-state than a clean hope subtype. |
| E19 Hope | E19.3 | Confidence-linked hope | Hope that co-varies with subjective confidence in outcome probability. | Borderline but acceptable | Is confidence-linking an emotion subtype or a moderating variable? |
| E20 Despair | E20.1 | Helplessness appraisal | Despair dominated by perceived lack of control or efficacy. | Borderline but acceptable | Is this still despair or more a causal appraisal? |
| E20 Despair | E20.2 | Global hopelessness | Widespread pessimism and belief that desired outcomes are unattainable. | Borderline but acceptable | Boundary concern: this reads like a broader outlook or state, not only a discrete despair form. |
| E21 Envy | E21.1 | Benign/aspirational envy | Envy that motivates self-improvement without malice. | Likely outside E | Boundary concern: self-improvement motivation is outside the intrinsic emotion boundary. |
| E21 Envy | E21.2 | Malicious envy | Envy accompanied by ill will or desire to reduce the other's advantage. | Likely outside E | Boundary concern: desire to reduce another person's advantage is motivational/action-oriented rather than an intrinsic envy subtype. |
| E22 Jealousy | E22.1 | Attachment-centered jealousy | Jealousy characterized by heightened possessive concern centered on the security and exclusivity of a valued attachment relationship. | Clear E | Is the attachment-centered form sufficiently distinct from insecurity? |
| E22 Jealousy | E22.3 | Attachment-insecurity jealousy | Jealousy characterized by perceived instability or threat to the security of a valued attachment relationship. | Borderline but acceptable | Boundary concern: this blends relational insecurity with jealousy and can drift toward attachment-context description rather than a pure jealousy form. |
| E23 Contempt | E23.1 | Moral contempt | Contempt grounded in moral judgement. | Borderline but acceptable | Boundary concern: the moral basis is central, but the label can slide into appraisal rather than the core affective contempt form. |
| E23 Contempt | E23.2 | Social dismissiveness | Low regard or disdain for other individuals or groups. | Clear E | Acceptable as contempt subtype? |
| E23 Contempt | E23.3 | Dismissive contempt | Contempt characterized by a felt sense of disdain, devaluation, and psychological distancing toward a person or group regarded as beneath respect. | Clear E | Is this affective form sufficiently distinct from a social action? |
| E24 Admiration | E24.1 | Skill/excellence recognition | Admiration based on observed skill or achievement. | Borderline but acceptable | Boundary concern: it is highly evaluative and can read as an appraisal of excellence rather than the emotion itself. |
| E24 Admiration | E24.2 | Uplifting admiration | Admiration characterized by a felt sense of elevation or positive uplift in response to another's excellence or virtue. | Clear E | Distinct enough from awe-adjacent admiration? |
| E24 Admiration | E24.3 | Affective awe-adjacent recognition | Recognition with strong positive elevation bordering on awe. | Borderline but acceptable | Is this close to awe rather than admiration? |
| E25 Amazement | E25.1 | Awe | Vastness-related wonder paired with cognitive accommodation. | Borderline but acceptable | Is awe best conceptualized as a distinct emotion or a subtype of amazement? |
| E25 Amazement | E25.2 | Astonishment | Intense surprise often with immediate cognitive disruption. | Borderline but acceptable | Boundary concern: this reads as a high-intensity surprise variant and can overlap with pure surprise rather than a distinct amazement form. |
| E26 Curiosity | E26.1 | Epistemic curiosity | Curiosity characterized by heightened interest in resolving an information gap or understanding an unknown. | Clear E | Distinct enough from novelty and investigative curiosity? |
| E26 Curiosity | E26.2 | Novelty-oriented curiosity | Curiosity characterized by heightened interest arising from unfamiliar, unexpected, or novel information. | Clear E | Distinct enough from epistemic curiosity? |
| E26 Curiosity | E26.3 | Investigative curiosity | Curiosity characterized by sustained interest in examining a question, subject, or uncertainty in greater depth. | Clear E | Acceptable as an inquiry-depth curiosity form? |
| E27 Empathy | E27.1 | Affective resonance | Feeling with another, sharing in their emotional state. | Clear E | Acceptable as a core empathy mode? |
| E28 Compassion | E28.1 | Concern for suffering | The affective core of compassion focused on others' suffering. | Clear E | Distinct enough from general concern? |
| E28 Compassion | E28.2 | Compassionate concern | Compassion characterized by affective concern focused on another's suffering, distinct from enacted helping behavior. | Clear E | Distinct enough from a helping action? |
| E29 Embarrassment | E29.1 | Minor social slip embarrassment | Embarrassment from small social mistakes. | Clear E | Acceptable as an embarrassment subtype? |
| E29 Embarrassment | E29.2 | Public exposure embarrassment | Embarrassment from being exposed or judged publicly. | Clear E | Distinct enough from E29.1? |
| E29 Embarrassment | E29.3 | Social-repair embarrassment | Embarrassment characterized by concern with restoring social ease or recovering from an awkward social misstep. | Borderline but acceptable | Boundary concern: the repair orientation can drift toward social-management behavior rather than the embarrassment form itself. |
| E30 Anticipation | None currently defined | No Level-2 nodes assigned | No Level-2 nodes assigned in the current file. | Not applicable | Review whether E30 should remain without subtypes or eventually receive them. |

## Open review themes for SME consideration

### Highest-priority boundary review
- E11.3 — Uncertainty sensitivity
- E16.3 — Social vs private shame context
- E21.1 — Benign/aspirational envy
- E21.2 — Malicious envy
- E5.3 — Social-avoidant disgust
- E15.2 — Reparative guilt
- E22.3 — Attachment-insecurity jealousy
- E24.1 — Skill/excellence recognition
- E25.2 — Astonishment
- E29.3 — Social-repair embarrassment

These entries merit the strongest boundary scrutiny because they can drift toward appraisal, social context, motivation, or behavior rather than staying within an intrinsic emotion form.

### Important internal-overlap review
- E22.1 vs E22.3
- E24.2 vs E24.3 vs E25.1
- E6.1 as possible attribute rather than subtype
- E7.2 as possible enjoyment/pleasure rather than excitement
- E26.1 vs E26.2 vs E26.3
- E27.1 vs E28.1

These pairs and clusters should be reviewed for semantic distinctness without treating overlap alone as a reason to remove or replace nodes.

### Borderline but acceptable items
- E5.3 Social-avoidant disgust: emotionally coherent but still close to social avoidance and action-oriented distancing.
- E9.2 Friendly goodwill: socially oriented and tone-like, but still a meaningful positive affective form.
- E14.1 Accumulated grievance: grievance history is valid, but the node can read as a relational history dimension.
- E15.2 Reparative guilt: legitimate emotion form, but it can drift toward repair behavior if not carefully framed.
- E16.1 Exposure shame: valid shame form, though the trigger is exposure and social visibility.
- E19.2 Passive wishfulness: low-agency hope-like state; still within E, but conceptually adjacent to longing.
- E20.2 Global hopelessness: valid despair form, but still close to broader outlook or mood.
- E22.3 Attachment-insecurity jealousy: valid jealousy form, but overlaps with relationship-context description.
- E23.1 Moral contempt: valid contempt basis, but may read as a moral-evaluation frame.
- E24.1 Skill/excellence recognition: valid admiration basis, but evaluative and appraisally anchored.
- E25.2 Astonishment: valid amazement form, but close to surprise and intensity variance.
- E29.3 Social-repair embarrassment: valid emotion form, but it is close to social management and corrective behavior.

### Likely outside E
- E11.3 Uncertainty sensitivity: uncertainty sensitivity is primarily a cognitive/processing sensitivity rather than an intrinsic anxiety form.
- E16.3 Social vs private shame context: public vs private is primarily contextual rather than an intrinsic shame form.
- E21.1 Benign/aspirational envy: self-improvement motivation is outside the intrinsic emotion boundary.
- E21.2 Malicious envy: desire to reduce another person's advantage is motivational/action-oriented rather than an intrinsic envy subtype.

## Review conclusion
The current E taxonomy remains structurally stable and internally coherent at the 71-node level, but the strict E-layer boundary rule requires that a smaller set of nodes be treated as boundary-sensitive rather than automatically accepted as pure intrinsic emotion forms. The review package now reflects that distinction: some nodes remain acceptable within E, while a few are explicitly flagged as likely outside E and a larger subset is classified as borderline but acceptable for SME review rather than immediate deletion.

## Documentation status
This package is a read-only review artifact and is intentionally separate from the source YAML. It preserves the taxonomy authoritatively in [efmsomb_emotion_taxonomy_v1_proposed.yaml](efmsomb_emotion_taxonomy_v1_proposed.yaml) and provides a clean, review-oriented view for domain validation.
