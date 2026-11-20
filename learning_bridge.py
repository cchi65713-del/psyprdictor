"""Minimal orchestration layer for execution -> outcome -> learning.

Phase 1 scope: centralize the existing manual learning flow without changing
habit-strength logic or personality modeling.

The bridge intentionally preserves the current semantics used by the project:
- set execution/outcome on PersonState
- record feedback if available
- update the pattern learner
- update habit strengths from memory using the existing algorithm
- optionally store an Experience record when a caller explicitly requests it

The bridge does not implement satisfaction-based habit weighting or personality
learning; those are intentionally deferred.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

from experience import Experience
from habit_formation import update_habit_strengths


class LearningBridge:
    """Minimal compatibility wrapper around the current learning pipeline.

    This Phase 1 component is intentionally conservative: it keeps the current
    behavior of the ad-hoc logic in `main.py` and `scenario_tester.py`, but moves
    it into a single API so the flow is easier to test and extend later.
    """

    @staticmethod
    def _as_path(value: Optional[Union[str, Sequence[str]]]) -> Optional[List[str]]:
        if value is None:
            return None
        if isinstance(value, str):
            return [part for part in value.split(".") if part]
        if isinstance(value, (list, tuple)):
            return [str(part) for part in value if part is not None and str(part).strip()]
        return [str(value)]

    @staticmethod
    def _build_feedback_record(
        person_id: Optional[str],
        chosen_action: Optional[str],
        actual_outcome: Optional[str],
        pattern_id: Optional[str],
        path: Optional[List[str]],
        context: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        if chosen_action is None and actual_outcome is None and pattern_id is None:
            return None
        return {
            "person_id": person_id,
            "action": chosen_action,
            "outcome": actual_outcome,
            "pattern_id": pattern_id,
            "path": path,
            "context": context,
            "timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    def _build_experience(
        pattern_path: Optional[List[str]],
        actual_outcome: Optional[str],
        context: Optional[str] = None,
        intensity: Optional[float] = None,
        timestamp: Optional[datetime] = None,
        efmsomb: Optional[dict] = None,
        **_: Any,
    ) -> Optional[Experience]:
        if actual_outcome is None:
            return None
        path = pattern_path
        if path is None:
            path = []
        if timestamp is None:
            timestamp = datetime.now()
        resolved_intensity = 5.0 if intensity is None else float(intensity)
        return Experience(
            path=path,
            intensity=resolved_intensity,
            context=context or "execution outcome",
            outcome=actual_outcome,
            timestamp=timestamp,
            efmsomb=efmsomb,
        )

    def record_execution(
        self,
        person_state: Any,
        person_id: Optional[str] = None,
        chosen_action: Optional[str] = None,
        actual_outcome: Optional[str] = None,
        pattern_id: Optional[str] = None,
        pattern_path: Optional[Union[str, Sequence[str]]] = None,
        context: Optional[str] = None,
        memory: Any = None,
        pattern_learner: Any = None,
        state_manager: Any = None,
        system_memory: Any = None,
        pattern_adaptation: Any = None,
        predicted_outcome: Optional[str] = None,
        store_experience: Optional[bool] = None,
        experience: Optional[Experience] = None,
        intensity: Optional[float] = None,
        feedback: Optional[Dict[str, Any]] = None,
        efmsomb: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """Centralize current execution->learning behavior.

        Default behavior preserves the exact legacy flow already present in the
        codebase: set execution/outcome on the person, update pattern learner,
        and then refresh habit strengths from memory using the existing algorithm.

        Optional `store_experience=True` adds a Memory.store(...) record without
        changing the core habit logic. This is intentionally conservative and not
        tied to any new satisfaction-based weighting.
        """
        normalized_path = self._as_path(pattern_path)
        if pattern_id is not None and normalized_path is None:
            normalized_path = self._as_path(pattern_id)

        if person_state is not None:
            if chosen_action is not None:
                person_state.execution = chosen_action
            if actual_outcome is not None:
                person_state.outcome = actual_outcome

        if feedback is None:
            feedback = self._build_feedback_record(
                person_id=person_id,
                chosen_action=chosen_action,
                actual_outcome=actual_outcome,
                pattern_id=pattern_id,
                path=normalized_path,
                context=context,
            )
        if feedback is not None and hasattr(person_state, "record_feedback"):
            person_state.record_feedback(feedback)

        if pattern_adaptation is not None and pattern_id is not None and predicted_outcome is not None and actual_outcome is not None:
            try:
                pattern_adaptation.update(pattern_id, predicted_outcome, actual_outcome)
            except Exception:
                pass

        if store_experience is None:
            store_experience = memory is not None

        if efmsomb is None and person_state is not None:
            efmsomb = getattr(person_state, "efmsomb", None)

        if memory is not None and actual_outcome is not None and store_experience:
            exp = experience if experience is not None else self._build_experience(
                pattern_path=normalized_path,
                actual_outcome=actual_outcome,
                context=context,
                intensity=intensity,
                efmsomb=efmsomb,
            )
            if exp is not None:
                memory.store(exp)

        # Preserve the legacy learning sequence exactly: pattern learner update
        # followed by habit-strength refresh. When a Memory is connected to a
        # PatternLearner, Memory.store(... ) already calls learner.learn(...), so
        # we avoid a duplicate write here unless the bridge is operating without
        # a memory instance.
        if pattern_learner is not None and actual_outcome is not None and memory is None:
            if normalized_path:
                try:
                    pattern_learner.record_feedback(normalized_path, actual_outcome)
                except Exception:
                    pass

        if memory is not None and person_state is not None:
            try:
                if pattern_id:
                    update_habit_strengths(person_state, memory, pattern_learner, pattern_id=pattern_id)
                elif normalized_path:
                    update_habit_strengths(person_state, memory, pattern_learner, pattern_id=".".join(normalized_path))
            except Exception:
                pass

        if state_manager is not None and system_memory is not None and person_id is not None:
            try:
                state_manager.export_memory_refs_to_system_memory(person_id, system_memory)
            except Exception:
                pass

        return {
            "person_id": person_id,
            "chosen_action": chosen_action,
            "outcome": actual_outcome,
            "pattern_id": pattern_id,
            "path": normalized_path,
            "memory_updated": memory is not None and actual_outcome is not None,
            "habit_strength_updated": bool(person_state is not None and getattr(person_state, "habit_strength", None)),
            "feedback": feedback,
        }
