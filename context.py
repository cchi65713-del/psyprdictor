class ContextMemory:

    def __init__(self):
        self.contexts = {}

    def record(self, pattern_id, context):
        if pattern_id not in self.contexts:
            self.contexts[pattern_id] = []

        self.contexts[pattern_id].append(context)

    def get_contexts(self, pattern_id):
        return self.contexts.get(pattern_id, [])

    def show(self):
        print("\n===== CONTEXT MEMORY =====")

        for pattern_id, contexts in self.contexts.items():
            print(f"Pattern: {pattern_id}")

            for number, context in enumerate(contexts, start=1):
                print(f"  {number}: {context}")