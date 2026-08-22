class ContextMemory:

    def __init__(self):

        self.contexts = {}

    # ==========================================
    # LEARN FROM EXPERIENCE
    # ==========================================

    def learn(self, experiences):

        for experience in experiences:

            context = experience.context.lower().strip()
            outcome = experience.outcome

            if context not in self.contexts:

                self.contexts[context] = {}

            if outcome not in self.contexts[context]:

                self.contexts[context][outcome] = 0

            self.contexts[context][outcome] += 1

    # ==========================================
    # FIND SIMILAR CONTEXTS
    # ==========================================

    def find_matches(self, current_context):

        if not current_context:

            return {}

        current_words = set(
            current_context.lower().split()
        )

        matches = {}

        for context, outcomes in self.contexts.items():

            stored_words = set(
                context.split()
            )

            if not stored_words:

                continue

            shared_words = (
                current_words.intersection(
                    stored_words
                )
            )

            if not shared_words:

                continue

            similarity = (
                len(shared_words)
                / len(current_words)
            )

            matches[context] = {
                "similarity": similarity,
                "outcomes": outcomes
            }

        return matches

    # ==========================================
    # PREDICT FROM CONTEXT
    # ==========================================

    def predict(self, current_context):

        matches = self.find_matches(
            current_context
        )

        outcome_scores = {}

        for data in matches.values():

            similarity = data["similarity"]

            for outcome, count in data["outcomes"].items():

                score = similarity * count

                if outcome not in outcome_scores:

                    outcome_scores[outcome] = 0

                outcome_scores[outcome] += score

        if not outcome_scores:

            return None, 0, {}

        predicted_outcome = max(
            outcome_scores,
            key=outcome_scores.get
        )

        total_score = sum(
            outcome_scores.values()
        )

        confidence = (
            outcome_scores[predicted_outcome]
            / total_score
        ) * 100

        return (
            predicted_outcome,
            confidence,
            outcome_scores
        )

    # ==========================================
    # SHOW CONTEXT MEMORY
    # ==========================================

    def show(self):

        print("\n===== CONTEXT MEMORY =====")

        if not self.contexts:

            print("No context memory available.")

            return

        for context, outcomes in self.contexts.items():

            print(f"\nContext: {context}")

            for outcome, count in outcomes.items():

                print(
                    f"  {outcome} -> {count}"
                )

    # ==========================================
    # SHOW CONTEXT PREDICTION
    # ==========================================

    def show_prediction(self, current_context):

        (
            predicted_outcome,
            confidence,
            outcome_scores
        ) = self.predict(current_context)

        print("\n===== CONTEXT PREDICTION =====")

        print(
            f"Current Context: "
            f"{current_context}"
        )

        if predicted_outcome is None:

            print(
                "No context prediction available."
            )

            return

        print(
            f"Predicted Outcome: "
            f"{predicted_outcome}"
        )

        print(
            f"Context Confidence: "
            f"{confidence:.1f}%"
        )

        print("\nContext Outcome Scores:")

        for outcome, score in outcome_scores.items():

            print(
                f"  {outcome} -> "
                f"{score:.2f}"
            )