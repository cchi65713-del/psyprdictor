from memory import Memory
from experience import Experience
from pattern import PatternRecognizer

# This reproduces the bug: some experiences in the system are stored with string-style paths,
# while PatternRecognizer expects list-style paths.
current_path = ["E4", "F3", "M2"]

memory = Memory()
for suffix in [
    ["S5", "B1"],
    ["S5", "B1"],
    ["S2", "B4"],
    ["S5", "B1"],
]:
    path = current_path + suffix
    memory.store(Experience(path=".".join(path), intensity=8, context="ctx", outcome=suffix[-1]))

recognizer = PatternRecognizer(memory)
matches = recognizer.recognize(current_path)
print(f"match_count={len(matches)}")
assert len(matches) == 4, f"Expected 4 matches, found {len(matches)}"
