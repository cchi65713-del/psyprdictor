"""State Modulation layer for PsyPredictor.

This module sits between BehavioralTendency generation and CompetitionEngine.
It does not choose actions; it only adjusts the strength of an existing tendency
based on the person's current state.

The initial implementation intentionally uses a minimal, explicit rule set so the
architecture can support future more nuanced factors without redesigning the.
core mechanism.
"""

from typing import Dict, List, Optional


class StateModulator:
    """Applies transparent, deterministic state-based modulation to a tendency."""

    # Minimal rule set. Explicit names allow future extension without changing the
    # public interface.
    STATE_FACTORS = {
        "neutral": 1.0,
        "calm": 1.0,
        "confident": 1.02,
        "defensive": 1.08,
        "threatened": 1.15,
        "overwhelmed": 0.82,
        "confused": 0.9,
    }

    def __init__(self):
        self.state_factors = self.STATE_FACTORS.copy()

    def _read_state(self, person_state) -> Dict[str, object]:
        """Read the current state values from a PersonState-like object."""
        if person_state is None:
            return {
                "state_of_mind": {},
                "emotion": None,
                "feeling": None,
                "mood": None,
            }

        state_of_mind = getattr(person_state, "state_of_mind", {}) or {}
        emotion = getattr(person_state, "emotion", None)
        feeling = getattr(person_state, "feeling", None)
        mood = getattr(person_state, "mood", None)

        return {
            "state_of_mind": state_of_mind,
            "emotion": emotion,
            "feeling": feeling,
            "mood": mood,
        }

    def _state_factor_for(self, person_state) -> Optional[float]:
        """Return a single float factor for the currently recognized state.

        This first implementation intentionally does not build complex formulas.
        It only recognizes explicit state labels and their corresponding factors.
        """
        state_data = self._read_state(person_state)
        state_of_mind = state_data["state_of_mind"]
        emotion = state_data["emotion"]
        feeling = state_data["feeling"]
        mood = state_data["mood"]

        # 1) If state_of_mind is a string, match directly.
        if isinstance(state_of_mind, str):
            key = state_of_mind.strip().lower()
            if key in self.state_factors:
                return self.state_factors[key]

        # 2) If state_of_mind is a dict, look for known keys.
        if isinstance(state_of_mind, dict):
            for key, value in state_of_mind.items():
                if value is False:
                    continue
                token = str(key).strip().lower()
                if token in self.state_factors:
                    return self.state_factors[token]

        # 3) Check emotion/feeling/mood strings.
        for token in (emotion, feeling, mood):
            if token is None:
                continue
            key = str(token).strip().lower()
            if key in self.state_factors:
                return self.state_factors[key]

        return 1.0

    def modulate(self, tendency, person_state):
        """Apply state-based modulation to a BehavioralTendency.

        Returns the same tendency object with transparent modulation metadata.
        """
        if tendency is None:
            return tendency

        # Preserve original state before modulation for transparency.
        tendency.pre_state_strength = getattr(tendency, "normalized_strength", tendency.raw_strength)

        factor = self._state_factor_for(person_state)
        reasons: List[str] = []

        if factor == 1.0:
            reasons.append("state:neutral")
        else:
            state_data = self._read_state(person_state)
            state_of_mind = state_data["state_of_mind"]
            if isinstance(state_of_mind, dict):
                recognized = [
                    str(k).strip().lower()
                    for k, v in state_of_mind.items()
                    if v is not False and str(k).strip().lower() in self.state_factors
                ]
                if recognized:
                    reasons.append(f"state:{recognized[0]}")
            else:
                key = str(state_of_mind).strip().lower()
                if key in self.state_factors:
                    reasons.append(f"state:{key}")

            for token in (state_data["emotion"], state_data["feeling"], state_data["mood"]):
                if token is None:
                    continue
                key = str(token).strip().lower()
                if key in self.state_factors and key not in reasons:
                    reasons.append(f"state:{key}")
                    break

        tendency.state_modulation_factor = factor
        tendency.state_modulation_reasons = reasons

        # The modulator only changes tendency strength; it does not choose an action.
        tendency.post_state_strength = tendency.pre_state_strength * factor

        # Update the tendency's adjusted strength if present, without overriding the original raw data.
        if hasattr(tendency, "adjusted_strength"):
            tendency.adjusted_strength = tendency.post_state_strength

        return tendency
