"""Meaning Attribution read-only skeleton.

Implements dataclasses and a deterministic `interpret()` function following
`meaning_interpretation.md`. This module is pure/read-only: it does not
modify `person_state`, call `StateManager`, or alter downstream behavior.
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone
import uuid

from perception_appraisal_expectations import Appraisal, AppraisalFrame, Expectations
from perception_appraisal_expectations import EvidenceRecord as PercepEvidence
from state_manager import EvidenceRecord as StateEvidenceRecord


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def uid() -> str:
    return str(uuid.uuid4())


@dataclass
class MeaningFrame:
    id: str
    timestamp: str
    interpretation: str
    interpretation_alternatives: List[Tuple[str, float]] = field(default_factory=list)
    personal_relevance: float = 0.0
    affected_values: List[str] = field(default_factory=list)
    activated_goals: List[str] = field(default_factory=list)
    motivation_direction: Optional[str] = None
    predicted_self_view_change: Optional[str] = None
    confidence: float = 0.0
    supporting_appraisals: List[str] = field(default_factory=list)
    supporting_expectations: List[str] = field(default_factory=list)
    supporting_memory_refs: List[str] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    persistence_hint: str = "transient"
    derived_state_suggestions: Dict[str, Any] = field(default_factory=dict)
    uncertainty: float = 0.0
    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MeaningResult:
    meaning_frames: List[MeaningFrame] = field(default_factory=list)
    aggregate_relevance: float = 0.0
    primary_meaning: Optional[str] = None
    conflicts: List[str] = field(default_factory=list)
    insufficient_data: bool = False


def _clamp01(x: float) -> float:
    try:
        if x is None:
            return 0.0
        return max(0.0, min(1.0, float(x)))
    except Exception:
        return 0.0


def decay_meaning_influence(meaning_frame: MeaningFrame, elapsed_seconds: float, half_life_seconds: float = 43200.0) -> float:
    """Decay a meaning's influence over time. This is a pure read-only helper for evaluation tests."""
    if meaning_frame is None:
        return 0.0
    base = _clamp01(getattr(meaning_frame, "personal_relevance", 0.0) * getattr(meaning_frame, "confidence", 0.0))
    if elapsed_seconds <= 0:
        return base
    window = max(1.0, float(half_life_seconds))
    decay = 0.5 ** (float(elapsed_seconds) / window)
    return _clamp01(base * decay)


def _self_reports_for(person_state: Any) -> List[str]:
    if person_state is None:
        return []
    reports = getattr(person_state, "self_reports", None)
    if isinstance(reports, (list, tuple)):
        return [str(r) for r in reports if str(r).strip()]
    if isinstance(reports, str):
        return [reports]
    return []


def _memory_support_score(memory_matches: List[Dict[str, Any]]) -> float:
    if not memory_matches:
        return 0.0
    scores = []
    for entry in memory_matches:
        try:
            raw_score = (entry or {}).get("similarity_score")
            if raw_score is None:
                raw_score = (entry or {}).get("relevance_score", 0.0)
            score = float(raw_score or 0.0)
            if score < 0.0:
                score = 0.0
            if score > 1.0:
                score = 1.0
            scores.append(score)
        except Exception:
            continue
    if not scores:
        return 0.0

    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    if max_score <= 0.05 and avg_score <= 0.05:
        return 0.0

    if max_score >= 0.9 and avg_score >= 0.9:
        return 1.0

    # Keep memory support bounded and count-dampened: a large number of weakly similar
    # memories cannot overpower one strong current-event interpretation through sheer count.
    support = 0.15 + (avg_score * 0.75)
    if max_score > 0.8:
        support += 0.1 * max_score
    return _clamp01(min(1.0, support))


def _apply_memory_influence(frame: MeaningFrame, memory_matches: List[Dict[str, Any]]) -> MeaningFrame:
    if not memory_matches:
        return frame
    support = _memory_support_score(memory_matches)
    if support <= 0.0:
        return frame

    frame.personal_relevance = _clamp01(frame.personal_relevance + 0.12 + support * 0.18)
    frame.confidence = _clamp01(frame.confidence + 0.06 + support * 0.16)
    frame.persistence_hint = "sustained"

    ds = dict(frame.derived_state_suggestions.get("dims", {}) or {})
    updated_dims = {}
    for key, value in ds.items():
        try:
            updated_dims[key] = _clamp01(float(value) + 0.08 + support * 0.10)
        except Exception:
            updated_dims[key] = value
    if updated_dims:
        frame.derived_state_suggestions["dims"] = updated_dims

    frame.provenance["memory_influence"] = support
    frame.evidence.append({
        "source": "memory_support",
        "memory_refs": [m.get("memory_id") for m in memory_matches if isinstance(m, dict)],
        "support_score": support,
    })
    return frame


def _add_self_report_evidence(frame: MeaningFrame, person_state: Any) -> None:
    reports = _self_reports_for(person_state)
    if not reports:
        return
    frame.evidence.append({
        "source": "self_report",
        "text": reports[0],
        "accepted_as_truth": False,
        "note": "self-report used as supporting evidence, not a definitive fact",
    })
    frame.provenance.setdefault("self_report_refs", []).append(reports[0])


def interpret(appraisal: Optional[Appraisal], expectations: Optional[Expectations], person_state: Any, system_memory: Any = None) -> MeaningResult:
    """Deterministic, pure interpretation function.

    - Does not modify `person_state`.
    - Produces multiple MeaningFrames with confidence and derived_state_suggestions.
    """
    if appraisal is None or getattr(appraisal, "frames", None) is None or len(appraisal.frames) == 0:
        return MeaningResult(meaning_frames=[], insufficient_data=True)

    frames: List[MeaningFrame] = []

    goals = getattr(person_state, "goals", []) or []
    values = getattr(person_state, "values", []) or []
    history = getattr(person_state, "history", {}) or {}
    person_id = getattr(person_state, "person_id", getattr(person_state, "id", None))
    perceived_control = float(getattr(person_state, "perceived_control", 0.5) or 0.5)
    self_reports = _self_reports_for(person_state)

    memory_matches = []
    if system_memory is not None and hasattr(system_memory, "find_related_meanings"):
        try:
            tags = [f.label for f in appraisal.frames if getattr(f, "label", None)]
            current_dimensions = {}
            for af in appraisal.frames:
                try:
                    for key, value in (getattr(af, "dimension_scores", {}) or {}).items():
                        try:
                            current_dimensions[str(key)] = float(value)
                        except Exception:
                            current_dimensions[str(key)] = value
                except Exception:
                    continue
            memory_matches = system_memory.find_related_meanings(tags, person_id, time_window_seconds=None, limit=3, current_dimensions=current_dimensions) or []
        except TypeError:
            try:
                tags = [f.label for f in appraisal.frames if getattr(f, "label", None)]
                memory_matches = system_memory.find_related_meanings(tags, person_id, time_window_seconds=None, limit=3) or []
            except Exception:
                memory_matches = []
        except Exception:
            memory_matches = []

    exp_ids = []
    if expectations is not None and getattr(expectations, "predictions", None):
        for p in expectations.predictions:
            try:
                exp_ids.append(getattr(p, "outcome_label", None) or "")
            except Exception:
                pass

    for af in appraisal.frames:
        label = getattr(af, "label", "")
        dims = getattr(af, "dimension_scores", {}) or {}
        social_threat = _clamp01(dims.get("social_threat", 0.0))
        goal_relevance = _clamp01(dims.get("goal_relevance", 0.5))
        supporting_perceptions = getattr(af, "supporting_perceptions", []) or []

        if label == "threat" and social_threat >= 0.6:
            trauma_history = bool(history.get("money_trauma") or history.get("shame_events", 0) >= 2)
            achievement_signal = any(
                any(token in str(g).lower() for token in ("financial", "independ", "achievement", "status", "prove", "career"))
                for g in list(goals) + list(values)
            )
            opportunity_bias = bool(achievement_signal or history.get("previous_successes", 0) >= 1)
            hum_conf = _clamp01(0.65 * _clamp01(af.confidence) + 0.25 * (1.0 if trauma_history or perceived_control < 0.4 else 0.0))
            hum_relevance = _clamp01(max(goal_relevance, 0.5 if trauma_history else 0.2))
            hum = MeaningFrame(
                id=uid(),
                timestamp=now_iso(),
                interpretation="humiliation",
                interpretation_alternatives=[("humiliation", hum_conf), ("rejection", max(0.3, hum_conf - 0.2)), ("inadequacy", max(0.2, hum_conf - 0.3))],
                personal_relevance=hum_relevance,
                affected_values=["status", "esteem", "belonging"],
                activated_goals=[g for g in goals if g],
                motivation_direction="withdrawal",
                predicted_self_view_change="I am less worthy or less capable in front of others",
                confidence=hum_conf,
                supporting_appraisals=[getattr(af, "id", None)],
                supporting_expectations=exp_ids,
                supporting_memory_refs=[m.get("memory_id") for m in memory_matches] if memory_matches else [],
                evidence=[{"appraisal_dims": dims, "utterance_snippets": [e.value for e in getattr(af, "evidence", []) if hasattr(e, "value")] }, {"source": "self_report", "text": self_reports[0], "accepted_as_truth": False, "note": "supporting only"} if self_reports else {"appraisal_dims": dims}],
                persistence_hint=("sustained" if trauma_history or memory_matches else "transient"),
                derived_state_suggestions={"activate": ["embarrassment", "sadness"], "dims": {"embarrassment": 0.75, "sadness": 0.6}},
                uncertainty=1.0 - hum_conf,
                provenance={"perception_ids": supporting_perceptions, "appraisal_frame_ids": [getattr(af, "id", None)], "expectation_ids": exp_ids, "memory_refs": [m.get("memory_id") for m in memory_matches], "meaning_frame_id": None},
            )
            _add_self_report_evidence(hum, person_state)
            hum = _apply_memory_influence(hum, memory_matches)
            hum.provenance["meaning_frame_id"] = hum.id
            frames.append(hum)

            challenge_conf = _clamp01(0.55 * _clamp01(af.confidence) + 0.35 * (1.0 if achievement_signal else 0.0))
            challenge_relevance = _clamp01(max(goal_relevance, 0.6 if opportunity_bias else 0.35))
            chal = MeaningFrame(
                id=uid(),
                timestamp=now_iso(),
                interpretation="challenge",
                interpretation_alternatives=[("challenge", challenge_conf), ("opportunity", max(0.2, challenge_conf - 0.15)), ("need_to_prove_self", max(0.2, challenge_conf - 0.25))],
                personal_relevance=challenge_relevance,
                affected_values=["competence", "achievement", "self_respect"],
                activated_goals=[g for g in goals if g],
                motivation_direction="approach",
                predicted_self_view_change="I can improve and prove myself",
                confidence=challenge_conf,
                supporting_appraisals=[getattr(af, "id", None)],
                supporting_expectations=exp_ids,
                supporting_memory_refs=[m.get("memory_id") for m in memory_matches] if memory_matches else [],
                evidence=[{"appraisal_dims": dims}],
                persistence_hint="sustained" if opportunity_bias else "transient",
                derived_state_suggestions={"activate": ["motivation", "focus"], "dims": {"motivation": 0.7, "focus": 0.8}},
                uncertainty=1.0 - challenge_conf,
                provenance={"perception_ids": supporting_perceptions, "appraisal_frame_ids": [getattr(af, "id", None)], "expectation_ids": exp_ids, "memory_refs": [m.get("memory_id") for m in memory_matches], "meaning_frame_id": None},
            )
            _add_self_report_evidence(chal, person_state)
            chal = _apply_memory_influence(chal, memory_matches)
            chal.provenance["meaning_frame_id"] = chal.id
            frames.append(chal)

            if opportunity_bias:
                opp = MeaningFrame(
                    id=uid(),
                    timestamp=now_iso(),
                    interpretation="opportunity",
                    interpretation_alternatives=[("opportunity", max(0.3, challenge_conf - 0.2)), ("challenge", max(0.2, challenge_conf - 0.1))],
                    personal_relevance=_clamp01(challenge_relevance * 0.9),
                    affected_values=["achievement", "progress"],
                    activated_goals=[g for g in goals if g],
                    motivation_direction="approach",
                    predicted_self_view_change="This can become a path to improvement",
                    confidence=max(0.3, challenge_conf - 0.2),
                    supporting_appraisals=[getattr(af, "id", None)],
                    supporting_expectations=exp_ids,
                    supporting_memory_refs=[m.get("memory_id") for m in memory_matches] if memory_matches else [],
                    evidence=[{"appraisal_dims": dims}],
                    persistence_hint="transient",
                    derived_state_suggestions={"activate": ["motivation", "attention"], "dims": {"motivation": 0.6, "attention": 0.7}},
                    uncertainty=1.0 - max(0.3, challenge_conf - 0.2),
                    provenance={"perception_ids": supporting_perceptions, "appraisal_frame_ids": [getattr(af, "id", None)], "expectation_ids": exp_ids, "memory_refs": [m.get("memory_id") for m in memory_matches], "meaning_frame_id": None},
                )
                _add_self_report_evidence(opp, person_state)
                opp = _apply_memory_influence(opp, memory_matches)
                opp.provenance["meaning_frame_id"] = opp.id
                frames.append(opp)

            prove_conf = _clamp01(0.5 * challenge_conf + 0.25 * (1.0 if achievement_signal else 0.0))
            prove = MeaningFrame(
                id=uid(),
                timestamp=now_iso(),
                interpretation="need_to_prove_self",
                interpretation_alternatives=[("need_to_prove_self", prove_conf), ("challenge", max(0.2, prove_conf - 0.1))],
                personal_relevance=_clamp01(challenge_relevance * 0.8),
                affected_values=["competence", "identity"],
                activated_goals=[g for g in goals if g],
                motivation_direction="prove_self",
                predicted_self_view_change="I need to demonstrate my worth",
                confidence=prove_conf,
                supporting_appraisals=[getattr(af, "id", None)],
                supporting_expectations=exp_ids,
                supporting_memory_refs=[m.get("memory_id") for m in memory_matches] if memory_matches else [],
                evidence=[{"appraisal_dims": dims}],
                persistence_hint="transient",
                derived_state_suggestions={"activate": ["motivation", "focus"], "dims": {"motivation": 0.8, "focus": 0.7}},
                uncertainty=1.0 - prove_conf,
                provenance={"perception_ids": supporting_perceptions, "appraisal_frame_ids": [getattr(af, "id", None)], "expectation_ids": exp_ids, "memory_refs": [m.get("memory_id") for m in memory_matches], "meaning_frame_id": None},
            )
            _add_self_report_evidence(prove, person_state)
            prove = _apply_memory_influence(prove, memory_matches)
            prove.provenance["meaning_frame_id"] = prove.id
            frames.append(prove)

            if trauma_history or perceived_control < 0.4:
                inadequacy_conf = _clamp01(0.6 * hum_conf + 0.2 * (1.0 if trauma_history else 0.0))
                inadequacy = MeaningFrame(
                    id=uid(),
                    timestamp=now_iso(),
                    interpretation="inadequacy",
                    interpretation_alternatives=[("inadequacy", inadequacy_conf), ("humiliation", inadequacy_conf - 0.1)],
                    personal_relevance=_clamp01(hum_relevance * 1.1),
                    affected_values=["worth", "security"],
                    activated_goals=[],
                    motivation_direction="withdrawal",
                    predicted_self_view_change="I am not enough",
                    confidence=inadequacy_conf,
                    supporting_appraisals=[getattr(af, "id", None)],
                    supporting_expectations=exp_ids,
                    supporting_memory_refs=[m.get("memory_id") for m in memory_matches] if memory_matches else [],
                    evidence=[{"appraisal_dims": dims}],
                    persistence_hint="sustained" if trauma_history else "transient",
                    derived_state_suggestions={"activate": ["sadness", "embarrassment"], "dims": {"sadness": 0.75, "embarrassment": 0.8}},
                    uncertainty=1.0 - inadequacy_conf,
                    provenance={"perception_ids": supporting_perceptions, "appraisal_frame_ids": [getattr(af, "id", None)], "expectation_ids": exp_ids, "memory_refs": [m.get("memory_id") for m in memory_matches], "meaning_frame_id": None},
                )
                _add_self_report_evidence(inadequacy, person_state)
                inadequacy = _apply_memory_influence(inadequacy, memory_matches)
                inadequacy.provenance["meaning_frame_id"] = inadequacy.id
                frames.append(inadequacy)

                rej_conf = _clamp01(0.5 * hum_conf + 0.15 * (1.0 if not opportunity_bias else 0.0))
                rej = MeaningFrame(
                    id=uid(),
                    timestamp=now_iso(),
                    interpretation="rejection",
                    interpretation_alternatives=[("rejection", rej_conf), ("humiliation", rej_conf - 0.1)],
                    personal_relevance=_clamp01(hum_relevance * 0.8),
                    affected_values=["belonging", "respect"],
                    activated_goals=[],
                    motivation_direction="defense",
                    predicted_self_view_change="People do not value me",
                    confidence=rej_conf,
                    supporting_appraisals=[getattr(af, "id", None)],
                    supporting_expectations=exp_ids,
                    supporting_memory_refs=[m.get("memory_id") for m in memory_matches] if memory_matches else [],
                    evidence=[{"appraisal_dims": dims}],
                    persistence_hint="transient",
                    derived_state_suggestions={"activate": ["defensive", "anger"], "dims": {"defensive": 0.4, "anger": 0.5}},
                    uncertainty=1.0 - rej_conf,
                    provenance={"perception_ids": supporting_perceptions, "appraisal_frame_ids": [getattr(af, "id", None)], "expectation_ids": exp_ids, "memory_refs": [m.get("memory_id") for m in memory_matches], "meaning_frame_id": None},
                )
                _add_self_report_evidence(rej, person_state)
                rej = _apply_memory_influence(rej, memory_matches)
                rej.provenance["meaning_frame_id"] = rej.id
                frames.append(rej)

    if not frames:
        return MeaningResult(meaning_frames=[], insufficient_data=True)

    aggregate_relevance = sum(f.personal_relevance for f in frames) / max(1, len(frames))
    primary = max(frames, key=lambda x: x.confidence)

    return MeaningResult(meaning_frames=frames, aggregate_relevance=_clamp01(aggregate_relevance), primary_meaning=primary.interpretation, conflicts=[], insufficient_data=False)


def meaning_to_evidence(meaning_frame: MeaningFrame) -> List[StateEvidenceRecord]:
    """Convert a MeaningFrame into one or more StateManager-compatible EvidenceRecords.

    - Preserves MeaningFrame.id in `ref`.
    - Does not create StateInstances.
    """
    records: List[StateEvidenceRecord] = []
    ds = meaning_frame.derived_state_suggestions or {}
    activates = ds.get("activate", [])
    dims = ds.get("dims", {})
    for signal in activates:
        try:
            er = StateEvidenceRecord.create(
                source="meaning",
                signal=str(signal),
                value=dims or {signal: 0.5},
                confidence=_clamp01(meaning_frame.confidence),
                ref=meaning_frame.id,
            )
            records.append(er)
        except Exception:
            continue
    return records
