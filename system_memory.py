class SystemMemory:


    def __init__(self):

        self.beliefs = {}

        self.values = {}

        self.environment = {}

        self.history = {}

        self.relationships = {}

        self.rules = {}



    # ==========================================
    # ADD BELIEF
    # ==========================================

    def add_belief(
        self,
        person,
        belief
    ):

        if person not in self.beliefs:

            self.beliefs[person] = []


        self.beliefs[person].append(
            belief
        )



    # ==========================================
    # ADD VALUE
    # ==========================================

    def add_value(
        self,
        person,
        value
    ):

        if person not in self.values:

            self.values[person] = []


        self.values[person].append(
            value
        )



    # ==========================================
    # ADD ENVIRONMENT
    # ==========================================

    def add_environment(
        self,
        person,
        environment
    ):

        self.environment[person] = environment



    # ==========================================
    # ADD HISTORY
    # ==========================================

    def add_history(
        self,
        person,
        event
    ):

        if person not in self.history:

            self.history[person] = []


        self.history[person].append(
            event
        )



    # ==========================================
    # ADD RELATIONSHIP
    # ==========================================

    def add_relationship(
        self,
        person,
        relationship
    ):

        if person not in self.relationships:

            self.relationships[person] = []


        self.relationships[person].append(
            relationship
        )



    # ==========================================
    # ADD LEARNED RULE
    # ==========================================

    def add_rule(
        self,
        person,
        rule
    ):

        if person not in self.rules:

            self.rules[person] = []


        self.rules[person].append(
            rule
        )



    # ==========================================
    # GET PERSON MEMORY
    # ==========================================

    def get_memory(
        self,
        person
    ):

        return {

            "beliefs":
            self.beliefs.get(
                person,
                []
            ),


            "values":
            self.values.get(
                person,
                []
            ),


            "environment":
            self.environment.get(
                person,
                None
            ),


            "history":
            self.history.get(
                person,
                []
            ),


            "relationships":
            self.relationships.get(
                person,
                []
            ),


            "rules":
            self.rules.get(
                person,
                []
            )
        }



    # ==========================================
    # SHOW MEMORY
    # ==========================================

    def show(
        self,
        person
    ):

        memory = self.get_memory(
            person
        )


        print(
            "\n===== SYSTEM MEMORY ====="
        )


        print(
            f"Person: {person}"
        )


        for category, data in memory.items():

            print(
                f"\n{category.upper()}:"
            )

            print(data)


    # ==========================================
    # ASSESS TENDENCY
    # ==========================================

    def assess_tendency(
        self,
        person,
        tendency
    ):
        """
        Inspect stored memory for `person` and return a multiplicative
        adjustment factor and reasons for the given `tendency`.

        Returns: (factor: float, reasons: List[str])

        Factor semantics (suggested):
            neutral -> 1.0
            support  -> up to 1.1
            oppose   -> down toward 0.7
            forbid/violate -> down toward 0.3

        The final factor is clamped to [0.3, 1.1].
        """

        base = 1.0
        reasons = []

        # Quick access
        person_rules = self.rules.get(person, [])

        # Rules are flexible: allow simple string forms like
        # 'support:WalkAway', 'oppose:RespondImmediately', 'forbid:Action'
        for rule in person_rules:

            if not isinstance(rule, str):
                # ignore unrecognized rule formats for now
                continue

            parts = rule.split(":", 1)
            if len(parts) != 2:
                continue

            effect = parts[0].strip().lower()
            action = parts[1].strip()

            if action != tendency.action:
                continue

            if effect in ("forbid", "strongly_oppose", "violate"):
                # Strong rule violation: immediate heavy penalty
                base = min(base, 0.3)
                reasons.append(f"rule:{rule}")

            elif effect in ("oppose", "against"):
                # Moderate opposition
                base *= 0.8
                reasons.append(f"rule:{rule}")

            elif effect in ("support", "favor"):
                # Mild support
                base *= 1.05
                reasons.append(f"rule:{rule}")

        # Additional simple heuristics (non-exhaustive): beliefs/values can
        # contain keywords stating support/oppose in free text. Check for
        # exact mentions of the action name.
        for category in ("beliefs", "values", "history", "relationships"):

            items = getattr(self, category).get(person, [])

            for it in items:
                try:
                    text = str(it).lower()
                except Exception:
                    continue

                if tendency.action.lower() in text:
                    # If memory mentions the action positively, apply small boost
                    if "not " in text or "avoid" in text or "no " in text:
                        base *= 0.9
                        reasons.append(f"{category}:{it}")
                    else:
                        base *= 1.03
                        reasons.append(f"{category}:{it}")

        # Clamp to allowed range
        factor = max(0.3, min(1.1, base))

        return factor, reasons

    # ==========================================
    # FIND RELATED MEANINGS
    # ==========================================

    @staticmethod
    def _normalize_tokens(value):
        if value is None:
            return set()
        text = str(value).lower().replace("_", " ").replace("-", " ")
        return {token for token in text.split() if token}

    @classmethod
    def _compute_similarity_score(cls, current_tags, current_dimensions, memory_event):
        if not isinstance(memory_event, dict):
            return 0.0
        if memory_event.get("type") != "state_learning":
            return 0.0

        mem = memory_event.get("memory_ref") or {}
        cname = memory_event.get("canonical_name") or (mem.get("canonical_name") if isinstance(mem, dict) else None)
        dims = memory_event.get("dimensions") or (mem.get("dimensions") if isinstance(mem, dict) else {})
        if not isinstance(dims, dict):
            dims = {}
        if not isinstance(current_dimensions, dict):
            current_dimensions = {}

        tag_tokens = set()
        for tag in current_tags or []:
            tag_tokens |= cls._normalize_tokens(tag)

        name_tokens = cls._normalize_tokens(cname)
        tag_overlap = 0.0
        if tag_tokens and name_tokens:
            overlap = len(tag_tokens & name_tokens)
            union = len(tag_tokens | name_tokens)
            tag_overlap = (overlap / union) if union else 0.0

        dim_score = 0.0
        if dims and current_dimensions:
            shared_keys = [k for k in dims.keys() if k in current_dimensions]
            if shared_keys:
                values = []
                for key in shared_keys:
                    try:
                        stored = float(dims.get(key, 0.0))
                        current = float(current_dimensions.get(key, 0.0))
                        values.append(1.0 - abs(stored - current))
                    except Exception:
                        continue
                if values:
                    dim_score = sum(values) / len(values)

        score = 0.0
        if tag_overlap > 0.0:
            score = max(score, 0.7 * tag_overlap)
        if dim_score > 0.0:
            score = max(score, 0.5 * dim_score)
        if cname and tag_tokens:
            cname_l = str(cname).lower()
            if any(str(tag).lower() == cname_l for tag in current_tags or []):
                score = max(score, 0.85)
            elif any(str(tag).lower() in cname_l or cname_l in str(tag).lower() for tag in current_tags or []):
                score = max(score, 0.65)

        if score < 0.0:
            return 0.0
        if score > 1.0:
            return 1.0
        return score

    def find_related_meanings(self, tags, person, time_window_seconds=None, limit=3, current_dimensions=None):
        """
        Minimal lookup for memories related to `tags` for a specific `person`.

        - Searches `self.history[person]` for `state_learning` events exported by StateManager.
        - Each memory gets a bounded similarity_score in [0,1] based on overlapping tags and
          dimension alignment with the current interpretation context.
        - Returns a list of dicts with at least `memory_id` and optionally `similarity_score`.
        """
        if not tags:
            return []
        try:
            person_history = self.history.get(person, [])
        except Exception:
            return []

        tags_l = [str(t).lower() for t in tags if t]
        matches = []
        for ev in reversed(person_history):
            try:
                if not isinstance(ev, dict):
                    continue
                if ev.get("type") != "state_learning":
                    continue
                mem = ev.get("memory_ref") or {}
                mem_id = ev.get("memory_id") or mem.get("state_id") or mem.get("memory_id")
                cname = ev.get("canonical_name") or (mem.get("canonical_name") if isinstance(mem, dict) else None)
                similarity = self._compute_similarity_score(tags_l, current_dimensions, ev)
                if cname:
                    cname_l = str(cname).lower()
                    if any(t in cname_l or t == cname_l for t in tags_l):
                        matches.append({"memory_id": mem_id, "canonical_name": cname, "timestamp": mem.get("timestamp"), "source_event": ev, "similarity_score": similarity})
                else:
                    if mem_id and any(t == str(mem_id).lower() for t in tags_l):
                        matches.append({"memory_id": mem_id, "canonical_name": None, "timestamp": mem.get("timestamp"), "source_event": ev, "similarity_score": similarity})
            except Exception:
                continue
            if len(matches) >= (limit or 3):
                break

        if not matches:
            for ev in reversed(person_history):
                try:
                    if not isinstance(ev, dict):
                        continue
                    if ev.get("type") != "state_learning":
                        continue
                    mem = ev.get("memory_ref") or {}
                    mem_id = ev.get("memory_id") or mem.get("state_id") or mem.get("memory_id")
                    cname = ev.get("canonical_name") or (mem.get("canonical_name") if isinstance(mem, dict) else None)
                    similarity = self._compute_similarity_score(tags_l, current_dimensions, ev)
                    matches.append({"memory_id": mem_id, "canonical_name": cname, "timestamp": mem.get("timestamp"), "source_event": ev, "similarity_score": similarity})
                except Exception:
                    continue
                if len(matches) >= (limit or 3):
                    break

        return matches