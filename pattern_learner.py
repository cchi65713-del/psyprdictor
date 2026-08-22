from learned_pattern import LearnedPattern


class PatternLearner:

    def __init__(self):
        self.patterns = {}

    @staticmethod
    def normalize_path(path):
        if path is None:
            return []

        if isinstance(path, str):
            return [part for part in path.split(".") if part]

        return [str(part) for part in path if part is not None]

    def record_feedback(self, path, outcome):
        normalized_path = self.normalize_path(path)

        if not normalized_path:
            return

        for length in range(2, len(normalized_path) + 1):

            pattern_path = tuple(normalized_path[:length])

            if pattern_path not in self.patterns:

                self.patterns[pattern_path] = LearnedPattern(
                    list(pattern_path)
                )

            pattern = self.patterns[pattern_path]

            pattern.add_occurrence(outcome)

    def learn(self, experiences):

        for experience in experiences:

            self.record_feedback(
                experience.path,
                experience.outcome
            )

    def get_pattern(self, path):

        return self.patterns.get(tuple(path))

    def has_pattern(self, path):

        return tuple(path) in self.patterns

    def get_all_patterns(self):

        return list(self.patterns.values())

    def show_all(self):

        print("\n===== LEARNED PATTERNS =====")

        if not self.patterns:

            print("No patterns learned yet.")
            return

        for pattern in self.patterns.values():

            pattern.show()