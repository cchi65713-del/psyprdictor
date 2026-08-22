"""Canonical person-model contract for PsyPredictor.

This module defines the explicit layers that make up a person for prediction and
behavior modeling:

- stable: identity, personality, values, beliefs, relationships
- semi_stable: needs, goals, standards, preferences
- dynamic: perception, appraisal, emotion, mood, arousal, regulation
- learning: memory, habits, patterns, expectations
- meta: confidence, awareness, uncertainty, metacognition

The goal is to give the codebase a single contract that all modules can read and
write from, while keeping legacy PersonState aliases for compatibility.
"""

from __future__ import annotations

from typing import Any, Dict


class PersonModelContract:
    """Explicit, canonical model of a person.

    This object is intentionally lightweight and acts as the shared contract that
    binds the rest of the system together.
    """

    def __init__(self):
        self.layers: Dict[str, Dict[str, Any]] = {
            "stable": {
                "person_id": None,
                "identity": {},
                "personality": {},
                "values": [],
                "beliefs": {},
                "relationships": [],
            },
            "semi_stable": {
                "needs": {},
                "goals": [],
                "standards": [],
                "preferences": {},
            },
            "dynamic": {
                "perception": {},
                "appraisal": {},
                "emotion": None,
                "mood": None,
                "arousal": 0.0,
                "regulation": 0.5,
                "attention": {},
            },
            "learning": {
                "memory": {},
                "habits": {},
                "patterns": [],
                "expectations": {},
            },
            "meta": {
                "confidence": 0.5,
                "awareness": 0.5,
                "uncertainty": 0.0,
                "metacognition": {},
            },
        }
        self.stable = self.layers["stable"]
        self.semi_stable = self.layers["semi_stable"]
        self.dynamic = self.layers["dynamic"]
        self.learning = self.layers["learning"]
        self.meta = self.layers["meta"]

    def sync_from_person_state(self, person_state: Any):
        """Synchronize the contract with the current PersonState instance."""
        identity = getattr(person_state, "identity", None)
        if identity is None:
            identity = {}
        personality = getattr(person_state, "personality", None)
        if personality is None:
            personality = {}
        value_weights = getattr(person_state, "value_weights", None)
        if value_weights is None:
            value_weights = []
        beliefs = getattr(person_state, "beliefs", None)
        if beliefs is None:
            beliefs = {}
        need_state = getattr(person_state, "need_state", getattr(person_state, "needs", None))
        if need_state is None:
            need_state = {}
        active_goals = getattr(person_state, "active_goals", getattr(person_state, "goals", None))
        if active_goals is None:
            active_goals = []
        preferences = getattr(person_state, "preferences", None)
        if preferences is None:
            preferences = {}
        perception = getattr(person_state, "perception", None)
        if perception is None:
            perception = {}
        appraisal = getattr(person_state, "appraisal", None)
        if appraisal is None:
            appraisal = {}
        attention = getattr(person_state, "attention", None)
        if attention is None:
            attention = {}
        memory = getattr(person_state, "history", None)
        if memory is None:
            memory = {}
        habit_strength = getattr(person_state, "habit_strength", None)
        if habit_strength is None:
            habit_strength = {}
        active_patterns = getattr(person_state, "active_patterns", None)
        if active_patterns is None:
            active_patterns = []
        expectations = getattr(person_state, "expectations", None)
        if expectations is None:
            expectations = {}
        meta_confidence = getattr(person_state, "state_meta_confidence", getattr(person_state, "confidence", 0.5))
        awareness = getattr(person_state, "awareness", 0.5)

        self.layers["stable"]["person_id"] = getattr(person_state, "person_id", None)
        self.layers["stable"]["identity"] = identity
        self.layers["stable"]["personality"] = personality
        self.layers["stable"]["values"] = value_weights
        self.layers["stable"]["beliefs"] = beliefs
        self.layers["stable"]["relationships"] = identity.get("relationships", []) if isinstance(identity, dict) else []

        self.layers["semi_stable"]["needs"] = need_state
        self.layers["semi_stable"]["goals"] = active_goals
        self.layers["semi_stable"]["standards"] = identity.get("standards", []) if isinstance(identity, dict) else []
        self.layers["semi_stable"]["preferences"] = preferences

        self.layers["dynamic"]["perception"] = perception
        self.layers["dynamic"]["appraisal"] = appraisal
        self.layers["dynamic"]["emotion"] = getattr(person_state, "emotion", None)
        self.layers["dynamic"]["mood"] = getattr(person_state, "mood", None)
        self.layers["dynamic"]["arousal"] = getattr(person_state, "arousal", 0.0)
        self.layers["dynamic"]["regulation"] = getattr(person_state, "state_regulation", getattr(person_state, "self_regulation", 0.5))
        self.layers["dynamic"]["attention"] = attention

        self.layers["learning"]["memory"] = memory
        self.layers["learning"]["habits"] = habit_strength
        self.layers["learning"]["patterns"] = active_patterns
        self.layers["learning"]["expectations"] = expectations

        self.layers["meta"]["confidence"] = meta_confidence
        self.layers["meta"]["awareness"] = awareness
        self.layers["meta"]["uncertainty"] = max(0.0, 1.0 - float(awareness))
        self.layers["meta"]["metacognition"] = getattr(person_state, "metacognition", None)
        if self.layers["meta"]["metacognition"] is None:
            self.layers["meta"]["metacognition"] = {}

    def as_dict(self):
        return {layer_name: dict(values) for layer_name, values in self.layers.items()}
