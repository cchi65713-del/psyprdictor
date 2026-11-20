from registry import Registry
from activation import ActivationEngine
from box import Box
from knowledge import *
from efmsomb_taxonomy import (
    BehaviorSignature,
    EmotionState,
    FeelingState,
    MoodState,
    StateOfMindState,
)
from memory import Memory
from experience import Experience
from pattern import PatternRecognizer
from pattern_strength import PatternStrength
from pattern_consistency import PatternConsistency
from prediction import PredictionEngine
from pattern_id import PatternID
from outcome import PatternOutcome
from probability import ProbabilityEngine
from pattern_learner import PatternLearner
from context_memory import ContextMemory
from prediction_fusion import PredictionFusion
from datetime import datetime, timedelta
from prediction_explanation import PredictionExplanation
from awareness_anchor import AwarenessAnchor
from metacognition import Metacognition
from system_memory import SystemMemory
from system_influence import SystemInfluence
from self_learning import SelfLearning
from pattern_adaptation import PatternAdaptation
from adaptive_probability import AdaptiveProbability
from feedback import FeedbackLearner
from person_state import PersonState
from memory_sync import sync_system_to_person, sync_person_to_system
from action_selection import (
    suggest_actions,
    ActionSelector,
    propose_goal_directed,
    propose_habitual,
    propose_reactive,
)
from arbitration import arbitrate
from habit_formation import update_habit_strengths
from learning_bridge import LearningBridge

person_state = PersonState("Person1")
person_state.fill_actual_identity(
    name="Person1",
    roles={"self": 1.0, "defender": 0.8},
    standards=["Respect", "Boundaries"],
    values=["respect", "boundaries", "self_respect"],
    beliefs=["Respect must be defended", "Self respect matters"],
    relationships=["Difficult relationship"],
)

person_state.update_context(
    context="Someone insulted the person"
)

person_state.apply_efmsomb_taxonomy(
    emotion_state=EmotionState(
        label="E4",
        intensity=0.88,
        valence="negative",
        confidence=0.82,
    ),
    feeling_state=FeelingState(
        quality="F3",
        texture="sharp",
        intensity=0.78,
        salience=0.9,
    ),
    mood_state=MoodState(
        tone="M2",
        intensity=0.66,
        drift=0.2,
        decay=0.1,
    ),
    state_of_mind_state=StateOfMindState(
        frame="S5",
        regulation_mode="defensive",
        control_level=0.42,
        flexibility=0.55,
        cognitive_bias="hostile",
    ),
    behavior_state=BehaviorSignature(
        signature="B1",
        mode="protective",
    ),
)


# ============================================================
# PATTERN ADAPTATION
# ============================================================

pattern_adaptation = PatternAdaptation()

adaptive_probability = AdaptiveProbability(
    pattern_adaptation
)

feedback = FeedbackLearner(
    pattern_adaptation
)


# ============================================================
# 1. CREATE EFMSOMB ROOT BOXES
# ============================================================

emotion = Box("E", "Emotion", EMOTIONS, "Emotion")
feeling = Box("F", "Feeling", FEELINGS, "Feeling")
mood = Box("M", "Mood", MOODS, "Mood")

state_of_mind = Box(
    "S",
    "State of Mind",
    STATE_OF_MIND,
    "State of Mind"
)

behavior = Box(
    "B",
    "Behavior",
    BEHAVIORS,
    "Behavior"
)

belief = Box(
    "G",
    "Belief",
    BELIEFS,
    "Belief"
)

need = Box(
    "N",
    "Need",
    NEEDS,
    "Need"
)

trigger = Box(
    "T",
    "Trigger",
    TRIGGERS,
    "Trigger"
)

relationship = Box(
    "R",
    "Relationship",
    RELATIONSHIPS,
    "Relationship"
)


# ============================================================
# 2. CREATE REGISTRY
# ============================================================

registry = Registry()

registry.register(emotion)
registry.register(feeling)
registry.register(mood)
registry.register(state_of_mind)
registry.register(behavior)
registry.register(belief)
registry.register(need)
registry.register(trigger)
registry.register(relationship)


# ============================================================
# 3. EXPAND BOXES
# ============================================================

emotion.expand(registry)
feeling.expand(registry)
mood.expand(registry)
state_of_mind.expand(registry)
behavior.expand(registry)
belief.expand(registry)
need.expand(registry)
trigger.expand(registry)
relationship.expand(registry)


# ============================================================
# 4. CREATE PATTERN LEARNER
# ============================================================

pattern_learner = PatternLearner()


# ============================================================
# 5. CREATE MEMORY
# ============================================================

memory = Memory()

memory.connect_pattern_learner(
    pattern_learner
)


# ============================================================
# 6. CREATE EXPERIENCES
# ============================================================

experience1 = Experience(
    path=["E4", "F3", "M2", "S5", "B1"],
    intensity=8,
    context="Repeated conflict",
    outcome="B1",
    timestamp=datetime.now() - timedelta(days=30)
)

experience2 = Experience(
    path=["E4", "F3", "M2", "S5", "B1"],
    intensity=7,
    context="Someone insulted the person",
    outcome="B1",
    timestamp=datetime.now() - timedelta(days=14)
)

experience3 = Experience(
    path=["E4", "F3", "M2", "S2", "B4"],
    intensity=5,
    context="Minor disagreement",
    outcome="B4",
    timestamp=datetime.now() - timedelta(days=20)
)

experience4 = Experience(
    path=["E4", "F3", "M2", "S5", "B1"],
    intensity=9,
    context="Serious conflict",
    outcome="B1",
    timestamp=datetime.now() - timedelta(days=7)
)

experience5 = Experience(
    path=["E4", "F3", "M2", "S2", "B4"],
    intensity=6,
    context="Person was already frustrated",
    outcome="B4",
    timestamp=datetime.now() - timedelta(days=10)
)

experience6 = Experience(
    path=["E4", "F3", "M2", "S5", "B1"],
    intensity=8,
    context="Another serious conflict",
    outcome="B1",
    timestamp=datetime.now() - timedelta(days=1)
)


# ============================================================
# 7. STORE EXPERIENCES
# ============================================================

# IMPORTANT:
# Store each experience ONLY ONCE.

memory.store(experience1)
memory.store(experience2)
memory.store(experience3)
memory.store(experience4)
memory.store(experience5)
memory.store(experience6)


# ============================================================
# 8. AUTOMATIC PATTERN LEARNING
# ============================================================

print("\n===== AUTOMATIC LEARNING =====")

pattern_learner.show_all()


# ============================================================
# 9. CONTEXT MEMORY
# ============================================================

context_memory = ContextMemory()

context_memory.learn(
    memory.get_all()
)

context_memory.show()


# ============================================================
# 10. SHOW MEMORY
# ============================================================

print("\n==========================================")
print("MEMORY")
print("==========================================")

memory.show()


# ============================================================
# 11. ACTIVATION ENGINE
# ============================================================

engine = ActivationEngine()

engine.connect("E4", "F3")
engine.connect("F3", "M2")
engine.connect("M2", "S5")
engine.connect("S5", "B1")

engine.show_connections()


# ============================================================
# 12. CURRENT PATH
# ============================================================
# ============================================================
# 13. CURRENT CONTEXT
# ============================================================

# Derive current path and context from the central PersonState
current_path = [
    token for token in (
        person_state.emotion,
        person_state.feeling,
        person_state.mood
    ) if token
]


# Current context comes from the person state
current_context = person_state.context


# ============================================================
# 14. PATTERN RECOGNITION
# ============================================================

pattern_recognizer = PatternRecognizer(
    memory
)

pattern_recognizer.show_result(
    current_path
)

pattern_recognizer.show_next_steps(
    current_path
)

pattern_recognizer.show_next_step_probabilities(
    current_path
)

pattern_recognizer.show_possible_outcomes(
    current_path
)


# ============================================================
# 15. PATTERN ID
# ============================================================

pattern_id_engine = PatternID()

current_pattern_id = pattern_id_engine.show(
    current_path
)


# ============================================================
# 16. PATTERN MEMORY
# ============================================================

pattern_history = memory.get_by_pattern_id(
    current_pattern_id
)

print("\n===== PATTERN MEMORY =====")

print(
    f"Pattern ID: {current_pattern_id}"
)

print(
    f"Related Experiences: "
    f"{len(pattern_history)}"
)

for experience in pattern_history:

    print(
        f"  Path: {experience.path}"
    )

    print(
        f"  Intensity: "
        f"{experience.intensity}"
    )

    print(
        f"  Context: "
        f"{experience.context}"
    )

    print(
        f"  Outcome: "
        f"{experience.outcome}"
    )


# ============================================================
# 17. LEARN PATTERN OUTCOMES
# ============================================================

pattern_outcomes = PatternOutcome()

pattern_outcomes.learn_from_memory(
    memory
)

pattern_outcomes.show()


# ============================================================
# 18. LEARNED PATTERN LOOKUP
# ============================================================

learned_pattern = pattern_learner.get_pattern(
    current_path
)

print("\n===== PATTERN LOOKUP =====")

if learned_pattern:

    print("Pattern found!")

    learned_pattern.show()

else:

    print("Pattern not found.")


# ============================================================
# 19. OUTCOME PROBABILITY
# ============================================================

probability_engine = ProbabilityEngine()

if learned_pattern:

    outcomes = []

    for outcome, count in (
        learned_pattern.outcomes.items()
    ):

        for _ in range(count):

            outcomes.append(outcome)

else:

    outcomes = []


probability_engine.show(
    ".".join(current_path),
    outcomes
)


# ============================================================
# 20. PATTERN STRENGTH
# ============================================================

pattern_strength = PatternStrength()

match_count = pattern_recognizer.count_pattern(
    current_path
)

pattern_strength.show(
    current_path,
    match_count
)


# ============================================================
# 21. PATTERN CONSISTENCY
# ============================================================

pattern_consistency = PatternConsistency()

pattern_outcomes_list = (
    pattern_recognizer.get_outcomes(
        current_path
    )
)

pattern_consistency.show(
    ".".join(current_path),
    pattern_outcomes_list
)


# ============================================================
# 22. WEIGHTED / CONTEXT-AWARE PREDICTION
# ============================================================

prediction_engine = PredictionEngine()

matching_experiences = (
    pattern_recognizer.recognize(
        current_path
    )
)

prediction_engine.show_prediction(
    current_path,
    matching_experiences,
    current_context
)


# ============================================================
# 23. CONTEXT MEMORY PREDICTION
# ============================================================

context_memory.show_prediction(
    current_context
)


# ============================================================
# 24. FINAL FUSED PREDICTION
# ============================================================

pattern_scores = {}

if learned_pattern:

    total_outcomes = sum(
        learned_pattern.outcomes.values()
    )

    if total_outcomes:

        for outcome, count in (
            learned_pattern.outcomes.items()
        ):

            pattern_scores[outcome] = (
                count / total_outcomes
            ) * 100


weighted_outcome_scores = (
    prediction_engine.predict(
        current_path,
        matching_experiences,
        current_context
    )[2]
)


context_outcome_scores = (
    context_memory.predict(
        current_context
    )[2]
)


final_prediction = PredictionFusion()

final_prediction.show(
    pattern_scores,
    weighted_outcome_scores,
    context_outcome_scores
) 

print("\n===== PERSON STATE =====")
person_state.show()

# ============================================================
# 28. SYSTEM MEMORY (moved earlier so it influences action selection)
# ============================================================

system_memory = SystemMemory()

system_memory.add_belief(
    "Person1",
    "Respect must be defended"
)

system_memory.add_value(
    "Person1",
    "Self respect"
)

system_memory.add_environment(
    "Person1",
    "High conflict environment"
)

system_memory.add_history(
    "Person1",
    "Previous conflicts were ignored"
)

system_memory.add_relationship(
    "Person1",
    "Difficult relationship"
)

system_memory.add_rule(
    "Person1",
    "When attacked, respond immediately"
)

system_memory.show(
    "Person1"
)

# Merge system-level memory into the runtime person state
try:
    sync_system_to_person(system_memory, person_state, person_state.person_id)
except Exception:
    pass

# ============================================================
# 24.5 ACTION SELECTION + ARBITRATION + SYSTEM MEMORY
# ============================================================

print("\n===== ACTION SELECTION =====")

# Ensure habit strengths are initialized from past experiences before proposals
try:
    update_habit_strengths(person_state, memory, pattern_learner, pattern_id=current_pattern_id)
except Exception:
    pass

# Generate proposals from three competing systems
print("\n1. Goal-directed proposals:")
gd_scores, gd_reasons = propose_goal_directed(
    person_state,
    current_context,
    current_pattern_id,
)
for a, s in gd_scores.items():
    if s:
        print(f"   {a} -> {s:.3f}  reasons: {gd_reasons.get(a, [])}")

print("\n2. Habitual proposals:")
hb_scores, hb_reasons = propose_habitual(
    person_state,
    current_pattern_id,
    pattern_learner
)
for a, s in hb_scores.items():
    if s:
        print(f"   {a} -> {s:.3f}  reasons: {hb_reasons.get(a, [])}")

print("\n3. Reactive proposals:")
rt_scores, rt_reasons = propose_reactive(person_state)
for a, s in rt_scores.items():
    if s:
        print(f"   {a} -> {s:.3f}  reasons: {rt_reasons.get(a, [])}")

# Aggregate proposals and track contributions per-system
aggregated = {}
contributions = {}
systems = [
    ("GoalDirected", gd_scores, gd_reasons),
    ("Habitual", hb_scores, hb_reasons),
    ("Reactive", rt_scores, rt_reasons),
]

# Configurable system-level weights: increase GoalDirected influence
system_weights = {"GoalDirected": 1.5, "Habitual": 1.0, "Reactive": 1.0}

for sys_name, scores_dict, reasons_dict in systems:
    for action, score in scores_dict.items():
        if score <= 0:
            continue
        weight = system_weights.get(sys_name, 1.0)
        weighted = float(score) * float(weight)
        aggregated[action] = aggregated.get(action, 0.0) + weighted
        contributions.setdefault(action, []).append((sys_name, weighted, reasons_dict.get(action, [])))

print("\n4. Aggregated proposals (before SystemMemory):")
for a, s in aggregated.items():
    srcs = contributions.get(a, [])
    src_desc = ", ".join([f"{t[0]}(+{t[1]:.2f})" for t in srcs])
    print(f"   {a} -> {s:.3f}  sources: {src_desc}")

# Apply SystemMemory influence to aggregated scores and capture deltas/reasons
selector = ActionSelector()
pre_memory_scores = aggregated.copy()
if not pre_memory_scores:
    # If nothing proposed, fallback to baseline suggestion
    pre_memory_scores = suggest_actions(person_state, current_pattern_id, matching_experiences)

print("\n5. SystemMemory Influence:")
adjusted_scores, mem_influences = selector.apply_system_memory_influence(
    pre_memory_scores.copy(), person_state, system_memory, person_state.person_id
)

# Track memory contributions as a pseudo-system
for action in adjusted_scores:
    delta = adjusted_scores.get(action, 0.0) - pre_memory_scores.get(action, 0.0)
    if delta != 0:
        contributions.setdefault(action, []).append(("SystemMemory", float(delta), mem_influences.get(action, [])))

for action, infl_list in mem_influences.items():
    if infl_list:
        print(f"   {action}:")
        for infl in infl_list:
            print(f"     - {infl}")

print("\n6. Final competing scores (after SystemMemory):")
for a, s in adjusted_scores.items():
    srcs = contributions.get(a, [])
    src_desc = ", ".join([f"{t[0]}(+{t[1]:.2f})" for t in srcs])
    print(f"   {a} -> {s:.3f}  sources: {src_desc}")

person_state.available_actions = list(adjusted_scores.keys())
person_state.action_tendencies = adjusted_scores

# Run arbitration with source contributions
print("\n7. Arbitration:")
chosen_action, action_confidence, arbitration_reason = arbitrate(adjusted_scores, contributions)
person_state.selected_action = chosen_action
print(f"   Selected Action: {chosen_action} (confidence: {action_confidence:.1f}%)")
print(f"   Reason: {arbitration_reason}")

# Simulate execution mapping to an outcome
print("\n8. Simulated Execution:")
action_to_outcome = {
    "RespondImmediately": "B1",
    "Negotiation": "B1",
    "StayQuiet": "B4",
    "WalkAway": "B4"
}
actual_outcome = action_to_outcome.get(chosen_action, None)
person_state.execution = chosen_action
person_state.outcome = actual_outcome
print(f"   Action: {chosen_action} -> Outcome: {actual_outcome}")

# Step: Record feedback into pattern learner and pattern adaptation
print("\n9. Feedback & Learning:")
if chosen_action is not None and actual_outcome is not None:
    predicted_outcome = None
    if pattern_scores:
        predicted_outcome = adaptive_probability.predict(current_pattern_id, pattern_scores)[0]

    bridge = LearningBridge()
    diag = bridge.record_execution(
        person_state=person_state,
        person_id=person_state.person_id,
        chosen_action=chosen_action,
        actual_outcome=actual_outcome,
        pattern_id=current_pattern_id,
        pattern_path=current_path,
        context=current_context,
        memory=memory,
        pattern_learner=pattern_learner,
        pattern_adaptation=pattern_adaptation,
        predicted_outcome=predicted_outcome,
    )

    if diag.get("memory_updated"):
        print(f"   Pattern learner updated from memory: {current_path} -> {actual_outcome}")
    if current_pattern_id and diag.get("habit_strength_updated"):
        print(f"   Habit strengths refreshed for pattern {current_pattern_id}")

    try:
        if current_pattern_id and predicted_outcome is not None:
            print(f"   Pattern adaptation updated (predicted: {predicted_outcome}, actual: {actual_outcome})")
    except Exception:
        pass

# Push any updates from the runtime person state back into SystemMemory
try:
    sync_person_to_system(person_state, system_memory, person_state.person_id)
except Exception:
    pass


# ============================================================
# 25. PREDICTION EXPLANATION
# ============================================================

explainer = PredictionExplanation()

explainer.explain(
    current_path,
    current_context,
    learned_pattern,
    {
        "outcome": "B1",
        "confidence": 76.6
    },
    {
        "outcome": "B1"
    }
)


# ============================================================
# 26. AWARENESS ANCHOR
# ============================================================

anchor = AwarenessAnchor()

awareness_result = anchor.apply(
    predicted_outcome="B1",
    confidence=76.6,
    awareness_level="HIGH"
)

anchor.show(
    awareness_result
)


# ============================================================
# 27. METACOGNITION
# ============================================================

meta = Metacognition()

review = meta.review(
    prediction="B1",
    confidence=76.6,
    evidence=[
        "Pattern E4.F3.M2 appeared 6 times",
        "B1 happened 4 out of 6 times",
        "Context matched previous conflict"
    ]
)

meta.show(review)


# ============================================================
# PERSON STATE -> SYSTEM INFLUENCE (handled earlier before action selection)
# ============================================================


# ============================================================
# 30. SELF LEARNING
# ============================================================

self_learning = SelfLearning(
    pattern_learner=pattern_learner,
    pattern_adaptation=pattern_adaptation
)

# Example:
# System predicted B1,
# but actual behavior was B4.

self_learning.record_feedback(
    prediction="B1",
    actual="B4",
    context="Someone insulted the person",
    path=[
        "E4",
        "F3",
        "M2"
    ]
)

self_learning.analyze()


# ============================================================
# 31. PATTERN ADAPTATION
# ============================================================

pattern_adaptation.show()

print("\n===== LEARNED PATTERN AFTER FEEDBACK =====")
updated_pattern = pattern_learner.get_pattern([
    "E4",
    "F3",
    "M2"
])
if updated_pattern:
    updated_pattern.show()


# ============================================================
# 32. ADAPTIVE PROBABILITY
# ============================================================

# Use the AdaptiveProbability object created
# at the top of the file.

print(
    "\n===== ADAPTIVE PROBABILITY ====="
)

# We use the current pattern's original
# outcome probabilities as the input.

adaptive_scores = adaptive_probability.calculate(
    current_pattern_id,
    {
        "B1": 66.7,
        "B4": 33.3
    }
)

print(
    "\nAdaptive Outcome Scores:"
)

for outcome, score in adaptive_scores.items():

    print(
        f"  {outcome} -> "
        f"{score:.2f}"
    )

    person = PersonState("Person1")

person.update_context(
    context="Someone insulted the person",
    trigger="Insult"
)

person.apply_efmsomb_taxonomy(
    emotion_state=EmotionState(
        label="Anger",
        intensity=0.82,
        valence="negative",
        confidence=0.78,
    ),
    feeling_state=FeelingState(
        quality="Disrespected",
        texture="sharp",
        intensity=0.75,
        salience=0.8,
    ),
    mood_state=MoodState(
        tone="Irritated",
        intensity=0.64,
        drift=0.25,
        decay=0.12,
    ),
    state_of_mind_state=StateOfMindState(
        frame="Defensive",
        regulation_mode="redirect",
        control_level=0.46,
        flexibility=0.58,
        cognitive_bias="self_protective",
    ),
    behavior_state=BehaviorSignature(
        signature="B1",
        mode="protective",
    ),
)

person.add_active_pattern("E4.F3.M2")

person.show()