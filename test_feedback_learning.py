from feedback import FeedbackLearner
from pattern_adaptation import PatternAdaptation
from pattern_learner import PatternLearner
from self_learning import SelfLearning
from adaptive_probability import AdaptiveProbability


def test_feedback_learning_updates_pattern_weight():
    pattern_id = "E4.F3.M2"
    adaptation = PatternAdaptation()
    learner = FeedbackLearner(adaptation)

    initial_weight = adaptation.get_weight(pattern_id)

    learner.learn_from_result(pattern_id, "B1", "B4")
    wrong_weight = adaptation.get_weight(pattern_id)
    assert wrong_weight < initial_weight

    learner.learn_from_result(pattern_id, "B1", "B1")
    corrected_weight = adaptation.get_weight(pattern_id)
    assert corrected_weight > wrong_weight


def test_self_learning_updates_pattern_evidence_on_feedback():
    pattern_id = "E4.F3.M2"
    pattern_learner = PatternLearner()
    adaptation = PatternAdaptation()
    self_learning = SelfLearning(pattern_learner, adaptation)

    initial_pattern = pattern_learner.get_pattern(["E4", "F3", "M2"])
    assert initial_pattern is None

    self_learning.record_feedback(
        prediction="B1",
        actual="B4",
        context="Someone insulted the person",
        path=["E4", "F3", "M2"],
    )

    updated_pattern = pattern_learner.get_pattern(["E4", "F3", "M2"])
    assert updated_pattern is not None
    assert updated_pattern.outcomes.get("B4", 0) >= 1
    assert adaptation.get_weight(pattern_id) < 1.0


def test_adaptive_probability_uses_updated_pattern_outcomes_after_feedback():
    pattern_id = "E4.F3.M2"
    pattern_learner = PatternLearner()
    adaptation = PatternAdaptation()
    adaptive_probability = AdaptiveProbability(adaptation)

    pattern_learner.record_feedback(["E4", "F3", "M2"], "B1")
    pattern_learner.record_feedback(["E4", "F3", "M2"], "B1")
    pattern_learner.record_feedback(["E4", "F3", "M2"], "B1")
    pattern_learner.record_feedback(["E4", "F3", "M2"], "B1")
    pattern_learner.record_feedback(["E4", "F3", "M2"], "B4")
    pattern_learner.record_feedback(["E4", "F3", "M2"], "B4")
    pattern_learner.record_feedback(["E4", "F3", "M2"], "B4")

    updated_pattern = pattern_learner.get_pattern(["E4", "F3", "M2"])
    assert updated_pattern is not None
    assert updated_pattern.outcomes == {"B1": 4, "B4": 3}

    adaptive_scores = adaptive_probability.calculate_from_pattern(
        pattern_id,
        updated_pattern,
    )

    assert adaptive_scores["B1"] == 57.14285714285714
    assert adaptive_scores["B4"] == 42.857142857142854
