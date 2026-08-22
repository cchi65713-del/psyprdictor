class Memory:

    @staticmethod
    def normalize_path(path):
        if path is None:
            return []

        if isinstance(path, str):
            return [part for part in path.split(".") if part]

        return [str(part) for part in path if part is not None]

    def __init__(self, pattern_learner=None):

        self.experiences = []
        self.pattern_learner = pattern_learner


# ==========================================
# CONNECT PATTERN LEARNER
# ==========================================

    def connect_pattern_learner(self, pattern_learner):

        self.pattern_learner = pattern_learner


# ==========================================
# STORE EXPERIENCE
# ==========================================

    def store(self, experience):

        if isinstance(experience.path, str):
            experience.path = self.normalize_path(experience.path)

        # Store the experience
        self.experiences.append(experience)

        # Automatically teach the pattern learner
        if self.pattern_learner:

            self.pattern_learner.learn(
                [experience]
            )


# ==========================================
# GET ALL EXPERIENCES
# ==========================================

    def get_all(self):

        return self.experiences


# ==========================================
# FIND EXPERIENCES BY PATTERN ID
# ==========================================

    def get_by_pattern_id(self, pattern_id):

        matches = []
        pattern_tokens = self.normalize_path(pattern_id)

        for experience in self.experiences:

            experience_tokens = self.normalize_path(experience.path)
            if len(experience_tokens) >= len(pattern_tokens) and experience_tokens[:len(pattern_tokens)] == pattern_tokens:
                matches.append(experience)

        return matches


# ==========================================
# SHOW MEMORY
# ==========================================

    def show(self):

        print("\n===== MEMORY =====")

        if not self.experiences:

            print("Memory is empty.")
            return

        for number, experience in enumerate(
            self.experiences,
            start=1
        ):

            pattern_id = ".".join(
                self.normalize_path(experience.path)
            )

            print(f"\nExperience {number}")
            print(f"Pattern ID: {pattern_id}")
            print(f"Path: {experience.path}")
            print(f"Intensity: {experience.intensity}")
            print(f"Context: {experience.context}")
            print(f"Outcome: {experience.outcome}")