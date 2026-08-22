class ProbabilityEngine:

    def show(self, pattern_id, outcomes):

        print("\n===== OUTCOME PROBABILITY =====")
        print(f"Pattern: {pattern_id}")

        if not outcomes:

            print("No outcome history available.")
            return

        counts = {}

        for outcome in outcomes:

            if outcome not in counts:
                counts[outcome] = 0

            counts[outcome] += 1

        total = len(outcomes)

        for outcome, count in counts.items():

            probability = (count / total) * 100

            print(
                f"  {outcome} -> "
                f"{probability:.1f}%"
            )

        most_likely = max(
            counts,
            key=counts.get
        )

        print(
            f"Most Likely Outcome: "
            f"{most_likely}"
        )