class PredictionExplanation:

    def __init__(self):
        pass


    # ==========================================
    # GENERATE EXPLANATION
    # ==========================================

    def explain(
        self,
        current_path,
        current_context,
        learned_pattern,
        weighted_result,
        context_result
    ):

        print("\n===== PREDICTION EXPLANATION =====")


        predicted_outcome = weighted_result["outcome"]
        confidence = weighted_result["confidence"]


        print(
            f"Prediction: {predicted_outcome}"
        )


        print("\nReasons:")


        # --------------------------------------
        # Pattern reason
        # --------------------------------------

        if learned_pattern:

            total = sum(
                learned_pattern.outcomes.values()
            )

            outcome_count = (
                learned_pattern.outcomes
                .get(predicted_outcome, 0)
            )

            print(
                f"1. Previous pattern ended in "
                f"{predicted_outcome} "
                f"{outcome_count}/{total} times"
            )


        # --------------------------------------
        # Context reason
        # --------------------------------------

        if context_result:

            context_outcome = (
                context_result["outcome"]
            )

            print(
                f"2. Current context "
                f"'{current_context}' "
                f"matches previous situations "
                f"leading to {context_outcome}"
            )


        # --------------------------------------
        # Path reason
        # --------------------------------------

        print(
            f"3. Current emotional path: "
            f"{current_path}"
        )


        # --------------------------------------
        # Confidence
        # --------------------------------------

        print(
            f"\nFinal Confidence: "
            f"{confidence:.1f}%"
        )