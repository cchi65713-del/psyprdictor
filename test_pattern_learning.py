from memory import Memory
from experience import Experience
from pattern_learner import PatternLearner


memory = Memory()


# ============================================================
# EXPERIENCES
# ============================================================

memory.store(
    Experience(
        path=["E4", "F3", "M2", "S5", "B1"],
        intensity=8,
        context="Repeated conflict",
        outcome="B1"
    )
)

memory.store(
    Experience(
        path=["E4", "F3", "M2", "S5", "B1"],
        intensity=7,
        context="Another conflict",
        outcome="B1"
    )
)

memory.store(
    Experience(
        path=["E4", "F3", "M2", "S2", "B4"],
        intensity=6,
        context="Feeling misunderstood",
        outcome="B4"
    )
)


# ============================================================
# LEARN PATTERNS
# ============================================================

learner = PatternLearner()

learner.learn(
    memory.get_all()
)


# ============================================================
# SHOW LEARNED PATTERNS
# ============================================================

learner.show_all()


# ============================================================
# CHECK SPECIFIC PATTERN
# ============================================================

pattern = learner.get_pattern(
    ["E4", "F3", "M2"]
)

if pattern:

    print("\n===== SPECIFIC PATTERN =====")

    pattern.show()

else:

    print("Pattern not found.")