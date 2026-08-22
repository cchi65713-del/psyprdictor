class PatternID:

    @staticmethod
    def normalize_path(path):
        if path is None:
            return []
        if isinstance(path, str):
            return [part for part in path.split(".") if part]
        return [str(part) for part in path if part is not None]

    def create(self, path):
        return ".".join(self.normalize_path(path))

    def show(self, path):

        pattern_id = self.create(path)

        print("\n===== PATTERN ID =====")
        print(f"Path: {path}")
        print(f"Pattern ID: {pattern_id}")

        return pattern_id