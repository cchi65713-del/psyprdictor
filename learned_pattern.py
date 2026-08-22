class LearnedPattern:

    def __init__(self, path, occurrences=0):
        self.path = path
        self.occurrences = occurrences
        self.outcomes = {}

    def add_occurrence(self, outcome=None):

        self.occurrences += 1

        if outcome:

            if outcome not in self.outcomes:
                self.outcomes[outcome] = 0

            self.outcomes[outcome] += 1

    def most_likely_outcome(self):

        if not self.outcomes:
            return None

        return max(
            self.outcomes,
            key=self.outcomes.get
        )

    def show(self):

        print("\n===== LEARNED PATTERN =====")

        print(f"Path: {self.path}")
        print(f"Occurrences: {self.occurrences}")

        if self.outcomes:

            print("Outcomes:")

            for outcome, count in self.outcomes.items():

                print(
                    f"  {outcome} -> {count}"
                )

        prediction = self.most_likely_outcome()

        if prediction:

            print(
                f"Most Likely Outcome: {prediction}"
            )