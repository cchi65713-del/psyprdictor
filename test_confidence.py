from competition import BehavioralTendency, CompetitionEngine


def run_confidence_tests():
    engine = CompetitionEngine()

    # TEST 1: Strong clear winner with multiple sources agreeing -> high confidence
    t1 = BehavioralTendency(action="X", raw_strength=90, source="goal_directed", confidence_in_proposal=0.95, supporting_evidence=["e1"])
    t2 = BehavioralTendency(action="X", raw_strength=80, source="reactive", confidence_in_proposal=0.9, supporting_evidence=["e2"])
    t3 = BehavioralTendency(action="X", raw_strength=8, source="habitual", confidence_in_proposal=0.85, supporting_evidence=["e3"])

    res1 = engine.compete([t1, t2, t3])
    print("TEST 1: Strong clear winner")
    print(res1.confidence_breakdown)
    print(f"decision_confidence={res1.decision_confidence:.4f}")
    assert res1.decision_confidence > 0.8

    # TEST 2: Very close competition between two actions -> lower confidence
    a1 = BehavioralTendency(action="A", raw_strength=50, source="goal_directed", confidence_in_proposal=0.9)
    a2 = BehavioralTendency(action="B", raw_strength=49.5, source="reactive", confidence_in_proposal=0.95)

    res2 = engine.compete([a1, a2])
    print("\nTEST 2: Very close competition")
    print(res2.confidence_breakdown)
    print(f"decision_confidence={res2.decision_confidence:.4f}")
    assert res2.decision_confidence < 0.5

    # TEST 3: One strong source wins but others disagree -> convergence reduced
    s1 = BehavioralTendency(action="Win", raw_strength=100, source="reactive", confidence_in_proposal=0.95)
    s2 = BehavioralTendency(action="Lose", raw_strength=60, source="goal_directed", confidence_in_proposal=0.9)
    s3 = BehavioralTendency(action="Lose", raw_strength=6, source="habitual", confidence_in_proposal=0.8)

    res3 = engine.compete([s1, s2, s3])
    print("\nTEST 3: Strong source wins but others disagree")
    print(res3.confidence_breakdown)
    print(f"decision_confidence={res3.decision_confidence:.4f}")
    assert res3.convergence_score < 1.0
    assert res3.decision_confidence < 0.8

    # TEST 4: Winning sources have low proposal confidence -> lower source_confidence
    l1 = BehavioralTendency(action="LowConf", raw_strength=80, source="reactive", confidence_in_proposal=0.2)
    l2 = BehavioralTendency(action="LowConf", raw_strength=70, source="habitual", confidence_in_proposal=0.3)
    l3 = BehavioralTendency(action="Other", raw_strength=10, source="goal_directed", confidence_in_proposal=0.9)

    res4 = engine.compete([l1, l2, l3])
    print("\nTEST 4: Low source confidence")
    print(res4.confidence_breakdown)
    print(f"decision_confidence={res4.decision_confidence:.4f}")
    assert res4.source_confidence_score < 0.5

    # TEST 5: Winning tendencies have little/no evidence -> evidence component reduced
    e1 = BehavioralTendency(action="Eless", raw_strength=80, source="reactive", confidence_in_proposal=0.9, supporting_evidence=[])
    e2 = BehavioralTendency(action="Other", raw_strength=30, source="goal_directed", confidence_in_proposal=0.9, supporting_evidence=["x","y","z"])

    res5 = engine.compete([e1, e2])
    print("\nTEST 5: Little/no evidence for winner")
    print(res5.confidence_breakdown)
    print(f"evidence_score={res5.evidence_score:.4f}, decision_confidence={res5.decision_confidence:.4f}")
    assert res5.evidence_score == 0.0

    # TEST 6: A single habit-driven B1 experience should not become near-certain.
    h1 = BehavioralTendency(action="RespondImmediately", raw_strength=1.5, source="habitual", confidence_in_proposal=0.9, supporting_evidence=["B1 outcome"])
    res6 = engine.compete([h1])
    print("\nTEST 6: Single habit-driven proposal")
    print(res6.confidence_breakdown)
    print(f"decision_confidence={res6.decision_confidence:.4f}")
    assert res6.decision_confidence < 0.7

    print("\nConfidence tests completed.")


if __name__ == "__main__":
    run_confidence_tests()
