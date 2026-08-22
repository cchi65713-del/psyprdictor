"""EFMSOMB taxonomy definitions.

This module defines a compact, architecture-safe EFMSOMB vocabulary and schema.
It is intentionally separate from the decision layer: the repository's actual
behavior selection remains driven by the canonical dynamic person state and the
competition engine, while EFMSOMB here acts as a structured state description.

The goal is to keep the taxonomy expressive enough for runtime state tracking,
pattern learning, and appraisal, without turning EFMSOMB into a new decision
source or letting it overtake the architecture.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


_VALID_VALENCE = {"positive", "negative", "mixed", "neutral"}


def _validate_float(value: float, *, min_value: float = 0.0, max_value: float = 1.0, name: str = "value") -> float:
    """Validate a bounded float used in the taxonomy.

    Values are intentionally kept within 0..1 for consistency with the rest of
    the runtime state model and to avoid overcomplicated cardinality.
    """
    numeric = float(value)
    if numeric < min_value or numeric > max_value:
        raise ValueError(f"{name} must be between {min_value} and {max_value}.")
    return numeric


def validate_emotion_state(state: EmotionState) -> EmotionState:
    """Validate a structured emotion state."""
    if state.label not in EMOTION_STARTER:
        raise ValueError(f"Unknown emotion label: {state.label}")
    state.intensity = _validate_float(state.intensity, name="emotion.intensity")
    if state.valence not in _VALID_VALENCE:
        raise ValueError(f"Unsupported emotion valence: {state.valence}")
    state.confidence = _validate_float(state.confidence, name="emotion.confidence")
    return state


def validate_feeling_state(state: FeelingState) -> FeelingState:
    """Validate a structured feeling state."""
    if state.quality not in FEELING_STARTER:
        raise ValueError(f"Unknown feeling quality: {state.quality}")
    state.intensity = _validate_float(state.intensity, name="feeling.intensity")
    state.salience = _validate_float(state.salience, name="feeling.salience")
    return state


def validate_mood_state(state: MoodState) -> MoodState:
    """Validate a structured mood state."""
    if state.tone not in MOOD_STARTER:
        raise ValueError(f"Unknown mood tone: {state.tone}")
    state.intensity = _validate_float(state.intensity, name="mood.intensity")
    state.drift = _validate_float(state.drift, name="mood.drift")
    state.decay = _validate_float(state.decay, name="mood.decay")
    return state


def validate_state_of_mind_state(state: StateOfMindState) -> StateOfMindState:
    """Validate a state-of-mind state."""
    if state.frame not in STATE_OF_MIND_STARTER:
        raise ValueError(f"Unknown state-of-mind frame: {state.frame}")
    state.control_level = _validate_float(state.control_level, name="state_of_mind.control_level")
    state.flexibility = _validate_float(state.flexibility, name="state_of_mind.flexibility")
    return state


def validate_behavior_signature(state: BehaviorSignature) -> BehaviorSignature:
    """Validate a behavior signature."""
    if state.signature not in BEHAVIOR_STARTER:
        raise ValueError(f"Unknown behavior signature: {state.signature}")
    state.confidence = _validate_float(state.confidence, name="behavior.confidence")
    state.intensity = _validate_float(state.intensity, name="behavior.intensity")
    return state


@dataclass
class EmotionState:
    """Structured emotion description.

    Fields intentionally stay narrow: semantic label, intensity, valence,
    confidence, and optional trigger metadata. This keeps the taxonomy useful
    for state tracking and learned pattern encoding without overloading it.
    """

    label: str
    intensity: float = 0.0
    valence: str = "neutral"  # positive / negative / mixed / neutral
    confidence: float = 0.0
    trigger_ref: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass
class FeelingState:
    """Subjective felt quality beneath a named emotion label."""

    quality: str
    texture: str = "neutral"  # sharp / diffuse / heavy / numb / warm / hollow / etc.
    intensity: float = 0.0
    salience: float = 0.0
    source_ref: Optional[str] = None


@dataclass
class MoodState:
    """Longer-duration background affective tone."""

    tone: str
    intensity: float = 0.0
    drift: float = 0.0
    decay: float = 0.0
    baseline_anchor: str = "neutral"


@dataclass
class StateOfMindState:
    """Interpretive frame and regulatory posture of the current moment."""

    frame: str
    regulation_mode: str = "neutral"
    cognitive_bias: str = "neutral"
    control_level: float = 0.0
    flexibility: float = 0.0


@dataclass
class BehaviorSignature:
    """Observed or selected behavior signature."""

    signature: str
    mode: str = "observed"  # observed / selected / predicted
    confidence: float = 0.0
    intensity: float = 0.0
    context_ref: Optional[str] = None
    outcome_ref: Optional[str] = None


EMOTION_STARTER = [
    "anger",
    "fear",
    "sadness",
    "joy",
    "shame",
    "surprise",
    "disgust",
    "frustration",
    "anxiety",
    "relief",
    "guilt",
    "pride",
    "contempt",
    "loneliness",
    "hope",
    "confusion",
    "irritation",
    "excitement",
    "empathy",
    "envy",
]


FEELING_STARTER = [
    "disrespected",
    "threatened",
    "dismissed",
    "included",
    "ashamed",
    "relieved",
    "energized",
    "unsafe",
    "numb",
    "calm",
    "uneasy",
    "hopeful",
    "trapped",
    "validated",
    "confused",
    "bitter",
    "warm",
    "exposed",
    "rejected",
    "self-conscious",
]


MOOD_STARTER = [
    "calm",
    "tense",
    "irritable",
    "hopeful",
    "withdrawn",
    "neutral",
    "restless",
    "heavy",
    "buoyant",
    "guarded",
    "gloomy",
    "energized",
    "flat",
    "vigilant",
    "warm",
]


STATE_OF_MIND_STARTER = [
    "defensive",
    "open",
    "vigilant",
    "avoidant",
    "self-protective",
    "collaborative",
    "hyperfocused",
    "overwhelmed",
    "rational",
    "resentful",
    "disengaged",
    "hopeful",
    "suspicious",
    "anxious",
    "controlled",
    "impulsive",
    "reflective",
    "exhausted",
    "assertive",
    "compliant",
]


BEHAVIOR_STARTER = [
    "respond_immediately",
    "stay_quiet",
    "walk_away",
    "negotiate",
    "withdraw",
    "self_critique",
    "seek_support",
    "deflect",
    "confront",
    "comply",
    "escalate",
    "soothe",
    "hide",
    "persist",
    "adapt",
    "disengage",
    "assert_boundaries",
    "apologize",
    "explain",
    "project_blame",
]


__all__ = [
    "EmotionState",
    "FeelingState",
    "MoodState",
    "StateOfMindState",
    "BehaviorSignature",
    "EMOTION_STARTER",
    "FEELING_STARTER",
    "MOOD_STARTER",
    "STATE_OF_MIND_STARTER",
    "BEHAVIOR_STARTER",
]
