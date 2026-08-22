class PredictionEngine:

    # ==========================================
    # CALCULATE EXPERIENCE WEIGHT
    # ==========================================

    def calculate_weight(self, experience):

        # Get the new combined weight
        # from Experience:
        #
        # Intensity × Recency

        return experience.get_weight()

    # ==========================================
    # CONTEXT MATCH SCORE
    # ==========================================

    def context_score(self, experience, current_context):

        if not current_context:
            return 0

        stored_context = experience.context.lower()
        current_context = current_context.lower()

        # Exact context match
        if stored_context == current_context:
            return 1.0

        # Partial word matching
        stored_words = set(stored_context.split())
        current_words = set(current_context.split())

        if not stored_words or not current_words:
            return 0

        shared_words = stored_words.intersection(
            current_words
        )

        return len(shared_words) / len(current_words)

    # ==========================================
    # PREDICT
    # ==========================================

    def predict(
        self,
        current_path,
        experiences,
        current_context
    ):

        outcome_scores = {}

        for experience in experiences:

            # Check whether this experience
            # belongs to the current path.

            if experience.path[:len(current_path)] != current_path:
                continue

            # ----------------------------------
            # EXPERIENCE WEIGHT
            # ----------------------------------

            experience_weight = self.calculate_weight(
                experience
            )

            # ----------------------------------
            # CONTEXT MATCH
            # ----------------------------------

            context_match = self.context_score(
                experience,
                current_context
            )

            # ----------------------------------
            # FINAL WEIGHT
            # ----------------------------------

            # Give context a stronger influence
            # when calculating the prediction.

            final_weight = (
                experience_weight
                * (1 + context_match)
            )

            outcome = experience.outcome

            if outcome not in outcome_scores:
                outcome_scores[outcome] = 0

            outcome_scores[outcome] += final_weight

        # --------------------------------------
        # NO DATA
        # --------------------------------------

        if not outcome_scores:

            return None, 0, {}

        # --------------------------------------
        # FIND MOST LIKELY OUTCOME
        # --------------------------------------

        predicted_outcome = max(
            outcome_scores,
            key=outcome_scores.get
        )

        total_score = sum(
            outcome_scores.values()
        )

        confidence = (
            outcome_scores[predicted_outcome]
            / total_score
        ) * 100

        return (
            predicted_outcome,
            confidence,
            outcome_scores
        )

    # ==========================================
    # SHOW PREDICTION
    # ==========================================

    def show_prediction(
        self,
        current_path,
        experiences,
        current_context=None
    ):

        (
            predicted_outcome,
            confidence,
            outcome_scores
        ) = self.predict(
            current_path,
            experiences,
            current_context
        )

        print("\n===== WEIGHTED PREDICTION =====")

        print(
            f"Current Path: {current_path}"
        )

        print(
            f"Current Context: {current_context}"
        )

        if predicted_outcome is None:

            print(
                "No prediction available."
            )

            return

        print(
            f"Predicted Outcome: "
            f"{predicted_outcome}"
        )

        print(
            f"Weighted Confidence: "
            f"{confidence:.1f}%"
        )

        print("\nWeighted Outcome Scores:")

        for outcome, score in outcome_scores.items():

            print(
                f"  {outcome} -> "
                f"{score:.2f}"
            )