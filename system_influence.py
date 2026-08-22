class SystemInfluence:


    def __init__(self):

        self.weights = {

            "belief": 0.15,

            "history": 0.15,

            "environment": 0.10,

            "relationship": 0.10,

            "rule": 0.20

        }



    # ==========================================
    # CALCULATE INFLUENCE
    # ==========================================

    def calculate(
        self,
        system_memory,
        person,
        outcome
    ):


        memory = system_memory.get_memory(
            person
        )


        score = 0



        # BELIEFS

        for belief in memory["beliefs"]:

            if outcome == "B1":

                score += self.weights["belief"]



        # HISTORY

        for event in memory["history"]:

            if "conflict" in event.lower():

                if outcome == "B1":

                    score += self.weights["history"]



        # ENVIRONMENT

        environment = memory["environment"]


        if environment:

            if "conflict" in environment.lower():

                if outcome == "B1":

                    score += self.weights["environment"]



        # RELATIONSHIP

        for relation in memory["relationships"]:

            if "difficult" in relation.lower():

                if outcome == "B1":

                    score += self.weights["relationship"]



        # RULES

        for rule in memory["rules"]:

            if "respond" in rule.lower():

                if outcome == "B1":

                    score += self.weights["rule"]



        return score



    # ==========================================
    # APPLY TO PREDICTION
    # ==========================================

    def adjust_prediction(
        self,
        scores,
        system_memory,
        person
    ):


        adjusted = {}


        for outcome, score in scores.items():


            influence = self.calculate(

                system_memory,

                person,

                outcome

            )


            adjusted[outcome] = (
                score + influence
            )


        return adjusted