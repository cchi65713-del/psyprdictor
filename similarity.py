class SimilarityEngine:

    def compare(self, path1, path2):
        if not path1 or not path2:
            return 0

        matches = 0
        length = min(len(path1), len(path2))

        for i in range(length):
            if path1[i] == path2[i]:
                matches += 1

        return (matches / max(len(path1), len(path2))) * 100

    def show_comparison(self, path1, path2):
        score = self.compare(path1, path2)

        print("\n===== PATTERN SIMILARITY =====")
        print(f"Path 1: {path1}")
        print(f"Path 2: {path2}")
        print(f"Similarity: {score:.1f}%")