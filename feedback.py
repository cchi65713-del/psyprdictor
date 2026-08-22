class FeedbackLearner:

    def __init__(self, pattern_adaptation):
        self.pattern_adaptation = pattern_adaptation


    def learn_from_result(
        self,
        pattern_id,
        predicted,
        actual
    ):

        print("\n===== FEEDBACK LEARNING =====")

        print(
            f"Predicted: {predicted}"
        )

        print(
            f"Actual: {actual}"
        )


        if predicted == actual:

            print(
                "Result: Correct prediction"
            )

            self.pattern_adaptation.strengthen(
                pattern_id
            )


        else:

            print(
                "Result: Wrong prediction"
            )

            self.pattern_adaptation.weaken(
                pattern_id
            )