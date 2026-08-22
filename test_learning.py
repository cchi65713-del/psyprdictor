from memory import Memory
from experience import Experience
from pattern import PatternRecognizer
from prediction import PredictionEngine


# ============================================================
# STAGE 26 — MULTIPLE EXPERIENCE LEARNING TEST
# ============================================================


# ------------------------------------------------------------
# CREATE MEMORY
# ------------------------------------------------------------

memory = Memory()


# ------------------------------------------------------------
# CREATE EXPERIENCES
# ------------------------------------------------------------

experiences = [

    Experience(
        path=["E4", "F3", "M2", "S5", "B1"],
        intensity=8,
        context="Repeated conflict",
        outcome="B1"
    ),

    Experience(
        path=["E4", "F3", "M2", "S5", "B2"],
        intensity=6,
        context="Argument with someone",
        outcome="B2"
    ),

    Experience(
        path=["E4", "F3", "M2", "S2", "B4"],
        intensity=7,
        context="Feeling misunderstood",
        outcome="B4"
    ),

    Experience(
        path=["E10", "F8", "M6", "S3", "B7"],
        intensity=5,
        context="Unexpected situation",
        outcome="B7"
    ),

    Experience(
        path=["E10", "F8", "M6", "S3", "B7"],
        intensity=8,
        context="Similar unexpected situation",
        outcome="B7"
    )

]


# ------------------------------------------------------------
# STORE EXPERIENCES
# ------------------------------------------------------------

for experience in experiences:

    memory.store(experience)


# ------------------------------------------------------------
# SHOW MEMORY
# ------------------------------------------------------------

print("\n")
print("============================================================")
print("                    STORED EXPERIENCES")
print("============================================================")

memory.show()


# ------------------------------------------------------------
# CREATE PATTERN RECOGNIZER
# ------------------------------------------------------------

pattern_recognizer = PatternRecognizer(memory)


# ------------------------------------------------------------
# TEST CURRENT PATH
# ------------------------------------------------------------

current_path = ["E4", "F3", "M2"]


print("\n")
print("============================================================")
print("                    PATTERN TEST")
print("============================================================")


pattern_recognizer.show_result(current_path)


# ------------------------------------------------------------
# SHOW POSSIBLE NEXT STEPS
# ------------------------------------------------------------

pattern_recognizer.show_next_steps(current_path)


# ------------------------------------------------------------
# SHOW POSSIBLE OUTCOMES
# ------------------------------------------------------------

pattern_recognizer.show_possible_outcomes(current_path)


# ------------------------------------------------------------
# PREDICTION
# ------------------------------------------------------------

prediction_engine = PredictionEngine()


matching_experiences = pattern_recognizer.recognize(
    current_path
)


prediction_engine.show_prediction(
    current_path,
    matching_experiences
)