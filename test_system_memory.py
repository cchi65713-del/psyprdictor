from competition import BehavioralTendency, CompetitionEngine
from system_memory import SystemMemory


def run_tests():
    person = "alice"

    # Shared engine with SystemMemory attached
    memory = SystemMemory()
    engine = CompetitionEngine(system_memory=memory)

    # ----------------------------------
    # TEST 1: Memory neutral -> factor == 1.0
    # ----------------------------------
    goal = BehavioralTendency(
        action="WalkAway",
        raw_strength=45.0,
        source="goal_directed",
        confidence_in_proposal=0.85,
        supporting_evidence=["conflict avoidance goal"],
        reason="Goal to avoid conflict"
    )

    res = engine.compete([goal], person)
    t = res.all_proposals[0]
    print("TEST 1: Memory neutral")
    print(f"  system_memory_factor={t.system_memory_factor}")
    print(f"  normalized={t.normalized_strength:.4f}, adjusted={t.adjusted_strength:.4f}")
    assert abs(t.system_memory_factor - 1.0) < 1e-8

    # ----------------------------------
    # TEST 2: Memory supports WalkAway -> slight increase
    # ----------------------------------
    memory.add_rule(person, "support:WalkAway")

    goal2 = BehavioralTendency(
        action="WalkAway",
        raw_strength=45.0,
        source="goal_directed",
        confidence_in_proposal=0.85,
    )

    res2 = engine.compete([goal2], person)
    t2 = res2.all_proposals[0]
    print("\nTEST 2: Memory supports WalkAway")
    print(f"  system_memory_factor={t2.system_memory_factor}")
    print(f"  normalized={t2.normalized_strength:.4f}, adjusted={t2.adjusted_strength:.4f}")
    assert t2.system_memory_factor > 1.0
    assert t2.adjusted_strength > t2.normalized_strength

    # Clear rules for next cases
    memory.rules[person] = []

    # ----------------------------------
    # TEST 3: Memory opposes RespondImmediately -> reduced but not zero
    # ----------------------------------
    memory.add_rule(person, "oppose:RespondImmediately")

    reactive = BehavioralTendency(
        action="RespondImmediately",
        raw_strength=70.0,
        source="reactive",
        confidence_in_proposal=0.95,
    )

    res3 = engine.compete([reactive], person)
    t3 = res3.all_proposals[0]
    print("\nTEST 3: Memory opposes RespondImmediately")
    print(f"  system_memory_factor={t3.system_memory_factor}")
    print(f"  normalized={t3.normalized_strength:.4f}, adjusted={t3.adjusted_strength:.4f}")
    assert 0.3 <= t3.system_memory_factor < 1.0
    assert t3.adjusted_strength < t3.normalized_strength

    # Clear rules for next case
    memory.rules[person] = []

    # ----------------------------------
    # TEST 4: Rule strongly opposes -> factor >= 0.3
    # ----------------------------------
    memory.add_rule(person, "forbid:RespondImmediately")

    reactive2 = BehavioralTendency(
        action="RespondImmediately",
        raw_strength=70.0,
        source="reactive",
        confidence_in_proposal=0.95,
    )

    res4 = engine.compete([reactive2], person)
    t4 = res4.all_proposals[0]
    print("\nTEST 4: Rule strongly opposes RespondImmediately")
    print(f"  system_memory_factor={t4.system_memory_factor}")
    print(f"  normalized={t4.normalized_strength:.4f}, adjusted={t4.adjusted_strength:.4f}")
    assert t4.system_memory_factor >= 0.3

    print("\nAll SystemMemory tests passed.")


if __name__ == "__main__":
    run_tests()
from system_memory import SystemMemory
from competition import BehavioralTendency, CompetitionEngine


def run_tests():

    mem = SystemMemory()

    print("\nTEST 1: Memory neutral (no entries)")
    t1 = BehavioralTendency(
        action="WalkAway",
        raw_strength=45.0,
        source="goal_directed",
        confidence_in_proposal=0.9,
    )

    f1, reasons1 = mem.assess_tendency("alice", t1)
    print(f"  factor={f1}, reasons={reasons1}")
    assert f1 == 1.0, "Neutral memory should return factor 1.0"

    print("\nTEST 2: Memory supports WalkAway")
    mem.add_rule("bob", "support:WalkAway")

    t2 = BehavioralTendency(
        action="WalkAway",
        raw_strength=45.0,
        source="goal_directed",
        confidence_in_proposal=0.9,
    )

    f2, reasons2 = mem.assess_tendency("bob", t2)
    print(f"  factor={f2}, reasons={reasons2}")
    assert f2 > 1.0 and f2 <= 1.1, "Support should slightly increase factor"

    # Also verify adjusted strength increases after integrate with engine
    engine = CompetitionEngine(system_memory=mem)
    result = engine.compete([t2], person="bob")
    proposal = result.all_proposals[0]
    print(
        f"  normalized={proposal.normalized_strength:.4f}, "
        f"adjusted={proposal.adjusted_strength:.4f}"
    )
    assert proposal.adjusted_strength > proposal.normalized_strength

    print("\nTEST 3: Memory opposes RespondImmediately")
    mem2 = SystemMemory()
    mem2.add_rule("carol", "oppose:RespondImmediately")

    t3 = BehavioralTendency(
        action="RespondImmediately",
        raw_strength=70.0,
        source="reactive",
        confidence_in_proposal=0.95,
    )

    f3, reasons3 = mem2.assess_tendency("carol", t3)
    print(f"  factor={f3}, reasons={reasons3}")
    assert 0.3 <= f3 < 1.0, "Opposition should reduce factor but not to zero"

    print("\nTEST 4: Strong rule opposes an action")
    mem3 = SystemMemory()
    mem3.add_rule("dave", "forbid:RespondImmediately")

    t4 = BehavioralTendency(
        action="RespondImmediately",
        raw_strength=70.0,
        source="reactive",
        confidence_in_proposal=0.95,
    )

    f4, reasons4 = mem3.assess_tendency("dave", t4)
    print(f"  factor={f4}, reasons={reasons4}")
    assert f4 >= 0.3, "Strong rule should be clamped to at least 0.3"

    print("\nAll SystemMemory tests passed.")


if __name__ == '__main__':
    run_tests()
