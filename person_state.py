"""Person state container with canonical fields and backward-compatible aliases.

This module defines `PersonState` used across the codebase. It exposes
canonical prefixed fields (`trait_personality`, `value_weights`, `need_state`,
`active_goals`, `state_*`) while keeping legacy aliases for compatibility.

It also exposes a canonical person-model contract so the project has one stable,
shared representation of the person across identity, state, memory, goals, and
learning modules.
"""
from typing import Any, Dict, List

from efmsomb_taxonomy import (
    BehaviorSignature,
    EmotionState,
    FeelingState,
    MoodState,
    StateOfMindState,
)
from person_model_contract import PersonModelContract
from efmsomb_registry import label_to_code, code_to_label
import re


class PersonState:
    def __init__(self, person_id: str = "Person1"):
        # Identity
        self.person_id = person_id

        # Environment / perception
        self.context = None
        self.trigger = None
        self.environment: Dict[str, Any] = {}
        self.perception: Dict[str, Any] = {}
        self.attention: Dict[str, Any] = {}
        self.appraisal: Dict[str, Any] = {}
        self.expectations: Dict[str, Any] = {}

        # EFMSOMB (legacy fields kept)
        self.emotion = None
        self.feeling = None
        self.mood = None
        self.state_of_mind: Dict[str, Any] = {}
        self.behavior = None

        # Internal model
        self.beliefs: Dict[str, Any] = {}
        # Canonical value weights (list for now to match earlier shape).
        # Prefer `value_weights` but keep `values` alias for compatibility.
        self.value_weights: List[Any] = []
        self.values = self.value_weights

        # Needs
        self.need_state: Dict[str, float] = {}
        self.needs = self.need_state

        # Goals: `goal_manager` should own lifecycle; provide alias `goals`.
        self.active_goals: List[Dict[str, Any]] = []
        self.goals = self.active_goals

        # Preferences (legacy)
        self.preferences: Dict[str, Any] = {}

        # Personality (traits)
        self.personality: Dict[str, float] = {"aggression": 0.5, "avoidant": 0.5}
        self.trait_personality = self.personality

        self.identity: Dict[str, Any] = {}
        self.identity_schema: Dict[str, Any] = self.identity
        self.history: Dict[str, Any] = {}

        # Canonical person model contract: one explicit contract across all
        # stable, semi-stable, dynamic, learning, and meta layers.
        self.person_model = PersonModelContract()
        self.model = self.person_model

        # Seed the runtime identity with the person's actual identity metadata.
        self.fill_actual_identity(
            name=person_id,
            roles={"self": 1.0},
            standards=[],
        )

        # Body / regulation
        self.physiology: Dict[str, Any] = {}
        self.arousal: float = 0.0
        self.energy: float = 1.0
        self.perceived_control: float = 0.5

        # Canonical state splits to avoid overloading `state_of_mind`
        self.state_appraisal: Dict[str, Any] = {}
        self.state_emotion: List[Any] = []
        self.state_arousal: float = 0.0
        self.state_regulation: float = 0.5
        self.state_meta_confidence: float = 0.5

        # Backwards-compatible fields
        self.confidence = self.state_meta_confidence
        self.awareness = 0.5
        self.self_regulation = self.state_regulation

        # Action process
        self.available_actions: List[str] = []
        self.action_tendencies: Dict[str, Any] = {}
        self.intentions: Dict[str, Any] = {}
        self.selected_action = None
        self.execution = None
        self.outcome = None
        self.consequence = None

        # Learning / patterns
        self.memory_refs: List[Any] = []
        self.active_patterns: List[str] = []
        self.habit_strength: Dict[str, Dict[str, float]] = {}
        self.learning_parameters: Dict[str, Any] = {}

        self.prediction_history: List[Any] = []
        self.feedback_history: List[Any] = []

        # Minimal runtime states container (compatibility)
        self.states = {"active": [], "recent": [], "baseline": {"dimensions": {}, "last_update": None}}

        # Meaning attribution layer
        self.meanings: List[Any] = []

        # Structured canonical EFMSOMB runtime representation
        # Keys: emotion, feeling, mood, state_of_mind, behavior
        # Each value is a dict with at minimum: label, code, and any preserved metadata
        self.efmsomb: Dict[str, Dict[str, Any]] = {}

    def sync_person_model(self):
        """Keep the explicit person-model contract aligned with the runtime state."""
        self.person_model.sync_from_person_state(self)
        return self.person_model

    # ---------------------- Personality helpers ----------------------
    def set_personality_traits(self, **traits) -> Dict[str, float]:
        allowed = set(self.personality.keys())
        for name, value in traits.items():
            if name not in allowed:
                raise ValueError(f"Unsupported personality trait: {name}")
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                raise ValueError(f"Personality trait {name} must be numeric")
            self.personality[name] = max(0.0, min(1.0, numeric))
        self.sync_person_model()
        return self.personality

    def update_personality_trait(self, name: str, value: float):
        return self.set_personality_traits(**{name: value})

    # ---------------------- Context helpers ----------------------
    def update_context(self, context=None, trigger=None, environment=None):
        if context is not None:
            self.context = context
        if trigger is not None:
            self.trigger = trigger
        if environment is not None:
            self.environment = environment
        self.sync_person_model()

    # ---------------------- EFMSOMB helpers ----------------------
    def update_efmsomb(self, emotion=None, feeling=None, mood=None, state_of_mind=None, behavior=None):
        if emotion is not None:
            self.emotion = emotion
        if feeling is not None:
            self.feeling = feeling
        if mood is not None:
            self.mood = mood
        if state_of_mind is not None:
            self.state_of_mind = state_of_mind
        if behavior is not None:
            self.behavior = behavior
        self.sync_person_model()

    def apply_efmsomb_taxonomy(
        self,
        *,
        emotion_state: EmotionState | None = None,
        feeling_state: FeelingState | None = None,
        mood_state: MoodState | None = None,
        state_of_mind_state: StateOfMindState | None = None,
        behavior_state: BehaviorSignature | None = None,
    ):
        """Map EFMSOMB dataclass objects into the canonical dynamic person state.

        This is intentionally an adapter layer: the legacy EFMSOMB fields remain
        available for compatibility, while the canonical dynamic fields remain the
        real architecture sink.
        """
        warnings: List[str] = []

        def _resolve_label_code(value: str | None, category: str):
            """Return (label, code, warning_or_None).

            Accepts either a human-readable label or a canonical code and
            resolves the counterpart via the registry. Does not raise on
            unresolved labels; instead returns code=None and a warning.
            """
            if value is None:
                return None, None, None
            s = str(value).strip()
            if not s:
                return None, None, None
            # If it looks like a code (e.g., E4, S5.1), treat as code
            if re.match(r'^[EFMSBefmsb]\d+(?:\..+)?$', s):
                code = s.upper()
                try:
                    label = code_to_label(code)
                    return label, code, None
                except KeyError:
                    return s, code, f"Invalid code: {code}"
            # Otherwise treat as label
            label = s
            code = label_to_code(label, category=category)
            if code is None:
                return label, None, f"Unknown label for category {category}: {label}"
            return label, code, None

        resolved = {}

        if emotion_state is not None:
            label_input = getattr(emotion_state, "label", None)
            label, code, warn = _resolve_label_code(label_input, "E")
            if warn:
                warnings.append(warn)
            emo = {
                "label": label,
                "code": code,
                "intensity": getattr(emotion_state, "intensity", None),
                "valence": getattr(emotion_state, "valence", None),
                "confidence": getattr(emotion_state, "confidence", None),
                "trigger_ref": getattr(emotion_state, "trigger_ref", None),
                "timestamp": getattr(emotion_state, "timestamp", None),
            }
            self.efmsomb["emotion"] = emo
            self.state_emotion = [
                {k: emo.get(k) for k in ("label", "intensity", "valence", "confidence", "trigger_ref", "timestamp")}
            ]
            self.emotion = emo.get("label")
            resolved["emotion"] = emo

        if feeling_state is not None:
            label_input = getattr(feeling_state, "quality", None)
            label, code, warn = _resolve_label_code(label_input, "F")
            if warn:
                warnings.append(warn)
            feel = {
                "label": label,
                "code": code,
                "texture": getattr(feeling_state, "texture", None),
                "intensity": getattr(feeling_state, "intensity", None),
                "salience": getattr(feeling_state, "salience", None),
                "source_ref": getattr(feeling_state, "source_ref", None),
            }
            self.efmsomb["feeling"] = feel
            self.feeling = feel.get("label")
            self.state_appraisal = {
                **self.state_appraisal,
                "felt_quality": feel.get("label"),
                "texture": feel.get("texture"),
                "salience": feel.get("salience"),
                "source_ref": feel.get("source_ref"),
            }
            resolved["feeling"] = feel

        if mood_state is not None:
            label_input = getattr(mood_state, "tone", None)
            label, code, warn = _resolve_label_code(label_input, "M")
            if warn:
                warnings.append(warn)
            m = {
                "label": label,
                "code": code,
                "intensity": getattr(mood_state, "intensity", None),
                "drift": getattr(mood_state, "drift", None),
                "decay": getattr(mood_state, "decay", None),
                "baseline_anchor": getattr(mood_state, "baseline_anchor", None),
            }
            self.efmsomb["mood"] = m
            self.mood = m.get("label")
            self.state_appraisal = {
                **self.state_appraisal,
                "mood_tone": m.get("label"),
                "mood_intensity": m.get("intensity"),
                "mood_drift": m.get("drift"),
                "mood_decay": m.get("decay"),
            }
            resolved["mood"] = m

        if state_of_mind_state is not None:
            label_input = getattr(state_of_mind_state, "frame", None)
            label, code, warn = _resolve_label_code(label_input, "S")
            if warn:
                warnings.append(warn)
            som = {
                "label": label,
                "code": code,
                "regulation_mode": getattr(state_of_mind_state, "regulation_mode", None),
                "cognitive_bias": getattr(state_of_mind_state, "cognitive_bias", None),
                "control_level": getattr(state_of_mind_state, "control_level", None),
                "flexibility": getattr(state_of_mind_state, "flexibility", None),
            }
            self.efmsomb["state_of_mind"] = som
            self.state_of_mind = {
                "frame": som.get("label"),
                "regulation_mode": som.get("regulation_mode"),
                "cognitive_bias": som.get("cognitive_bias"),
                "control_level": som.get("control_level"),
                "flexibility": som.get("flexibility"),
            }
            self.state_regulation = float(som.get("control_level") or self.state_regulation)
            self.self_regulation = float(som.get("control_level") or self.self_regulation)
            self.state_appraisal = {
                **self.state_appraisal,
                "state_of_mind_frame": som.get("label"),
                "regulation_mode": som.get("regulation_mode"),
                "cognitive_bias": som.get("cognitive_bias"),
                "state_flexibility": som.get("flexibility"),
            }
            resolved["state_of_mind"] = som

        if behavior_state is not None:
            label_input = getattr(behavior_state, "signature", None)
            label, code, warn = _resolve_label_code(label_input, "B")
            if warn:
                warnings.append(warn)
            beh = {
                "label": label,
                "code": code,
                "mode": getattr(behavior_state, "mode", None),
                "confidence": getattr(behavior_state, "confidence", None),
                "intensity": getattr(behavior_state, "intensity", None),
                "context_ref": getattr(behavior_state, "context_ref", None),
                "outcome_ref": getattr(behavior_state, "outcome_ref", None),
            }
            self.efmsomb["behavior"] = beh
            self.behavior = beh.get("label")
            self.action_tendencies = {
                **self.action_tendencies,
                "behavior_signature": beh.get("label"),
                "behavior_mode": beh.get("mode"),
            }
            resolved["behavior"] = beh

        # Keep the top-level legacy fields in sync (already set above per-dimension)
        self.sync_person_model()
        # Return a compatibility-friendly flat mapping that preserves the
        # legacy shape expected by tests and external callers. Include both
        # the concise top-level labels (emotion/feeling/mood/behavior) and
        # the richer structured `resolved` map plus any warnings.
        return {
            "emotion": self.emotion,
            "feeling": self.feeling,
            "mood": self.mood,
            "behavior": self.behavior,
            "state_emotion": self.state_emotion,
            "state_appraisal": self.state_appraisal,
            "state_regulation": self.state_regulation,
            "resolved": resolved,
            "warnings": warnings,
        }

    def update(self, **kwargs):
        """Convenience updater: supports context and EFMSOMB keys plus any existing attribute."""
        ctx = kwargs.get("context")
        trig = kwargs.get("trigger")
        env = kwargs.get("environment")
        if (ctx is not None) or (trig is not None) or (env is not None):
            self.update_context(context=ctx, trigger=trig, environment=env)

        if any(k in kwargs for k in ("emotion", "feeling", "mood", "state_of_mind", "behavior")):
            self.update_efmsomb(
                emotion=kwargs.get("emotion"),
                feeling=kwargs.get("feeling"),
                mood=kwargs.get("mood"),
                state_of_mind=kwargs.get("state_of_mind"),
                behavior=kwargs.get("behavior"),
            )

        # Set other provided attributes if they exist on the object
        handled = {"context", "trigger", "environment", "emotion", "feeling", "mood", "state_of_mind", "behavior"}
        for key, value in kwargs.items():
            if key in handled:
                continue
            if hasattr(self, key) and value is not None:
                try:
                    setattr(self, key, value)
                except Exception:
                    pass
        self.sync_person_model()

    # ---------------------- Memory / patterns / actions ----------------------
    def fill_actual_identity(self, *, name=None, roles=None, standards=None, values=None, beliefs=None, relationships=None):
        """Populate the actual identity for this person in a reusable schema.

        The runtime identity keeps the canonical person metadata needed by
        downstream planners (e.g. goal generation and appraisal). It is
        intentionally conservative: it preserves any existing relationships and
        augments the identity from the current values, beliefs, and person id.
        """
        base_identity = self.identity if isinstance(self.identity, dict) else {}
        if not isinstance(base_identity, dict):
            base_identity = {}

        if name is None:
            name = getattr(self, "name", None) or self.person_id

        if roles is None:
            roles = base_identity.get("roles", {})
        if standards is None:
            standards = base_identity.get("standards", [])
        if values is None:
            raw_values = getattr(self, "value_weights", [])
            if isinstance(raw_values, dict):
                values = list(raw_values.keys())
            elif isinstance(raw_values, list):
                values = []
                for item in raw_values:
                    if isinstance(item, dict):
                        values.append(item.get("id") or item.get("name") or str(item))
                    else:
                        values.append(str(item))
            else:
                values = []
        if beliefs is None:
            raw_beliefs = getattr(self, "beliefs", {})
            if isinstance(raw_beliefs, dict):
                beliefs = list(raw_beliefs.get("explicit", []))
            elif isinstance(raw_beliefs, list):
                beliefs = list(raw_beliefs)
            else:
                beliefs = []
        if relationships is None:
            relationships = base_identity.get("relationships", [])

        actual_identity = dict(base_identity)
        actual_identity.update({
            "person_id": self.person_id,
            "name": name,
            "roles": dict(roles or {}),
            "standards": list(standards or []),
            "values": list(values or []),
            "beliefs": list(beliefs or []),
            "relationships": list(relationships or []),
            "summary": f"{name} ({self.person_id})",
        })

        self.identity = actual_identity
        self.identity_schema = self.identity
        self.sync_person_model()
        self.refresh_goals()
        return self.identity

    def refresh_goals(self, max_goals: int = 5):
        """Generate active goals from the current values, needs, and identity."""
        from goal_manager import GoalManager

        value_weights = getattr(self, "value_weights", {})
        need_state = getattr(self, "need_state", getattr(self, "needs", {}))
        identity_schema = getattr(self, "identity_schema", self.identity) or {}
        manager = GoalManager()
        self.active_goals = manager.generate_goals(
            value_weights=value_weights,
            need_state=need_state,
            identity_schema=identity_schema,
            max_goals=max_goals,
        )
        self.goals = self.active_goals
        self.sync_person_model()
        return self.active_goals

    def add_memory_ref(self, memory_ref: Any):
        if memory_ref not in self.memory_refs:
            self.memory_refs.append(memory_ref)

    def add_active_pattern(self, pattern_id: str):
        if pattern_id not in self.active_patterns:
            self.active_patterns.append(pattern_id)

    def remove_active_pattern(self, pattern_id: str):
        if pattern_id in self.active_patterns:
            self.active_patterns.remove(pattern_id)

    def add_available_action(self, action: str):
        if action not in self.available_actions:
            self.available_actions.append(action)

    def clear_actions(self):
        self.available_actions = []
        self.action_tendencies = {}
        self.intentions = {}
        self.selected_action = None

    def record_prediction(self, prediction: Any):
        self.prediction_history.append(prediction)

    def record_feedback(self, feedback: Any):
        self.feedback_history.append(feedback)

    def snapshot(self) -> Dict[str, Any]:
        snapshot = {}
        for key, value in self.__dict__.items():
            if isinstance(value, dict):
                snapshot[key] = value.copy()
            elif isinstance(value, list):
                snapshot[key] = value.copy()
            elif isinstance(value, set):
                snapshot[key] = value.copy()
            else:
                snapshot[key] = value
        return snapshot

    def show(self):
        print("\n==========================================")
        print("PERSON STATE")
        print("==========================================")
        print("Person ID:", self.person_id)
        print("\n--- CURRENT SITUATION ---")
        print("Context:", self.context)
        print("Trigger:", self.trigger)
        print("Environment:", self.environment)
        print("\n--- EFMSOMB ---")
        print("Emotion:", self.emotion)
        print("Feeling:", self.feeling)
        print("Mood:", self.mood)
        print("State of Mind:", self.state_of_mind)
        print("Behavior:", self.behavior)
        print("\n--- INTERNAL MODEL ---")
        print("Beliefs:", self.beliefs)
        print("Values:", self.values)
        print("Needs:", self.needs)
        print("Goals:", self.goals)
        print("Preferences:", self.preferences)
        print("Personality:", self.personality)
        print("Identity:", self.identity)
        print("\n--- REGULATION ---")
        print("Arousal:", self.arousal)
        print("Energy:", self.energy)
        print("Perceived Control:", self.perceived_control)
        print("Confidence:", self.confidence)
        print("Awareness:", self.awareness)
        print("Self Regulation:", self.self_regulation)
        print("\n--- ACTION ---")
        print("Available Actions:", self.available_actions)
        print("Action Tendencies:", self.action_tendencies)
        print("Intentions:", self.intentions)
        print("Selected Action:", self.selected_action)
        print("Execution:", self.execution)
        print("Outcome:", self.outcome)
        print("Consequence:", self.consequence)
        print("\n--- LEARNING ---")
        print("Memory References:", self.memory_refs)
        print("Active Patterns:", self.active_patterns)
        print("Habit Strength:", self.habit_strength)
        print("Learning Parameters:", self.learning_parameters)
        print("==========================================")