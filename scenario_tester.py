"""
Scenario tester for PsyPredictor.
Runs multiple predefined scenarios through the existing architecture and prints diagnostics.
"""
from datetime import datetime, timedelta
from person_state import PersonState
from memory import Memory
from pattern_learner import PatternLearner
from system_memory import SystemMemory
from action_selection import (
    propose_goal_directed,
    propose_habitual,
    propose_reactive,
)
from habit_formation import update_habit_strengths
from action_selection import ActionSelector
from arbitration import arbitrate
from experience import Experience

# Simple mapping outcomes->action (same as habit_formation default)
OUTCOME_TO_ACTION = {
    "B1": "RespondImmediately",
    "B4": "WalkAway",
    "B5": "StayQuiet",
}

# Helper to add experiences with days_ago timestamps using Experience
def make_experience(path, intensity, context, outcome, days_ago=0):
    timestamp = datetime.now() - timedelta(days=days_ago)
    return Experience(path=path, intensity=intensity, context=context, outcome=outcome, timestamp=timestamp)


def run_scenario(name, setup_fn):
    print(f"\n===== SCENARIO: {name} =====")

    # Create fresh components per scenario
    person = PersonState(person_id=name)
    memory = Memory()
    learner = PatternLearner()
    memory.connect_pattern_learner(learner)
    system_mem = SystemMemory()

    # Call setup function to populate person, memory, learner, system_mem
    setup_fn(person, memory, learner, system_mem)

    # Derive current path
    current_path = [t for t in (person.emotion, person.feeling, person.mood) if t]
    current_pattern_id = ".".join(current_path)

    # Ensure habit strengths reflect stored experiences
    update_habit_strengths(person, memory, learner, pattern_id=current_pattern_id)

    # Produce proposals
    gd_scores, gd_reasons = propose_goal_directed(person, person.context, current_pattern_id)
    hb_scores, hb_reasons = propose_habitual(person, current_pattern_id, learner)
    rt_scores, rt_reasons = propose_reactive(person)

    # Print proposals
    print("\nReactive proposals:")
    for a, s in rt_scores.items():
        if s:
            print(f"  {a} -> {s:.3f} reasons: {rt_reasons.get(a, [])}")

    print("\nHabitual proposals:")
    for a, s in hb_scores.items():
        if s:
            print(f"  {a} -> {s:.3f} reasons: {hb_reasons.get(a, [])}")

    print("\nGoal-directed proposals:")
    for a, s in gd_scores.items():
        if s:
            print(f"  {a} -> {s:.3f} reasons: {gd_reasons.get(a, [])}")

    # Aggregate
    aggregated = {}
    contributions = {}
    systems = [("GoalDirected", gd_scores, gd_reasons), ("Habitual", hb_scores, hb_reasons), ("Reactive", rt_scores, rt_reasons)]
    for sys_name, scores_dict, reasons_dict in systems:
        for action, score in scores_dict.items():
            if score <= 0:
                continue
            aggregated[action] = aggregated.get(action, 0.0) + score
            contributions.setdefault(action, []).append((sys_name, float(score), reasons_dict.get(action, [])))

    print("\nAggregated (pre-SystemMemory):")
    for a, s in aggregated.items():
        print(f"  {a} -> {s:.3f} sources: {', '.join([f'{t[0]}(+{t[1]:.2f})' for t in contributions.get(a, [])])}")

    # Apply SystemMemory
    selector = ActionSelector()
    adjusted_scores, mem_infl = selector.apply_system_memory_influence(aggregated.copy(), person, system_mem, person.person_id)
    for action in adjusted_scores:
        delta = adjusted_scores.get(action, 0.0) - aggregated.get(action, 0.0)
        if delta != 0:
            contributions.setdefault(action, []).append(("SystemMemory", float(delta), mem_infl.get(action, [])))

    print("\nSystemMemory influence:")
    for action, infl in mem_infl.items():
        if infl:
            print(f"  {action}:")
            for item in infl:
                print(f"    - {item}")

    print("\nFinal arbitration scores:")
    for a, s in adjusted_scores.items():
        print(f"  {a} -> {s:.3f} sources: {', '.join([f'{t[0]}(+{t[1]:.2f})' for t in contributions.get(a, [])])}")

    # Arbitration
    chosen, conf, reason = arbitrate(adjusted_scores, contributions)
    print(f"\nSelected action: {chosen} (confidence: {conf:.1f}%)")
    print(f"Reason: {reason}")

    # Simulate outcome (use default map)
    action_to_outcome = {v: k for k, v in OUTCOME_TO_ACTION.items()}
    simulated_outcome = None
    if chosen in action_to_outcome:
        simulated_outcome = action_to_outcome[chosen]
    else:
        # fallback: pick most likely outcome from pattern learner
        pat = learner.get_pattern(current_path)
        if pat:
            simulated_outcome = pat.most_likely_outcome()

    print(f"Simulated outcome: {simulated_outcome}")

    # Learning update
    if simulated_outcome:
        bridge = __import__('learning_bridge').LearningBridge()
        diag = bridge.record_execution(
            person_state=person,
            person_id=person.person_id,
            chosen_action=chosen,
            actual_outcome=simulated_outcome,
            pattern_id=current_pattern_id,
            pattern_path=current_path,
            context=person.context,
            memory=memory,
            pattern_learner=learner,
        )
        if diag.get("habit_strength_updated"):
            print("Learning update: pattern learner and habit strengths updated.")

    # Return summary dict if needed
    return {
        "name": name,
        "chosen": chosen,
        "confidence": conf,
        "reason": reason,
        "adjusted_scores": adjusted_scores,
        "contributions": contributions,
    }


# Scenario setups

def setup_repeated_conflict(person, memory, learner, system_mem):
    person.update_context(context="Someone insulted the person")
    person.update_efmsomb(emotion="E4", feeling="F3", mood="M2", state_of_mind={"defensive": True})
    system_mem.add_belief(person.person_id, "Respect must be defended")
    system_mem.add_value(person.person_id, "Self respect")
    system_mem.add_rule(person.person_id, "When attacked, respond immediately")
    # experiences already exist in global memory in main; add similar here
    memory.store(make_experience(path=["E4", "F3", "M2", "S5", "B1"], intensity=8, context="Repeated conflict", outcome="B1", days_ago=30))
    memory.store(make_experience(path=["E4", "F3", "M2", "S5", "B1"], intensity=7, context="Someone insulted the person", outcome="B1", days_ago=14))
    memory.store(make_experience(path=["E4", "F3", "M2", "S2", "B4"], intensity=5, context="Minor disagreement", outcome="B4", days_ago=20))
    memory.store(make_experience(path=["E4", "F3", "M2", "S5", "B1"], intensity=9, context="Serious conflict", outcome="B1", days_ago=7))
    memory.store(make_experience(path=["E4", "F3", "M2", "S2", "B4"], intensity=6, context="Person was already frustrated", outcome="B4", days_ago=10))
    memory.store(make_experience(path=["E4", "F3", "M2", "S5", "B1"], intensity=8, context="Another serious conflict", outcome="B1", days_ago=1))


def setup_minor_disagreement(person, memory, learner, system_mem):
    person.update_context(context="Minor disagreement")
    person.update_efmsomb(emotion="E2", feeling="F1", mood="M1", state_of_mind={})
    person.values = ["harmony"]
    system_mem.add_value(person.person_id, "harmony")
    # experiences favor B4
    memory.store(make_experience(path=["E2", "F1", "M1", "S2", "B4"], intensity=3, context="Minor disagreement", outcome="B4", days_ago=5))
    memory.store(make_experience(path=["E2", "F1", "M1", "S2", "B4"], intensity=4, context="Minor disagreement", outcome="B4", days_ago=10))


def setup_walkaway_beneficial(person, memory, learner, system_mem):
    person.update_context(context="Dangerous situation")
    person.update_efmsomb(emotion="E3", feeling="F2", mood="M3", state_of_mind={})
    person.needs = {"safety": True}
    system_mem.add_history(person.person_id, "Previous fights escalated badly")
    system_mem.add_value(person.person_id, "safety")
    memory.store(make_experience(path=["E3", "F2", "M3", "S2", "B4"], intensity=9, context="Dangerous situation", outcome="B4", days_ago=2))
    memory.store(make_experience(path=["E3", "F2", "M3", "S2", "B4"], intensity=7, context="Dangerous situation", outcome="B4", days_ago=6))


def setup_stayquiet_beneficial(person, memory, learner, system_mem):
    person.update_context(context="Formal meeting")
    person.update_efmsomb(emotion="E1", feeling="F1", mood="M1", state_of_mind={})
    person.values = ["harmony"]
    system_mem.add_rule(person.person_id, "Avoid confrontation during meetings")
    memory.store(make_experience(path=["E1", "F1", "M1", "S1", "B5"], intensity=2, context="Formal meeting", outcome="B5", days_ago=3))
    memory.store(make_experience(path=["E1", "F1", "M1", "S1", "B5"], intensity=2, context="Formal meeting", outcome="B5", days_ago=7))


def setup_habit_vs_goal_conflict(person, memory, learner, system_mem):
    # Habit: RespondImmediately is common, but current goal is to avoid conflict
    person.update_context(context="Provocation at work")
    person.update_efmsomb(emotion="E4", feeling="F3", mood="M2", state_of_mind={"defensive": True})
    person.goals = {"avoid_conflict": True}
    system_mem.add_value(person.person_id, "career")
    system_mem.add_rule(person.person_id, "Maintain professionalism at work")
    # Past experiences produced RespondImmediately
    memory.store(make_experience(path=["E4", "F3", "M2", "S5", "B1"], intensity=8, context="Provocation", outcome="B1", days_ago=30))
    memory.store(make_experience(path=["E4", "F3", "M2", "S5", "B1"], intensity=7, context="Provocation", outcome="B1", days_ago=20))
    memory.store(make_experience(path=["E4", "F3", "M2", "S5", "B1"], intensity=6, context="Provocation", outcome="B1", days_ago=10))


if __name__ == "__main__":
    scenarios = [
        ("Repeated conflict / insult", setup_repeated_conflict),
        ("Minor disagreement", setup_minor_disagreement),
        ("Walk away beneficial", setup_walkaway_beneficial),
        ("Stay quiet beneficial", setup_stayquiet_beneficial),
        ("Habit vs Goal conflict", setup_habit_vs_goal_conflict),
    ]

    results = []
    for name, fn in scenarios:
        res = run_scenario(name, fn)
        results.append(res)

    # Print brief summary
    print("\n===== SCENARIO SUMMARY =====")
    for r in results:
        print(f"{r['name']}: chosen={r['chosen']} conf={r['confidence']:.1f}%")
