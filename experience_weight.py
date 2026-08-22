class ExperienceWeight:

    def calculate(self, experience):
        """
        Calculate the importance of an experience.

        Factors:
        - Intensity: how strong the experience was
        - Recency: placeholder for now
        """

        intensity = experience.intensity

        # Convert intensity (1-10) into a basic weight
        intensity_weight = intensity / 10

        return intensity_weight

    def show(self, experience):

        weight = self.calculate(experience)

        print("\n===== EXPERIENCE WEIGHT =====")
        print(f"Context: {experience.context}")
        print(f"Intensity: {experience.intensity}")
        print(f"Weight: {weight:.2f}")