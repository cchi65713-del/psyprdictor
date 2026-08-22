class PatternOutcome:

    @staticmethod
    def normalize_path(path):
        if path is None:
            return []
        if isinstance(path, str):
            return [part for part in path.split(".") if part]
        return [str(part) for part in path if part is not None]

    def __init__(self):

        self.outcomes = {}

    # ==========================================
    # CREATE PATTERN ID
    # ==========================================

    def create_pattern_id(self, path):

        return ".".join(self.normalize_path(path))

    # ==========================================
    # RECORD OUTCOME
    # ==========================================

    def record(self, pattern_id, outcome):

        if pattern_id not in self.outcomes:

            self.outcomes[pattern_id] = []

        self.outcomes[pattern_id].append(
            outcome
        )

    # ==========================================
    # LEARN FROM MEMORY
    # ==========================================

    def learn_from_memory(self, memory):

        self.outcomes = {}

        for experience in memory.get_all():

            pattern_id = self.create_pattern_id(
                experience.path
            )

            if experience.outcome:

                self.record(
                    pattern_id,
                    experience.outcome
                )

    # ==========================================
    # GET OUTCOMES
    # ==========================================

    def get_outcomes(self, pattern_id):

        return self.outcomes.get(
            pattern_id,
            []
        )

    # ==========================================
    # SHOW LEARNED OUTCOMES
    # ==========================================

    def show(self):

        print("\n===== LEARNED PATTERN OUTCOMES =====")

        if not self.outcomes:

            print("No outcomes learned.")

            return

        for pattern_id, outcomes in (
            self.outcomes.items()
        ):

            print(f"\nPattern: {pattern_id}")

            for outcome in outcomes:

                print(f"  -> {outcome}")