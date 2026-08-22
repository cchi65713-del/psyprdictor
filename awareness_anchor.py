class AwarenessAnchor:


    def __init__(self):

        self.awareness_levels = {
            "LOW": 0.0,
            "MEDIUM": 0.3,
            "HIGH": 0.6
        }


    # ==========================================
    # APPLY AWARENESS
    # ==========================================

    def apply(
        self,
        predicted_outcome,
        confidence,
        awareness_level
    ):


        reduction = (
            self.awareness_levels
            .get(
                awareness_level.upper(),
                0
            )
        )


        new_confidence = (
            confidence *
            (1 - reduction)
        )


        return {
            "original_prediction":
                predicted_outcome,

            "original_confidence":
                confidence,

            "awareness_level":
                awareness_level,

            "adjusted_confidence":
                round(
                    new_confidence,
                    2
                )
        }


    # ==========================================
    # SHOW RESULT
    # ==========================================

    def show(
        self,
        result
    ):


        print(
            "\n===== AWARENESS ANCHOR ====="
        )


        print(
            f"Prediction: "
            f"{result['original_prediction']}"
        )


        print(
            f"Original Confidence: "
            f"{result['original_confidence']}%"
        )


        print(
            f"Awareness Level: "
            f"{result['awareness_level']}"
        )


        print(
            f"Adjusted Confidence: "
            f"{result['adjusted_confidence']}%"
        )