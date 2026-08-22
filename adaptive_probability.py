class AdaptiveProbability:


    def __init__(self, pattern_adaptation):

        self.pattern_adaptation = pattern_adaptation


    # ==========================================
    # APPLY PATTERN WEIGHT
    # ==========================================

    def adjust_scores(
        self,
        pattern_id,
        outcome_scores
    ):

        weight = self.pattern_adaptation.get_weight(
            pattern_id
        )

        adjusted_scores = {}

        for outcome, score in outcome_scores.items():

            adjusted_scores[outcome] = (
                score * weight
            )

        return adjusted_scores


    # ==========================================
    # CALCULATE PROBABILITY
    # ==========================================

    def calculate_probability(
        self,
        adjusted_scores
    ):

        if not adjusted_scores:

            return {}


        total = sum(
            adjusted_scores.values()
        )


        if total == 0:

            return {}


        probabilities = {}


        for outcome, score in adjusted_scores.items():

            probabilities[outcome] = (
                score / total
            ) * 100


        return probabilities


    # ==========================================
    # CALCULATE
    # ==========================================

    def calculate(
        self,
        pattern_id,
        outcome_scores
    ):

        adjusted_scores = self.adjust_scores(
            pattern_id,
            outcome_scores
        )

        return self.calculate_probability(
            adjusted_scores
        )

    # ==========================================
    # CALCULATE FROM PATTERN
    # ==========================================

    def calculate_from_pattern(
        self,
        pattern_id,
        pattern
    ):

        if pattern is None:
            return {}

        outcomes = getattr(pattern, "outcomes", {}) or {}

        if not outcomes:
            return {}

        total = sum(outcomes.values())

        if total <= 0:
            return {}

        probabilities = {}
        for outcome, count in outcomes.items():
            probabilities[outcome] = (count / total) * 100

        return probabilities

    # ==========================================
    # PREDICT
    # ==========================================

    def predict(
        self,
        pattern_id,
        outcome_scores
    ):

        adjusted_scores = self.adjust_scores(

            pattern_id,

            outcome_scores

        )


        probabilities = self.calculate_probability(

            adjusted_scores

        )


        if not probabilities:

            return None, 0, {}


        predicted_outcome = max(

            probabilities,

            key=probabilities.get

        )


        confidence = probabilities[
            predicted_outcome
        ]


        return (

            predicted_outcome,

            confidence,

            probabilities

        )


    # ==========================================
    # SHOW RESULT
    # ==========================================

    def show_prediction(

        self,

        pattern_id,

        outcome_scores

    ):

        (

            predicted,

            confidence,

            probabilities

        ) = self.predict(

            pattern_id,

            outcome_scores

        )


        print(
            "\n===== ADAPTIVE PROBABILITY ====="
        )


        print(
            f"Pattern: {pattern_id}"
        )


        if predicted is None:

            print(
                "No adaptive prediction available."
            )

            return


        print(
            f"Predicted Outcome: {predicted}"
        )


        print(
            f"Adaptive Confidence: "
            f"{confidence:.1f}%"
        )


        print(
            "\nAdaptive Probabilities:"
        )


        for outcome, probability in probabilities.items():

            print(

                f"  {outcome} -> "
                f"{probability:.1f}%"

            )