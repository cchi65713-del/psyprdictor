class PatternRecognizer:

    @staticmethod
    def normalize_path(path):
        if path is None:
            return []

        if isinstance(path, str):
            return [part for part in path.split(".") if part]

        return [str(part) for part in path if part is not None]

    def __init__(self, memory):
        self.memory = memory

    # ==========================================
    # CREATE PATTERN ID
    # ==========================================

    def create_pattern_id(self, current_path):

        return ".".join(
            self.normalize_path(current_path)
        )

    # ==========================================
    # FIND EXPERIENCES USING PATTERN ID
    # ==========================================

    def recognize(self, current_path):

        pattern_id = self.create_pattern_id(current_path)

        return self.memory.get_by_pattern_id(pattern_id)

    # ==========================================
    # COUNT MATCHES
    # ==========================================

    def count_pattern(self, current_path):

        return len(
            self.recognize(current_path)
        )

    # ==========================================
    # GET OUTCOMES
    # ==========================================

    def get_outcomes(self, current_path):

        matches = self.recognize(current_path)

        outcomes = []

        for experience in matches:

            if experience.outcome:

                outcomes.append(
                    experience.outcome
                )

        return outcomes

    # ==========================================
    # GET NEXT STEPS
    # ==========================================

    def get_next_steps(self, current_path):

        matches = self.recognize(current_path)

        next_steps = []
        current_tokens = self.normalize_path(current_path)

        for experience in matches:

            stored_path = self.normalize_path(experience.path)

            if len(stored_path) > len(current_tokens):

                next_step = stored_path[
                    len(current_tokens)
                ]

                next_steps.append(next_step)

        return next_steps

    # ==========================================
    # NEXT-STEP PROBABILITIES
    # ==========================================

    def get_next_step_probabilities(
        self,
        current_path
    ):

        next_steps = self.get_next_steps(
            current_path
        )

        total = len(next_steps)

        if total == 0:

            return {}

        counts = {}

        for step in next_steps:

            if step not in counts:

                counts[step] = 0

            counts[step] += 1

        probabilities = {}

        for step, count in counts.items():

            probabilities[step] = (
                count / total
            ) * 100

        return probabilities

    # ==========================================
    # SHOW PATTERN
    # ==========================================

    def show_result(self, current_path):

        matches = self.recognize(
            current_path
        )

        pattern_id = self.create_pattern_id(
            current_path
        )

        print("\n===== PATTERN RECOGNITION =====")

        print(f"Pattern ID: {pattern_id}")

        print(f"Current Path: {current_path}")

        if matches:

            print("Pattern recognized!")

            print(
                f"Matching Experiences: {len(matches)}"
            )

            for experience in matches:

                print(
                    f"  Path: {experience.path}"
                )

                print(
                    f"  Intensity: {experience.intensity}"
                )

                print(
                    f"  Context: {experience.context}"
                )

                print(
                    f"  Outcome: {experience.outcome}"
                )

        else:

            print(
                "No matching pattern found."
            )

    # ==========================================
    # SHOW NEXT STEPS
    # ==========================================

    def show_next_steps(self, current_path):

        next_steps = self.get_next_steps(
            current_path
        )

        print("\n===== POSSIBLE NEXT STEPS =====")

        if next_steps:

            for step in next_steps:

                print(f"  {step}")

        else:

            print(
                "No previous next steps found."
            )

    # ==========================================
    # SHOW NEXT-STEP PROBABILITIES
    # ==========================================

    def show_next_step_probabilities(
        self,
        current_path
    ):

        probabilities = (
            self.get_next_step_probabilities(
                current_path
            )
        )

        print(
            "\n===== PREDICTED NEXT STEPS ====="
        )

        if probabilities:

            for step, probability in (
                probabilities.items()
            ):

                print(
                    f"  {step} -> "
                    f"{probability:.1f}%"
                )

        else:

            print(
                "No prediction available."
            )

    # ==========================================
    # SHOW POSSIBLE OUTCOMES
    # ==========================================

    def show_possible_outcomes(
        self,
        current_path
    ):

        outcomes = self.get_outcomes(
            current_path
        )

        print(
            "\n===== POSSIBLE OUTCOMES ====="
        )

        if outcomes:

            seen_outcomes = []

            for outcome in outcomes:

                if outcome not in seen_outcomes:

                    seen_outcomes.append(
                        outcome
                    )

                    print(
                        f"  {outcome}"
                    )

        else:

            print(
                "No known outcomes found "
                "for this path."
            )