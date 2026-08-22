"""
Decision Engine for PsyPredictor.

Integrates all behavioral subsystems into one cohesive decision pipeline:
PersonState → Proposals → BehavioralTendencies → SystemMemory → Competition → Arbitration → DecisionResult

This is the central orchestration point where all pieces come together.
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from action_selection import propose_goal_directed, propose_reactive, propose_habitual
from competition import CompetitionEngine, BehavioralTendency, CompetitionResult
from perception_appraisal_expectations import Appraiser, ExpectationsGenerator, Perceptor
from state_inference import StateInferenceEngine
from state_modulation import StateModulator
from state_manager import StateManager, EvidenceRecord

logger = logging.getLogger(__name__)


@dataclass
class DecisionResult:
    """
    Complete result of a single decision by the person's integrated system.
    
    Wraps CompetitionResult and adds any decision-specific metadata.
    """
    
    # Core decision
    selected_action: Optional[str] = None
    selected_source: str = ""
    
    # Strength metrics
    final_strength: float = 0.0
    decision_confidence: float = 0.0
    
    # Conflict information
    conflict_info: Dict = field(default_factory=dict)
    conflict_level: str = "none"
    conflict_type: str = ""
    
    # Confidence breakdown (transparent components)
    confidence_breakdown: Dict = field(default_factory=dict)
    
    # All proposals for inspection
    all_proposals: List[BehavioralTendency] = field(default_factory=list)
    
    # System memory influence on the decision
    system_memory_influence: Dict = field(default_factory=dict)
    
    # Human-readable reasoning
    reasoning: str = ""
    
    # Person context (for traceability)
    person_id: str = ""
    context: Optional[str] = ""

    # State of Mind inference and modulation metadata
    state_of_mind_source: str = "insufficient-data"
    state_of_mind_manual: Any = None
    state_of_mind_inferred: List[str] = field(default_factory=list)
    state_of_mind_primary: Optional[str] = None
    state_of_mind_evidence: List[Dict[str, Any]] = field(default_factory=list)
    state_of_mind_confidence: str = "unknown"
    state_of_mind_conflicts: List[str] = field(default_factory=list)
    state_of_mind_summary: str = ""
    state_of_mind_insufficient_data: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_competition_result(
        cls,
        competition_result: CompetitionResult,
        person_id: str = "",
        context: str = "",
        state_inference_result=None,
    ):
        """Factory method: create DecisionResult from CompetitionResult."""
        summary = ""
        source = "insufficient-data"
        manual_state = None
        inferred_states: List[str] = []
        primary_state = None
        evidence: List[Dict[str, Any]] = []
        confidence = "unknown"
        conflicts: List[str] = []
        insufficient_data: Dict[str, Any] = {}

        if state_inference_result is not None:
            source = getattr(state_inference_result, "source", "insufficient-data")
            manual_state = getattr(state_inference_result, "manual_state", None)
            inferred_states = list(getattr(state_inference_result, "inferred_states", []))
            primary_state = getattr(state_inference_result, "primary_state", None)
            evidence = list(getattr(state_inference_result, "evidence", []))
            confidence = getattr(state_inference_result, "confidence", "unknown")
            conflicts = list(getattr(state_inference_result, "conflicts", []))
            insufficient_data = getattr(state_inference_result, "insufficient_data", {})

            if source == "manual":
                summary = f"Manual State of Mind preserved: {manual_state}"
            elif source == "inferred":
                labels = ", ".join(inferred_states) if inferred_states else "unknown"
                primary = primary_state or "unknown"
                summary = f"State of Mind inferred: {labels}. Primary state: {primary}."
            else:
                summary = "State of Mind unavailable: insufficient information."

        reasoning = competition_result.reasoning
        if summary:
            reasoning = f"State of Mind: {summary} {reasoning}".strip()

        return cls(
            selected_action=competition_result.selected_action,
            selected_source=competition_result.selected_source,
            final_strength=competition_result.final_strength,
            decision_confidence=competition_result.decision_confidence,
            conflict_info=competition_result.conflict_info,
            conflict_level=competition_result.conflict_level,
            conflict_type=competition_result.conflict_type,
            confidence_breakdown=competition_result.confidence_breakdown,
            all_proposals=competition_result.all_proposals,
            system_memory_influence=competition_result.system_memory_influence,
            reasoning=reasoning,
            person_id=person_id,
            context=context,
            state_of_mind_source=source,
            state_of_mind_manual=manual_state,
            state_of_mind_inferred=inferred_states,
            state_of_mind_primary=primary_state,
            state_of_mind_evidence=evidence,
            state_of_mind_confidence=confidence,
            state_of_mind_conflicts=conflicts,
            state_of_mind_summary=summary,
            state_of_mind_insufficient_data=insufficient_data,
        )


class DecisionEngine:
    """
    Central orchestration for PsyPredictor behavioral decisions.
    
    Coordinates:
    - Action proposal from three subsystems (goal-directed, reactive, habitual)
    - SystemMemory influence on proposals
    - Competition between proposals
    - Final arbitration
    
    Returns a complete DecisionResult.
    """
    
    @staticmethod
    def _is_mal_enabled(enable_mal: Optional[bool] = None) -> bool:
        if enable_mal is not None:
            return bool(enable_mal)
        raw = os.getenv("PSYPREDICTOR_ENABLE_MAL", "0")
        normalized = str(raw).strip().lower()
        return normalized in {"1", "true", "yes", "on"}

    def __init__(self, system_memory=None, subsystem_weights: Optional[Dict[str, float]] = None, enable_mal: Optional[bool] = None):
        """
        Initialize the decision engine.
        
        Args:
            system_memory: Optional SystemMemory instance for contextual adjustment.
            subsystem_weights: Optional dict mapping subsystem name -> weight for competition.
            enable_mal: Optional explicit override for the MAL feature flag.
        """
        self.system_memory = system_memory
        self.enable_mal = self._is_mal_enabled(enable_mal)
        self.competition_engine = CompetitionEngine(
            subsystem_weights=subsystem_weights,
            system_memory=system_memory
        )
        self.state_inference_engine = StateInferenceEngine()
        self.state_modulator = StateModulator()
        # lightweight StateManager used as an additive state maintenance layer
        self.state_manager = StateManager()

    def _ingest_meaning_evidence(self, appraisal, expectations, person_state):
        """Attach MeaningFrames to person_state and route their evidence into StateManager.

        This is explicitly additive and non-decisional. MAL does not modify behavior
        outside the existing StateManager evidence pipeline.
        """
        if not self.enable_mal:
            return

        try:
            from meaning_interpretation import interpret, meaning_to_evidence

            meaning_result = interpret(appraisal, expectations, person_state, self.system_memory)
            meaning_frames = list(getattr(meaning_result, "meaning_frames", []) or [])
            if not meaning_frames:
                return

            if not hasattr(person_state, "meanings"):
                person_state.meanings = []
            existing_meanings = list(getattr(person_state, "meanings", []) or [])
            person_state.meanings = existing_meanings + meaning_frames

            for frame in meaning_frames:
                try:
                    frame_id = getattr(frame, "id", None)
                    if not frame_id:
                        continue
                    for evidence in meaning_to_evidence(frame):
                        evidence.ref = frame_id
                        self.state_manager.create_or_update_from_trigger(evidence)
                except Exception as exc:
                    logger.warning("MAL evidence ingestion error; continuing without MAL effect: %s", exc)
        except Exception as exc:
            logger.warning("Meaning Attribution Layer failed; continuing with the standard pipeline: %s", exc)
    
    def decide(
        self,
        person_state,
        person_id: str = "",
        current_context: Optional[str] = None,
        current_pattern_id: Optional[str] = None,
        pattern_learner=None
    ) -> DecisionResult:
        """
        Generate one complete behavioral decision from the current person state.
        
        Flow:
        1. Request proposals from goal-directed, reactive, and habitual systems.
        2. Collect BehavioralTendency objects from each.
        3. Apply SystemMemory adjustments to tendencies (if available).
        4. Run CompetitionEngine to resolve conflicts.
        5. Extract conflict and confidence information.
        6. Return complete DecisionResult.
        
        Args:
            person_state: PersonState object describing current internal/external state.
            person_id: ID for person (for traceability).
            current_context: Current situation/context string.
            current_pattern_id: ID of current behavioral pattern (if any).
            pattern_learner: Optional pattern learner instance for habitual proposals.
        
        Returns:
            DecisionResult with all decision metadata.
        """

        if person_state is None:
            return DecisionResult(
                selected_action=None,
                reasoning="No person state available to infer State of Mind.",
                person_id=person_id,
                context=current_context,
                state_of_mind_source="insufficient-data",
                state_of_mind_summary="State of Mind unavailable: insufficient information.",
            )

        # ============================================================
        # STEP 0: PERCEPTION -> APPRAISAL -> EXPECTATIONS
        # ============================================================

        trigger = getattr(person_state, "trigger", None)
        if trigger is None and current_context is not None:
            trigger = current_context
        perception = Perceptor.process(trigger, person_state)
        person_state.perception = perception

        appraisal = Appraiser.evaluate(perception, person_state)
        person_state.appraisal = appraisal

        expectations = ExpectationsGenerator.update(appraisal, person_state)
        person_state.expectations = expectations

        # attach manager to this person_state for in-place updates
        self.state_manager.person_state = person_state

        # ============================================================
        # STEP 0a: OPTIONAL MAL EVIDENCE INTEGRATION
        # This is additive and feature-flagged; it never selects actions.
        # ============================================================
        self._ingest_meaning_evidence(appraisal, expectations, person_state)

        # ============================================================
        # STEP 0b: UPDATE StateManager with Appraisal / Expectations / EFMSOMB
        # This is additive: it only updates `person_state.states` and preserves
        # the legacy `person_state.state_of_mind`. It must not choose actions.
        # ============================================================

        try:
            # push appraisal frames into StateManager
            if getattr(appraisal, "frames", None):
                for frame in appraisal.frames:
                    try:
                        er = EvidenceRecord.create(
                            source="appraisal",
                            signal=str(frame.label),
                            value=(getattr(frame, "dimension_scores", {}) or {}),
                            confidence=float(getattr(frame, "confidence", 0.0)),
                            ref=getattr(frame, "id", None),
                        )
                        self.state_manager.create_or_update_from_trigger(er)
                    except Exception:
                        # keep pipeline robust; don't break decision flow on evidence errors
                        pass

            # push expectation predictions into StateManager
            if getattr(expectations, "predictions", None):
                for pred in expectations.predictions:
                    try:
                        er = EvidenceRecord.create(
                            source="expectation",
                            signal=str(getattr(pred, "outcome_label", "")),
                            value={"probability": float(getattr(pred, "probability", 0.0))},
                            confidence=float(getattr(pred, "probability", 0.0)),
                            ref=getattr(pred, None),
                        )
                        self.state_manager.create_or_update_from_trigger(er)
                    except Exception:
                        pass

            # push EFMSOMB signals (emotion/feeling/mood + regulation) as light evidence
            efmsomb_dims = {}
            for key in ("emotion", "feeling", "mood", "arousal", "self_regulation", "awareness", "perceived_control"):
                val = getattr(person_state, key, None)
                if val is None:
                    continue
                efmsomb_dims[key] = val

            # Only push EFMSOMB snapshot evidence when it carries signal:
            # - explicit emotion/feeling/mood provided, OR
            # - numeric dimensions deviate meaningfully from neutral (0.5)
            significant = False
            for key in ("emotion", "feeling", "mood"):
                if key in efmsomb_dims:
                    significant = True
                    break
            if not significant:
                # check numeric deviations
                for key in ("arousal", "self_regulation", "awareness", "perceived_control"):
                    if key in efmsomb_dims:
                        try:
                            v = float(efmsomb_dims[key])
                            if abs(v - 0.5) >= 0.15:
                                significant = True
                                break
                        except Exception:
                            continue

            if significant:
                try:
                    er = EvidenceRecord.create(
                        source="efmsomb",
                        signal="efmsomb_snapshot",
                        value=efmsomb_dims,
                        confidence=1.0,
                    )
                    self.state_manager.create_or_update_from_trigger(er)
                except Exception:
                    pass
        except Exception:
            # If StateManager is not available or some unexpected error occurs,
            # do not stop decision processing.
            pass

        # Optional bridge: export any reinforced memory refs into SystemMemory
        try:
            if self.system_memory and person_id:
                try:
                    exported = self.state_manager.export_memory_refs_to_system_memory(person_id, self.system_memory)
                    if exported:
                        logger.debug("Exported %d reinforced memory refs for person %s", exported, person_id)
                except Exception as exc:
                    # log export errors but keep pipeline robust
                    logger.exception("Failed exporting reinforced memory refs for person %s: %s", person_id, exc)
        except Exception as exc:
            logger.exception("Unexpected error in memory export bridge for person %s: %s", person_id, exc)

        # ============================================================
        # STEP 1: INFER CURRENT STATE OF MIND WITHOUT CHOOSING AN ACTION
        # ============================================================

        state_inference_result = self.state_inference_engine.infer(person_state)

        if state_inference_result.source == "manual":
            modulated_state = getattr(person_state, "state_of_mind", {}) or {}
        elif state_inference_result.inferred_states:
            modulated_state = {state: True for state in state_inference_result.inferred_states}
        else:
            modulated_state = {}

        if not isinstance(modulated_state, dict):
            modulated_state = {}

        try:
            import copy
            state_context = copy.copy(person_state)
            state_context.state_of_mind = modulated_state
        except Exception:
            state_context = person_state
        
        # ============================================================
        # STEP 1: COLLECT PROPOSALS FROM SUBSYSTEMS
        # ============================================================
        
        gd_result = propose_goal_directed(person_state, current_context, current_pattern_id)
        re_result = propose_reactive(person_state)
        ha_result = propose_habitual(person_state, current_pattern_id, pattern_learner)
        
        # Extract BehavioralTendency objects from ProposalResult wrappers
        gd_tendencies = gd_result.tendencies
        re_tendencies = re_result.tendencies
        ha_tendencies = ha_result.tendencies
        
        # Combine all tendencies
        all_tendencies = gd_tendencies + re_tendencies + ha_tendencies
        
        if not all_tendencies:
            # Fallback: no proposals generated
            return DecisionResult(
                selected_action=None,
                reasoning="No behavioral tendencies were generated by any subsystem.",
                person_id=person_id,
                context=current_context,
                state_of_mind_source=state_inference_result.source,
                state_of_mind_manual=getattr(state_inference_result, "manual_state", None),
                state_of_mind_inferred=list(getattr(state_inference_result, "inferred_states", [])),
                state_of_mind_primary=getattr(state_inference_result, "primary_state", None),
                state_of_mind_evidence=list(getattr(state_inference_result, "evidence", [])),
                state_of_mind_confidence=getattr(state_inference_result, "confidence", "unknown"),
                state_of_mind_conflicts=list(getattr(state_inference_result, "conflicts", [])),
                state_of_mind_summary="State of Mind unavailable: insufficient information." if not getattr(state_inference_result, "inferred_states", []) else f"State of Mind inferred: {', '.join(state_inference_result.inferred_states)}",
                state_of_mind_insufficient_data=getattr(state_inference_result, "insufficient_data", {}),
            )

        # ============================================================
        # STEP 2: APPLY STATE MODULATION TO EACH TENDENCY
        # ============================================================

        for tendency in all_tendencies:
            self.state_modulator.modulate(tendency, state_context)
        
        # ============================================================
        # STEP 3: APPLY SYSTEM MEMORY ADJUSTMENTS
        # ============================================================
        
        # SystemMemory is already applied during CompetitionEngine.compete(),
        # but we can log the adjustments for transparency.
        system_memory_summary = {}
        if self.system_memory and person_id:
            for t in all_tendencies:
                try:
                    factor, reasons = self.system_memory.assess_tendency(person_id, t)
                    if reasons:
                        system_memory_summary[t.action] = {
                            "factor": factor,
                            "reasons": reasons
                        }
                except Exception:
                    pass
        
        # ============================================================
        # STEP 4: RUN COMPETITION
        # ============================================================
        
        competition_result = self.competition_engine.compete(all_tendencies, person=person_id)
        
        # ============================================================
        # STEP 5: BUILD DECISION RESULT
        # ============================================================
        
        decision = DecisionResult.from_competition_result(
            competition_result,
            person_id=person_id,
            context=current_context,
            state_inference_result=state_inference_result,
        )
        
        # Enrich with system memory summary
        decision.system_memory_influence = system_memory_summary
        
        return decision


def make_decision(
    person_state,
    person_id: str = "",
    system_memory=None,
    current_context: Optional[str] = None,
    current_pattern_id: Optional[str] = None,
    pattern_learner=None,
    subsystem_weights: Optional[Dict[str, float]] = None,
    enable_mal: Optional[bool] = None,
) -> DecisionResult:
    """
    Convenience function: create a decision engine and make one decision.
    
    Use this for one-off decisions or when you don't need to reuse the engine.
    For repeated decisions with the same person, instantiate DecisionEngine once
    and call .decide() multiple times.
    """
    engine = DecisionEngine(system_memory=system_memory, subsystem_weights=subsystem_weights, enable_mal=enable_mal)
    return engine.decide(
        person_state,
        person_id=person_id,
        current_context=current_context,
        current_pattern_id=current_pattern_id,
        pattern_learner=pattern_learner
    )
