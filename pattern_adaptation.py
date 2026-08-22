class PatternAdaptation:


    def __init__(self):

        self.pattern_weights = {}



    # ==========================================
    # INITIALIZE PATTERN
    # ==========================================

    def create_pattern(
        self,
        pattern_id
    ):

        if pattern_id not in self.pattern_weights:

            self.pattern_weights[pattern_id] = 1.0



    # ==========================================
    # STRENGTHEN PATTERN
    # ==========================================

    def strengthen(self, pattern_id):

        self.create_pattern(pattern_id)

        self.pattern_weights[pattern_id] += 0.1

        print("Pattern strengthened")

        return self.pattern_weights[pattern_id]


    # ==========================================
    # WEAKEN PATTERN
    # ==========================================

    def weaken(self, pattern_id):

        self.create_pattern(pattern_id)

        self.pattern_weights[pattern_id] -= 0.1

        print("Pattern weakened")

        if self.pattern_weights[pattern_id] < 0:
            self.pattern_weights[pattern_id] = 0

        return self.pattern_weights[pattern_id]


    # ==========================================
    # UPDATE FROM FEEDBACK
    # ==========================================

    def update(

        self,
        pattern_id,
        prediction,
        actual

    ):

        if prediction == actual:
            return self.strengthen(pattern_id)

        return self.weaken(pattern_id)



    # ==========================================
    # GET PATTERN STRENGTH
    # ==========================================

    def get_weight(

        self,
        pattern_id

    ):

        return self.pattern_weights.get(

            pattern_id,

            1.0

        )



    # ==========================================
    # SHOW PATTERNS
    # ==========================================

    def show(self):


        print(
            "\n===== PATTERN ADAPTATION ====="
        )


        for pattern, weight in self.pattern_weights.items():

            print(

                pattern,

                "Weight:",

                round(weight,2)

            )