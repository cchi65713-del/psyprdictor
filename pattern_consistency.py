class PatternConsistency:

    def calculate(self, outcomes):

        if not outcomes:
            return 0

        counts = {}

        for outcome in outcomes:

            if outcome not in counts:
                counts[outcome] = 0

            counts[outcome] += 1

        total = len(outcomes)

        highest_count = max(counts.values())

        consistency = (highest_count / total) * 100

        return consistency

    def show(self, pattern_id, outcomes):

        consistency = self.calculate(outcomes)

        print("\n===== PATTERN CONSISTENCY =====")
        print(f"Pattern: {pattern_id}")
        print(f"Occurrences: {len(outcomes)}")
        print(f"Consistency: {consistency:.1f}%")

        if consistency >= 80:
            print("Consistency Status: HIGH")

        elif consistency >= 50:
            print("Consistency Status: MODERATE")

        else:
            print("Consistency Status: LOW")