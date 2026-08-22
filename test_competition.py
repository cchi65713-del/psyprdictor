from competition import BehavioralTendency, CompetitionEngine


# Goal-directed system wants to avoid the conflict
goal = BehavioralTendency(
    action="WalkAway",
    raw_strength=45.0,
    source="goal_directed",
    confidence_in_proposal=0.85,
    supporting_evidence=[
        "conflict avoidance goal",
        "relationship preservation"
    ],
    reason="Goal is to avoid conflict."
)


# Reactive system wants to respond immediately
reactive = BehavioralTendency(
    action="RespondImmediately",
    raw_strength=70.0,
    source="reactive",
    confidence_in_proposal=0.95,
    supporting_evidence=[
        "high arousal",
        "social threat perceived"
    ],
    reason="Immediate threat requires immediate response."
)


# Habit system also wants to respond immediately
habit = BehavioralTendency(
    action="RespondImmediately",
    raw_strength=3.2,
    source="habitual",
    confidence_in_proposal=0.80,
    supporting_evidence=[
        "learned response pattern",
        "previous similar situations"
    ],
    reason="Previous situations triggered immediate responses."
)


# Create competition engine
engine = CompetitionEngine()


# Run competition
result = engine.compete([
    goal,
    reactive,
    habit
])


# Display result
print("\n==============================")
print("COMPETITION TEST")
print("==============================")

print(f"Selected action: {result.selected_action}")
print(f"Selected source: {result.selected_source}")
print(f"Final strength: {result.final_strength:.4f}")
print(f"Decision confidence: {result.decision_confidence:.2%}")

print(f"\nConflict level: {result.conflict_level}")
print(f"Conflict sources: {result.conflict_sources}")
print(f"Margin: {result.conflict_margin:.4f}")
print(f"Margin percentage: {result.margin_percentage:.2%}")

print("\nAction pressures:")

for action, pressure in result.action_pressures.items():
    print(f"  {action}: {pressure:.4f}")

print("\nReasoning:")
print(result.reasoning)

print("\nIndividual proposals:")

for proposal in result.all_proposals:
    print(
        f"  {proposal.source}: "
        f"{proposal.action} | "
        f"raw={proposal.raw_strength:.2f} | "
        f"normalized={proposal.normalized_strength:.2f} | "
        f"confidence={proposal.confidence_in_proposal:.2f}"
    )

print("\n==============================")