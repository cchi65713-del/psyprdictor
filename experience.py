from datetime import datetime


class Experience:

    def __init__(
        self,
        path,
        intensity,
        context,
        outcome,
        timestamp=None,
        efmsomb=None
    ):

        self.path = path
        self.intensity = intensity
        self.context = context
        self.outcome = outcome

        # Use supplied timestamp,
        # otherwise use the current time.
        if timestamp is None:
            self.timestamp = datetime.now()
        else:
            self.timestamp = timestamp

        # Optional snapshot of canonical EFMSOMB metadata (dict or None).
        # This is intentionally optional and preserved for downstream
        # components that may rely on the runtime EFMSOMB snapshot.
        self.efmsomb = efmsomb

    # ==========================================
    # INTENSITY WEIGHT
    # ==========================================

    def get_intensity_weight(self):

        return self.intensity / 10

    # ==========================================
    # RECENCY
    # ==========================================

    def get_age_days(self):

        now = datetime.now()

        difference = now - self.timestamp

        return difference.total_seconds() / 86400

    # ==========================================
    # RECENCY WEIGHT
    # ==========================================

    def get_recency_weight(self):

        age_days = self.get_age_days()

        # Newer experiences have greater influence.
        weight = 1 / (1 + age_days)

        return weight

    # ==========================================
    # COMBINED EXPERIENCE WEIGHT
    # ==========================================

    def get_weight(self):

        intensity_weight = self.get_intensity_weight()

        recency_weight = self.get_recency_weight()

        return intensity_weight * recency_weight

    # ==========================================
    # SHOW EXPERIENCE
    # ==========================================

    def show(self):

        print("\n===== EXPERIENCE =====")

        print(f"Path: {self.path}")

        print(f"Intensity: {self.intensity}")

        print(f"Context: {self.context}")

        print(f"Outcome: {self.outcome}")

        print(f"Timestamp: {self.timestamp}")

        print(
            f"Age: "
            f"{self.get_age_days():.2f} days"
        )

        print(
            f"Intensity Weight: "
            f"{self.get_intensity_weight():.2f}"
        )

        print(
            f"Recency Weight: "
            f"{self.get_recency_weight():.2f}"
        )

        print(
            f"Combined Weight: "
            f"{self.get_weight():.2f}"
        )