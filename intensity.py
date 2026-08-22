class Intensity:

    def __init__(self):
        self.levels = {}

    def record(self, pattern_id, level):
        self.levels[pattern_id] = level

    def get_level(self, pattern_id):
        return self.levels.get(pattern_id)

    def show(self):
        print("\n===== INTENSITY =====")

        for pattern_id, level in self.levels.items():
            print(f"{pattern_id} -> Intensity: {level}")