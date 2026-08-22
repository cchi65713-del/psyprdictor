class PatternStrength:

    def calculate(self, match_count):

        if match_count <= 0:
            return 0

        # Simple strength scale
        if match_count == 1:
            return 20

        elif match_count == 2:
            return 40

        elif match_count == 3:
            return 60

        elif match_count == 4:
            return 80

        else:
            return 100

    def show(self, current_path, match_count):

        strength = self.calculate(match_count)

        print("\n===== PATTERN STRENGTH =====")
        print(f"Pattern: {current_path}")
        print(f"Occurrences: {match_count}")
        print(f"Strength: {strength}%")

        if strength >= 80:
            print("Pattern Status: STRONG")

        elif strength >= 40:
            print("Pattern Status: DEVELOPING")

        else:
            print("Pattern Status: WEAK")