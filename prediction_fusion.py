class PredictionFusion:

    def __init__(
        self,
        pattern_weight=0.4,
        weighted_weight=0.4,
        context_weight=0.2
    ):

        self.pattern_weight = pattern_weight
        self.weighted_weight = weighted_weight
        self.context_weight = context_weight

    # ==========================================
    # NORMALIZE INPUT SCORES
    # ==========================================

    def normalize_scores(self, scores):

        if not scores:
            return {}

        normalized = {}

        for outcome, score in scores.items():

            if score is None:
                continue

            value = float(score)

            if value > 1:
                value = value / 100.0

            normalized[outcome] = value

        return normalized

    # ==========================================
    # FUSE SCORES
    # ==========================================

    def fuse(
        self,
        pattern_scores=None,
        weighted_scores=None,
        context_scores=None
    ):

        pattern_scores = self.normalize_scores(
            pattern_scores or {}
        )
        weighted_scores = self.normalize_scores(
            weighted_scores or {}
        )
        context_scores = self.normalize_scores(
            context_scores or {}
        )

        all_outcomes = set(
            pattern_scores
        ) | set(
            weighted_scores
        ) | set(
            context_scores
        )

        if not all_outcomes:
            return None, 0.0, {}

        fused_scores = {}

        for outcome in all_outcomes:

            pattern_value = pattern_scores.get(outcome, 0.0)
            weighted_value = weighted_scores.get(outcome, 0.0)
            context_value = context_scores.get(outcome, 0.0)

            fused_scores[outcome] = (
                pattern_value * self.pattern_weight
                + weighted_value * self.weighted_weight
                + context_value * self.context_weight
            )

        predicted_outcome = max(
            fused_scores,
            key=fused_scores.get
        )

        total_score = sum(fused_scores.values())

        confidence = 0.0

        if total_score > 0:
            confidence = (
                fused_scores[predicted_outcome]
                / total_score
            ) * 100.0

        return (
            predicted_outcome,
            confidence,
            fused_scores
        )

    # ==========================================
    # SHOW FINAL PREDICTION
    # ==========================================

    def show(
        self,
        pattern_scores=None,
        weighted_scores=None,
        context_scores=None
    ):

        (
            predicted_outcome,
            confidence,
            fused_scores
        ) = self.fuse(
            pattern_scores,
            weighted_scores,
            context_scores
        )

        print("\n===== FINAL PREDICTION =====")

        if predicted_outcome is None:
            print("No final prediction available.")
            return

        print(
            f"Predicted Outcome: {predicted_outcome}"
        )

        print(
            f"Final Confidence: {confidence:.1f}%"
        )

        print("Final Outcome Scores:")

        for outcome, score in fused_scores.items():
            print(
                f"  {outcome} -> {score:.4f}"
            )
