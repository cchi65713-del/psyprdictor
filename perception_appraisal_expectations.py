"""Minimal Perception → Appraisal → Expectations layer for PsyPredictor.

This module intentionally implements only the first-pass deterministic rules defined
in the approved design: threat, ambiguity, opportunity, neutral/irrelevant, and
associated expectations. It uses runtime dataclasses and does not alter the
competition or arbitration pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class EvidenceRecord:
    field: str
    value: Any
    source: str
    note: str


@dataclass
class Observation:
    type: str
    value: Any
    normalized: Optional[float] = None
    location: Optional[str] = None
    timestamp: Optional[str] = None
    evidence: List[EvidenceRecord] = field(default_factory=list)


@dataclass
class Perception:
    id: str
    timestamp: str
    source: str
    observations: List[Observation]
    confidence: float
    manual: bool = False
    insufficient_data: bool = False
    context_id: Optional[str] = None
    note: Optional[str] = None


@dataclass
class AppraisalFrame:
    id: str
    label: str
    dimension_scores: Dict[str, float]
    supporting_perceptions: List[str]
    evidence: List[EvidenceRecord]
    confidence: float
    manual: bool = False


@dataclass
class Appraisal:
    id: str
    timestamp: str
    source: str
    frames: List[AppraisalFrame]
    confidence: float
    manual: bool = False
    insufficient_data: bool = False
    conflicts: List[str] = field(default_factory=list)


@dataclass
class Prediction:
    outcome_label: str
    probability: float
    supporting_appraisals: List[str]
    evidence: List[EvidenceRecord]
    expected_timeline: Optional[str] = None


@dataclass
class Expectations:
    id: str
    timestamp: str
    source: str
    predictions: List[Prediction]
    confidence: float
    manual: bool = False
    insufficient_data: bool = False


@dataclass
class NormalizedEvent:
    event_type: str
    text: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class Perceptor:
    """Converts raw trigger input into a clean perception object."""

    @staticmethod
    def _extract_text(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, dict):
            for key in ("text", "message", "utterance", "content"):
                result = value.get(key)
                if isinstance(result, str):
                    return result.strip()
            return ""
        return str(value)

    @staticmethod
    def _normalize_trigger(trigger: Any) -> NormalizedEvent:
        if trigger is None:
            return NormalizedEvent(event_type="none", text="", properties={}, metadata={})

        if isinstance(trigger, str):
            return NormalizedEvent(
                event_type="text",
                text=trigger,
                properties={"raw_text": trigger},
                metadata={},
            )

        if isinstance(trigger, dict):
            text = Perceptor._extract_text(trigger)
            props = dict(trigger)
            return NormalizedEvent(
                event_type=str(trigger.get("event_type", "dict")),
                text=text,
                properties=props,
                metadata={
                    "source": trigger.get("source", "trigger"),
                    "raw": trigger,
                },
            )

        attrs = {
            name: getattr(trigger, name)
            for name in (
                "text",
                "message",
                "utterance",
                "event_type",
                "properties",
                "metadata",
                "voice_volume",
                "proximity",
                "gesture",
            )
            if hasattr(trigger, name)
        }

        text = Perceptor._extract_text(attrs.get("text") or attrs.get("message") or attrs.get("utterance") or "")
        properties = dict(attrs.get("properties", {}) or {})
        metadata = dict(attrs.get("metadata", {}) or {})

        for key in ("voice_volume", "proximity", "gesture"):
            if key in attrs and key not in properties:
                properties[key] = attrs[key]

        return NormalizedEvent(
            event_type=str(attrs.get("event_type", "object")),
            text=text,
            properties=properties,
            metadata=metadata,
        )

    @staticmethod
    def _accusatory_phrases() -> List[str]:
        return [
            "you never",
            "you always",
            "you are",
            "you always screw",
            "you never listen",
            "we don't want you here",
            "you always ruin",
            "you screwed up",
        ]

    @staticmethod
    def _offer_phrases() -> List[str]:
        return [
            "i can help",
            "i can assist",
            "let me help",
            "i want to help",
            "good job",
            "thank you",
            "i can do that",
            "offer",
        ]

    @staticmethod
    def _numeric_from_trigger(properties: Dict[str, Any], keys: Sequence[str]) -> Optional[float]:
        for key in keys:
            value = properties.get(key)
            if value is None:
                continue
            try:
                return float(value)
            except (TypeError, ValueError):
                continue
        return None

    @staticmethod
    def _estimate_confidence(observations: Sequence[Observation]) -> float:
        if not observations:
            return 0.0
        return min(1.0, max(0.1, sum(0.2 for _ in observations) + 0.2))

    @staticmethod
    def process(trigger: Any, person_state: Any) -> Perception:
        """Extract minimal observations from a trigger."""
        normalized = Perceptor._normalize_trigger(trigger)
        text = normalized.text.strip()
        observations: List[Observation] = []

        if text:
            utterance_evidence = [
                EvidenceRecord(
                    field="text",
                    value=text,
                    source="trigger",
                    note="Raw utterance extracted from trigger.",
                )
            ]
            observations.append(
                Observation(
                    type="utterance",
                    value=text,
                    normalized=None,
                    evidence=utterance_evidence,
                )
            )

        volume_value = Perceptor._numeric_from_trigger(normalized.properties, ("voice_volume", "volume", "loudness"))
        if volume_value is not None:
            if volume_value > 1.0:
                normalized_volume = min(1.0, volume_value / 100.0)
            else:
                normalized_volume = min(1.0, max(0.0, volume_value))
            label = "high" if normalized_volume >= 0.65 else "normal"
            observations.append(
                Observation(
                    type="voice_volume",
                    value=label,
                    normalized=normalized_volume,
                    evidence=[
                        EvidenceRecord(
                            field="voice_volume",
                            value=volume_value,
                            source="trigger",
                            note="Volume was present in the trigger payload.",
                        )
                    ],
                )
            )

        proximity_value = Perceptor._numeric_from_trigger(normalized.properties, ("proximity", "distance"))
        if proximity_value is not None:
            normalized_distance = min(1.0, max(0.0, proximity_value))
            label = "close" if normalized_distance >= 0.6 else "far"
            observations.append(
                Observation(
                    type="proximity",
                    value=label,
                    normalized=normalized_distance,
                    evidence=[
                        EvidenceRecord(
                            field="proximity",
                            value=proximity_value,
                            source="trigger",
                            note="Spatial proximity was present in the trigger payload.",
                        )
                    ],
                )
            )

        if not observations:
            return Perception(
                id=f"perception-{utc_now_iso()}",
                timestamp=utc_now_iso(),
                source="trigger",
                observations=[],
                confidence=0.0,
                manual=False,
                insufficient_data=True,
                context_id=getattr(person_state, "context", None),
                note="No useful perception content was extracted.",
            )

        confidence = Perceptor._estimate_confidence(observations)
        return Perception(
            id=f"perception-{utc_now_iso()}",
            timestamp=utc_now_iso(),
            source="trigger",
            observations=observations,
            confidence=confidence,
            manual=False,
            insufficient_data=False,
            context_id=getattr(person_state, "context", None),
            note="Deterministic raw observation extraction completed.",
        )


class Appraiser:
    """Assigns interpretation frames using explicit, deterministic rules."""

    @staticmethod
    def _coerce_perceptions(perception_or_list: Union[Perception, Sequence[Perception]]) -> List[Perception]:
        if isinstance(perception_or_list, Perception):
            return [perception_or_list]
        return list(perception_or_list)

    @staticmethod
    def _all_observations(perceptions: Sequence[Perception]) -> List[Observation]:
        gathered: List[Observation] = []
        for perception in perceptions:
            if perception is None:
                continue
            if getattr(perception, "insufficient_data", False):
                continue
            gathered.extend(perception.observations)
        return gathered

    @staticmethod
    def _combined_text(observations: Sequence[Observation]) -> str:
        parts: List[str] = []
        for observation in observations:
            value = observation.value
            if observation.type == "utterance" and isinstance(value, str):
                parts.append(value.lower())
        return " ".join(parts)

    @staticmethod
    def _max_normalized(observations: Sequence[Observation], observation_type: str) -> float:
        values: List[float] = []
        for observation in observations:
            if observation.type == observation_type and observation.normalized is not None:
                values.append(float(observation.normalized))
        return max(values) if values else 0.0

    @staticmethod
    def _accusatory_match(text: str) -> bool:
        lowered = text.lower()
        return any(phrase in lowered for phrase in Perceptor._accusatory_phrases())

    @staticmethod
    def _opportunity_match(text: str) -> bool:
        lowered = text.lower()
        return any(phrase in lowered for phrase in Perceptor._offer_phrases())

    @staticmethod
    def _neutral_or_irrelevant(text: str) -> bool:
        lowered = text.lower().strip()
        if not lowered:
            return True
        if Appraiser._accusatory_match(lowered) or Appraiser._opportunity_match(lowered):
            return False
        return True

    @staticmethod
    def evaluate(perception: Union[Perception, Sequence[Perception]], person_state: Any) -> Appraisal:
        """Evaluate one or more perceptions into appraisal frames."""
        perceptions = Appraiser._coerce_perceptions(perception)
        observations = Appraiser._all_observations(perceptions)

        if not observations:
            return Appraisal(
                id=f"appraisal-{utc_now_iso()}",
                timestamp=utc_now_iso(),
                source="trigger",
                frames=[],
                confidence=0.0,
                manual=False,
                insufficient_data=True,
                conflicts=[],
            )

        text = Appraiser._combined_text(observations)
        volume = Appraiser._max_normalized(observations, "voice_volume")
        proximity = Appraiser._max_normalized(observations, "proximity")
        awareness = getattr(person_state, "awareness", 0.5)
        frames: List[AppraisalFrame] = []
        conflicts: List[str] = []

        threat = Appraiser._accusatory_match(text) or (volume >= 0.65 and proximity >= 0.5)
        ambiguous = (volume >= 0.65 and not Appraiser._accusatory_match(text)) or awareness < 0.35
        opportunity = Appraiser._opportunity_match(text) and not threat

        if threat:
            threat_confidence = 0.85 if volume >= 0.65 else 0.7
            frames.append(
                AppraisalFrame(
                    id=f"appraisal-frame-{utc_now_iso()}",
                    label="threat",
                    dimension_scores={
                        "valence": -0.9,
                        "goal_relevance": 0.8,
                        "controllability": -0.5,
                        "intentionality": 0.8,
                        "suddenness": 0.8,
                        "ambiguity": 0.2,
                        "social_threat": 0.95,
                    },
                    supporting_perceptions=[p.id for p in perceptions if p is not None],
                    evidence=[
                        EvidenceRecord(
                            field="utterance",
                            value=text,
                            source="trigger",
                            note="Accusatory content or high social pressure was detected.",
                        )
                    ],
                    confidence=threat_confidence,
                    manual=False,
                )
            )

        if ambiguous:
            ambiguous_confidence = 0.7 if volume >= 0.65 else 0.55
            frames.append(
                AppraisalFrame(
                    id=f"appraisal-frame-{utc_now_iso()}",
                    label="ambiguity",
                    dimension_scores={
                        "valence": 0.0,
                        "goal_relevance": 0.1,
                        "controllability": -0.2,
                        "intentionality": 0.1,
                        "suddenness": 0.5,
                        "ambiguity": 0.9,
                        "social_threat": 0.2,
                    },
                    supporting_perceptions=[p.id for p in perceptions if p is not None],
                    evidence=[
                        EvidenceRecord(
                            field="signal_conflict",
                            value={"volume": volume, "proximity": proximity, "awareness": awareness},
                            source="trigger",
                            note="Signal conflict or low awareness creates ambiguity.",
                        )
                    ],
                    confidence=ambiguous_confidence,
                    manual=False,
                )
            )
            conflicts.append("mixed or contradictory signals reduce certainty")

        if opportunity:
            opportunity_confidence = 0.8
            frames.append(
                AppraisalFrame(
                    id=f"appraisal-frame-{utc_now_iso()}",
                    label="opportunity",
                    dimension_scores={
                        "valence": 0.8,
                        "goal_relevance": 0.7,
                        "controllability": 0.6,
                        "intentionality": 0.2,
                        "suddenness": 0.3,
                        "ambiguity": 0.2,
                        "social_threat": 0.1,
                    },
                    supporting_perceptions=[p.id for p in perceptions if p is not None],
                    evidence=[
                        EvidenceRecord(
                            field="utterance",
                            value=text,
                            source="trigger",
                            note="Positive or cooperative language indicates an opportunity frame.",
                        )
                    ],
                    confidence=opportunity_confidence,
                    manual=False,
                )
            )

        if not frames:
            if Appraiser._neutral_or_irrelevant(text):
                return Appraisal(
                    id=f"appraisal-{utc_now_iso()}",
                    timestamp=utc_now_iso(),
                    source="trigger",
                    frames=[],
                    confidence=0.0,
                    manual=False,
                    insufficient_data=True,
                    conflicts=["no actionable interpretation cues"],
                )
            return Appraisal(
                id=f"appraisal-{utc_now_iso()}",
                timestamp=utc_now_iso(),
                source="trigger",
                frames=[],
                confidence=0.0,
                manual=False,
                insufficient_data=True,
                conflicts=[],
            )

        aggregate_confidence = min(1.0, sum(frame.confidence for frame in frames) / len(frames))
        return Appraisal(
            id=f"appraisal-{utc_now_iso()}",
            timestamp=utc_now_iso(),
            source="trigger",
            frames=frames,
            confidence=aggregate_confidence,
            manual=False,
            insufficient_data=False,
            conflicts=conflicts,
        )


class ExpectationsGenerator:
    """Creates deterministic short-term expectation predictions."""

    @staticmethod
    def _coerce_appraisals(appraisal_or_list: Union[Appraisal, Sequence[Appraisal]]) -> List[Appraisal]:
        if isinstance(appraisal_or_list, Appraisal):
            return [appraisal_or_list]
        return list(appraisal_or_list)

    @staticmethod
    def update(appraisals: Union[Appraisal, Sequence[Appraisal]], person_state: Any) -> Expectations:
        appraisals_list = ExpectationsGenerator._coerce_appraisals(appraisals)
        flat_frames: List[AppraisalFrame] = []
        for appraisal in appraisals_list:
            if appraisal is None:
                continue
            if appraisal.insufficient_data:
                continue
            flat_frames.extend(appraisal.frames)

        if not flat_frames:
            return Expectations(
                id=f"expectations-{utc_now_iso()}",
                timestamp=utc_now_iso(),
                source="trigger",
                predictions=[],
                confidence=0.0,
                manual=False,
                insufficient_data=True,
            )

        predictions: List[Prediction] = []
        for frame in flat_frames:
            outcome_label = frame.label
            evidence = [
                EvidenceRecord(
                    field="appraisal_label",
                    value=frame.label,
                    source="appraisal",
                    note="Generated from the deterministic appraisal rule set.",
                )
            ]
            if frame.label == "threat":
                predictions.extend(
                    [
                        Prediction(
                            outcome_label="confrontation",
                            probability=0.7,
                            supporting_appraisals=[frame.id],
                            evidence=evidence,
                            expected_timeline="short",
                        ),
                        Prediction(
                            outcome_label="ignore",
                            probability=0.2,
                            supporting_appraisals=[frame.id],
                            evidence=evidence,
                            expected_timeline="short",
                        ),
                        Prediction(
                            outcome_label="apology",
                            probability=0.1,
                            supporting_appraisals=[frame.id],
                            evidence=evidence,
                            expected_timeline="short",
                        ),
                    ]
                )
            elif frame.label == "ambiguity":
                predictions.extend(
                    [
                        Prediction(
                            outcome_label="confrontation",
                            probability=0.3,
                            supporting_appraisals=[frame.id],
                            evidence=evidence,
                            expected_timeline="short",
                        ),
                        Prediction(
                            outcome_label="ignore",
                            probability=0.3,
                            supporting_appraisals=[frame.id],
                            evidence=evidence,
                            expected_timeline="short",
                        ),
                        Prediction(
                            outcome_label="clarify",
                            probability=0.4,
                            supporting_appraisals=[frame.id],
                            evidence=evidence,
                            expected_timeline="short",
                        ),
                    ]
                )
            elif frame.label == "opportunity":
                predictions.extend(
                    [
                        Prediction(
                            outcome_label="cooperation",
                            probability=0.7,
                            supporting_appraisals=[frame.id],
                            evidence=evidence,
                            expected_timeline="short",
                        ),
                        Prediction(
                            outcome_label="acceptance",
                            probability=0.2,
                            supporting_appraisals=[frame.id],
                            evidence=evidence,
                            expected_timeline="short",
                        ),
                        Prediction(
                            outcome_label="no_action_needed",
                            probability=0.1,
                            supporting_appraisals=[frame.id],
                            evidence=evidence,
                            expected_timeline="short",
                        ),
                    ]
                )
            elif frame.label in {"neutral", "irrelevant"}:
                predictions.extend(
                    [
                        Prediction(
                            outcome_label="no_change",
                            probability=0.8,
                            supporting_appraisals=[frame.id],
                            evidence=evidence,
                            expected_timeline="short",
                        )
                    ]
                )

        aggregate_confidence = min(1.0, max(0.0, sum(frame.confidence for frame in flat_frames) / len(flat_frames)))
        return Expectations(
            id=f"expectations-{utc_now_iso()}",
            timestamp=utc_now_iso(),
            source="trigger",
            predictions=predictions,
            confidence=aggregate_confidence,
            manual=False,
            insufficient_data=False,
        )
