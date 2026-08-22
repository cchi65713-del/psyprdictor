class SelfLearning:


    def __init__(self, pattern_learner=None, pattern_adaptation=None):

        self.feedback_history = []
        self.pattern_learner = pattern_learner
        self.pattern_adaptation = pattern_adaptation


    @staticmethod
    def normalize_path(path):
        if path is None:
            return []

        if isinstance(path, str):
            return [part for part in path.split(".") if part]

        return [str(part) for part in path if part is not None]


    def connect_pattern_learner(self, pattern_learner):
        self.pattern_learner = pattern_learner


    def connect_pattern_adaptation(self, pattern_adaptation):
        self.pattern_adaptation = pattern_adaptation


    # ==========================================
    # RECEIVE RESULT
    # ==========================================

    def record_feedback(
        self,
        prediction,
        actual,
        context,
        path
    ):

        feedback = {

            "prediction": prediction,

            "actual": actual,

            "correct": prediction == actual,

            "context": context,

            "path": path

        }


        self.feedback_history.append(
            feedback
        )

        if self.pattern_learner is not None:
            self.pattern_learner.record_feedback(
                path,
                actual
            )

        if self.pattern_adaptation is not None:
            pattern_id = ".".join(
                self.normalize_path(path)
            )

            if pattern_id:
                self.pattern_adaptation.update(
                    pattern_id,
                    prediction,
                    actual
                )



    # ==========================================
    # ANALYZE ACCURACY
    # ==========================================

    def accuracy(self):


        if not self.feedback_history:

            return 0


        correct = 0


        for feedback in self.feedback_history:

            if feedback["correct"]:

                correct += 1



        return (
            correct /
            len(self.feedback_history)
        ) * 100



    # ==========================================
    # LEARNING ADVICE
    # ==========================================

    def analyze(self):


        print(
            "\n===== SELF LEARNING ====="
        )


        if not self.feedback_history:

            print(
                "No feedback available."
            )

            return



        for feedback in self.feedback_history:


            print(
                "\nPrediction:",
                feedback["prediction"]
            )


            print(
                "Actual:",
                feedback["actual"]
            )


            if feedback["correct"]:

                print(
                    "Result: Correct prediction"
                )

            else:

                print(
                    "Result: Pattern needs update"
                )



        print(
            "\nAccuracy:",
            round(
                self.accuracy(),
                2
            ),
            "%"
        )