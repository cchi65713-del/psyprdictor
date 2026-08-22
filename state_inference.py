"""State inference for PsyPredictor.

This module estimates State of Mind from the current PersonState without
changing the decision pipeline or competition logic.

It is intentionally conservative and explicit: it only reads existing fields,
records evidence for every inference, and does not perform action selection.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class StateInferenceResult:
    """Explanation-friendly result of inferring a person's current state."""

    manual_state: Any = None
    inferred_states: List[str] = field(default_factory=list)
    primary_state: Optional[str] = None
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    source: str = "insufficient-data"
    confidence: str = "unknown"
    conflicts: List[str] = field(default_factory=list)
    insufficient_data: Dict[str, Any] = field(default_factory=dict)

    # This explicit field makes the contract clear: StateInferenceEngine never
    # chooses an action. It only infers internal state.
    selected_action: Optional[str] = None


class StateInferenceEngine:
    """Infers current State of Mind from available PersonState information.

    This module is deliberately simple and transparent. It does not modify the
    PersonState object and does not influence competition or action selection.
    """

    STATE_PRIORITY = [
        "threatened",
        "defensive",
        "overwhelmed",
        "confused",
        "calm",
        "confident",
    ]

    def _normalize_manual_state(self, value):
        if value in (None, {}, [], ""):
            return []

        if isinstance(value, str):
            return [value.strip().lower()]

        if isinstance(value, dict):
            return [
                str(key).strip().lower()
                for key, active in value.items()
                if active is not False
            ]

        if isinstance(value, list):
            normalized = []
            for item in value:
                normalized.extend(self._normalize_manual_state(item))
            return normalized

        return []

    def _safe_lower(self, value):
        if value is None:
            return ""
        return str(value).strip().lower()

    def _extract_state_from_dict(self, person_state):
        state_of_mind = getattr(person_state, "state_of_mind", None)
        if not isinstance(state_of_mind, dict):
            return []

        return [
            str(key).strip().lower()
            for key, active in state_of_mind.items()
            if active is not False
        ]

    def _extract_appraisal_frames(self, person_state):
        appraisal = getattr(person_state, "appraisal", None)
        if appraisal is None:
            return []
        if hasattr(appraisal, "frames"):
            return list(getattr(appraisal, "frames", []) or [])
        if isinstance(appraisal, dict):
            return list(appraisal.get("frames", []) or [])
        return []

    def _extract_expectation_predictions(self, person_state):
        expectations = getattr(person_state, "expectations", None)
        if expectations is None:
            return []
        if hasattr(expectations, "predictions"):
            return list(getattr(expectations, "predictions", []) or [])
        if isinstance(expectations, dict):
            return list(expectations.get("predictions", []) or [])
        return []

    def _record_evidence(self, states, reason, person_state, source="efmsomb", appraisal_labels=None, expectation_labels=None, efmsomb_fields=None):
        payload = {
            "states": states,
            "reason": reason,
            "source": source,
            "appraisal_labels": list(appraisal_labels or []),
            "expectation_labels": list(expectation_labels or []),
            "efmsomb_fields": list(efmsomb_fields or []),
            "context": {
                "emotion": getattr(person_state, "emotion", None),
                "feeling": getattr(person_state, "feeling", None),
                "mood": getattr(person_state, "mood", None),
                "arousal": getattr(person_state, "arousal", None),
                "self_regulation": getattr(person_state, "self_regulation", None),
                "awareness": getattr(person_state, "awareness", None),
                "context": getattr(person_state, "context", None),
                "environment": getattr(person_state, "environment", None),
                "goals": getattr(person_state, "goals", None),
                "needs": getattr(person_state, "needs", None),
                "values": getattr(person_state, "values", None),
            },
        }
        return payload

    def _infer_from_rules(self, person_state):
        """Infer states from explicit, minimal field checks.

        No formulas, no action choice, and no competition-derived evidence.
        """
        evidence = []
        inferred = []

        emotion = self._safe_lower(getattr(person_state, "emotion", None))
        feeling = self._safe_lower(getattr(person_state, "feeling", None))
        mood = self._safe_lower(getattr(person_state, "mood", None))
        arousal = getattr(person_state, "arousal", 0.0)
        self_regulation = getattr(person_state, "self_regulation", 0.5)
        awareness = getattr(person_state, "awareness", 0.5)
        context = self._safe_lower(getattr(person_state, "context", None))
        environment = getattr(person_state, "environment", None)
        goals = getattr(person_state, "goals", None) or {}
        needs = getattr(person_state, "needs", None) or {}
        values = getattr(person_state, "values", None) or []
        appraisal_frames = self._extract_appraisal_frames(person_state)
        expectation_predictions = self._extract_expectation_predictions(person_state)

        # Rule 1: high arousal + low regulation + defensive context -> threatened/defensive
        if arousal is not None and arousal > 0.7 and self_regulation < 0.4:
            for state in ("threatened", "defensive"):
                if state not in inferred:
                    inferred.append(state)
                    evidence.append(
                        self._record_evidence(
                            [state],
                            "high arousal and low self-regulation indicate a threatened/defensive state.",
                            person_state,
                        )
                    )

        # Rule 2: explicit fear/anger/fight context indicate threatened/defensive
        if any(token in (emotion, feeling, mood) for token in ("anger", "fear", "anxious", "threatened")):
            if "threatened" not in inferred:
                inferred.append("threatened")
                evidence.append(
                    self._record_evidence(
                        ["threatened"],
                        "emotion/feeling/mood contains threat-like language.",
                        person_state,
                    )
                )

        # Rule 3: defensive or avoidant goals or context suggest defensive mode
        goal_text = " ".join(str(item).lower() for item in (goals if isinstance(goals, list) else [goals]))
        if "defend" in goal_text or "avoid" in goal_text or "protect" in goal_text:
            if "defensive" not in inferred:
                inferred.append("defensive")
                evidence.append(
                    self._record_evidence(
                        ["defensive"],
                        "goals indicate defense or protection.",
                        person_state,
                    )
                )

        # Rule 4: calm mood + strong regulation -> calm
        if mood == "calm" and self_regulation >= 0.7:
            if "calm" not in inferred:
                inferred.append("calm")
                evidence.append(
                    self._record_evidence(
                        ["calm"],
                        "calm mood and strong self-regulation indicate a calm state.",
                        person_state,
                    )
                )

        # Rule 5: low awareness + uncertainty-like mood or feeling -> confused
        if any(token in (emotion, feeling, mood) for token in ("confused", "uncertain", "unset", "lost")) or awareness <= 0.3:
            if "confused" not in inferred:
                inferred.append("confused")
                evidence.append(
                    self._record_evidence(
                        ["confused"],
                        "uncertain affect or low awareness indicates confusion.",
                        person_state,
                    )
                )

        # Rule 6: low awareness + high arousal + no regulation -> overwhelmed
        if awareness <= 0.3 and arousal > 0.7 and self_regulation <= 0.5:
            if "overwhelmed" not in inferred:
                inferred.append("overwhelmed")
                evidence.append(
                    self._record_evidence(
                        ["overwhelmed"],
                        "high arousal with low awareness and weak regulation suggest overwhelm.",
                        person_state,
                    )
                )

        # Rule 7: calm and confident/in-control context -> confident
        perceived_control = getattr(person_state, "perceived_control", 0.5)
        if self_regulation >= 0.7 and perceived_control >= 0.7:
            if "calm" in inferred and "confident" not in inferred:
                inferred.append("confident")
                evidence.append(
                    self._record_evidence(
                        ["confident"],
                        "high control and strong regulation indicate confident state.",
                        person_state,
                    )
                )

        threat_frames = [frame for frame in appraisal_frames if getattr(frame, "label", None) == "threat"]
        if threat_frames:
            threat_labels = [getattr(frame, "label", None) for frame in threat_frames if getattr(frame, "label", None)]
            if "threatened" not in inferred:
                inferred.append("threatened")
            evidence.append(
                self._record_evidence(
                    ["threatened"],
                    "threat appraisal frames suggest the person interprets the situation as threatening.",
                    person_state,
                    source="appraisal",
                    appraisal_labels=threat_labels,
                    efmsomb_fields=[field for field in ("arousal", "self_regulation", "awareness") if getattr(person_state, field, None) is not None],
                )
            )
            if self_regulation < 0.4 and "defensive" not in inferred:
                inferred.append("defensive")
                evidence.append(
                    self._record_evidence(
                        ["defensive"],
                        "threat appraisal combined with low self-regulation supports defensive activation.",
                        person_state,
                        source="appraisal",
                        appraisal_labels=threat_labels,
                        efmsomb_fields=["self_regulation", "arousal"],
                    )
                )

        ambiguity_frames = [frame for frame in appraisal_frames if getattr(frame, "label", None) == "ambiguity"]
        if ambiguity_frames:
            ambiguity_labels = [getattr(frame, "label", None) for frame in ambiguity_frames if getattr(frame, "label", None)]
            if "confused" not in inferred:
                inferred.append("confused")
            evidence.append(
                self._record_evidence(
                    ["confused"],
                    "ambiguity appraisal frames imply mixed or uncertain interpretation of the situation.",
                    person_state,
                    source="appraisal",
                    appraisal_labels=ambiguity_labels,
                    efmsomb_fields=[field for field in ("awareness", "arousal", "self_regulation") if getattr(person_state, field, None) is not None],
                )
            )

        opportunity_frames = [frame for frame in appraisal_frames if getattr(frame, "label", None) == "opportunity"]
        if opportunity_frames:
            opportunity_labels = [getattr(frame, "label", None) for frame in opportunity_frames if getattr(frame, "label", None)]
            if "confident" not in inferred and self_regulation >= 0.5:
                inferred.append("confident")
            if "calm" not in inferred and self_regulation >= 0.7:
                inferred.append("calm")
            if "confident" in inferred or "calm" in inferred:
                evidence.append(
                    self._record_evidence(
                        [state for state in ("confident", "calm") if state in inferred],
                        "opportunity appraisal frames suggest promising or actionable interpretation.",
                        person_state,
                        source="appraisal",
                        appraisal_labels=opportunity_labels,
                        efmsomb_fields=[field for field in ("awareness", "self_regulation", "mood") if getattr(person_state, field, None) is not None],
                    )
                )

        confrontation_predictions = [
            prediction for prediction in expectation_predictions
            if getattr(prediction, "outcome_label", "").lower() in {"confrontation", "attack", "threat", "retaliation"}
        ]
        if confrontation_predictions:
            highest_prob = max((float(getattr(prediction, "probability", 0.0)) for prediction in confrontation_predictions), default=0.0)
            if highest_prob >= 0.5 and "threatened" not in inferred:
                inferred.append("threatened")
            if highest_prob >= 0.5:
                evidence.append(
                    self._record_evidence(
                        ["threatened"],
                        "high confrontation expectations indicate anticipated threat or conflict.",
                        person_state,
                        source="expectation",
                        expectation_labels=[getattr(prediction, "outcome_label", None) for prediction in confrontation_predictions],
                        efmsomb_fields=[field for field in ("arousal", "self_regulation", "mood") if getattr(person_state, field, None) is not None],
                    )
                )

        competing_predictions = [prediction for prediction in expectation_predictions if getattr(prediction, "outcome_label", None)]
        if len(competing_predictions) > 1:
            probabilities = [float(getattr(prediction, "probability", 0.0)) for prediction in competing_predictions]
            if max(probabilities) - min(probabilities) <= 0.4 and "confused" not in inferred:
                inferred.append("confused")
                evidence.append(
                    self._record_evidence(
                        ["confused"],
                        "multiple competing expectations indicate uncertainty and reduced certainty.",
                        person_state,
                        source="expectation",
                        expectation_labels=[getattr(prediction, "outcome_label", None) for prediction in competing_predictions],
                        efmsomb_fields=["awareness", "mood", "self_regulation"],
                    )
                )

        positive_predictions = [
            prediction for prediction in expectation_predictions
            if getattr(prediction, "outcome_label", "").lower() in {"cooperation", "acceptance", "support", "help", "engagement", "collaboration"}
        ]
        if positive_predictions:
            highest_prob = max((float(getattr(prediction, "probability", 0.0)) for prediction in positive_predictions), default=0.0)
            if highest_prob >= 0.5 and "confident" not in inferred:
                inferred.append("confident")
                evidence.append(
                    self._record_evidence(
                        ["confident"],
                        "positive expectations suggest confident, cooperative interpretation of the situation.",
                        person_state,
                        source="expectation",
                        expectation_labels=[getattr(prediction, "outcome_label", None) for prediction in positive_predictions],
                        efmsomb_fields=["awareness", "self_regulation", "mood"],
                    )
                )

        # If no explicit rule fired, insufficient data.
        if not inferred:
            return inferred, evidence, True

        return inferred, evidence, False

    def _decide_primary_state(self, inferred_states):
        if not inferred_states:
            return None

        if len(inferred_states) == 1:
            return inferred_states[0]

        for state in self.STATE_PRIORITY:
            if state in inferred_states:
                return state

        return inferred_states[0]

    def _evaluate_conflict(self, manual_state, inferred_states):
        conflicts = []
        manual_labels = self._normalize_manual_state(manual_state)

        if manual_labels and inferred_states:
            for label in manual_labels:
                if label not in inferred_states and label in self.STATE_PRIORITY:
                    conflicts.append(
                        f"manual state {label!r} conflicts with inferred state(s) {inferred_states!r}"
                    )

        if len(inferred_states) > 1:
            # different active states are allowed, but describe them as plural rather than silent resolution
            states_text = ", ".join(sorted(set(inferred_states)))
            conflicts.append(f"multiple active states detected: {states_text}")

        return conflicts

    def infer(self, person_state):
        """Estimate State of Mind from PersonState without affecting other systems."""
        if person_state is None:
            return StateInferenceResult(
                manual_state=None,
                inferred_states=[],
                source="insufficient-data",
                confidence="unknown",
                insufficient_data={"reason": "No PersonState was provided."},
            )

        manual_state = getattr(person_state, "state_of_mind", None)
        manual_labels = self._normalize_manual_state(manual_state)

        # Preserve existing manual state. Do not write into PersonState.
        if manual_labels:
            result = StateInferenceResult(
                manual_state=manual_state,
                inferred_states=[],
                primary_state=None,
                evidence=[],
                source="manual",
                confidence="high" if len(manual_labels) == 1 else "medium",
                conflicts=[],
                insufficient_data={"reason": "manual state preserved; inference not required"},
            )
            return result

        # If a StateManager has populated `person_state.states`, prefer those
        # active StateInstances as the basis for inference. This keeps StateInference
        # aligned with the runtime StateManager while preserving manual overrides.
        try:
            states_container = getattr(person_state, "states", None)
            if states_container:
                active_states = states_container.get("active", []) or []
                if active_states:
                    inferred_from_states = []
                    evidence = []
                    for s in active_states:
                        # canonical_name is the primary semantic label for the instance
                        if getattr(s, "canonical_name", None):
                            inferred_from_states.append(str(s.canonical_name))
                        # collect evidence provenance from the StateInstance
                        try:
                            for ev in getattr(s, "evidence", []) or []:
                                evidence.append({
                                    "source": getattr(ev, "source", None),
                                    "signal": getattr(ev, "signal", None),
                                    "value": getattr(ev, "value", None),
                                    "timestamp": getattr(ev, "timestamp", None),
                                    "ref": getattr(ev, "ref", None),
                                })
                        except Exception:
                            pass

                    if inferred_from_states:
                        primary = inferred_from_states[0] if inferred_from_states else None
                        result = StateInferenceResult(
                            manual_state=None,
                            inferred_states=inferred_from_states,
                            primary_state=primary,
                            evidence=evidence,
                            source="inferred-via-states",
                            confidence="medium" if len(inferred_from_states) > 1 else "high",
                            conflicts=[],
                            insufficient_data={},
                        )
                        return result
        except Exception:
            # fall back to rule-based inference on any error
            pass

        inferred_states, evidence, insufficient = self._infer_from_rules(person_state)
        conflicts = []
        if inferred_states:
            primary_state = self._decide_primary_state(inferred_states)
            source = "inferred"
            confidence = "high" if len(inferred_states) == 1 else "medium"
        else:
            primary_state = None
            source = "insufficient-data"
            confidence = "unknown"
            evidence = []

        if insufficient and not inferred_states:
            conflicts = []
            insufficient_data = {
                "reason": "insufficient information to determine a clear state",
                "available_signals": {
                    "emotion": getattr(person_state, "emotion", None),
                    "feeling": getattr(person_state, "feeling", None),
                    "mood": getattr(person_state, "mood", None),
                    "arousal": getattr(person_state, "arousal", None),
                    "self_regulation": getattr(person_state, "self_regulation", None),
                    "awareness": getattr(person_state, "awareness", None),
                    "context": getattr(person_state, "context", None),
                },
            }
        else:
            insufficient_data = {}
            conflicts = self._evaluate_conflict(manual_state, inferred_states)

        return StateInferenceResult(
            manual_state=manual_state,
            inferred_states=inferred_states,
            primary_state=primary_state,
            evidence=evidence,
            source=source,
            confidence=confidence,
            conflicts=conflicts,
            insufficient_data=insufficient_data,
            selected_action=None,
        )
