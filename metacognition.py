class Metacognition:


    def __init__(self):

        self.prediction_history = []


    # ==========================================
    # REVIEW PREDICTION
    # ==========================================

    def review(
        self,
        prediction,
        confidence,
        evidence
    ):

        review = {

            "prediction": prediction,

            "confidence": confidence,

            "evidence": evidence,

            "status": self.evaluate(confidence)

        }


        self.prediction_history.append(review)


        return review



    # ==========================================
    # EVALUATE CONFIDENCE
    # ==========================================

    def evaluate(
        self,
        confidence
    ):


        if confidence >= 80:

            return "STRONG PATTERN"


        elif confidence >= 50:

            return "UNCERTAIN PATTERN"


        else:

            return "WEAK PATTERN"



    # ==========================================
    # SHOW THINKING
    # ==========================================

    def show(
        self,
        review
    ):


        print(
            "\n===== METACOGNITION ====="
        )


        print(
            f"Prediction Reviewed: "
            f"{review['prediction']}"
        )


        print(
            f"Confidence: "
            f"{review['confidence']}%"
        )


        print(
            f"Pattern Status: "
            f"{review['status']}"
        )


        print(
            "\nEvidence:"
        )


        for item in review["evidence"]:

            print(
                f" - {item}"
            )