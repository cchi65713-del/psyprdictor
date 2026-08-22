"""
Minimal StateManager implementation matching STATE_OF_MIND_API.md (first-pass).
This module implements dataclasses and deterministic update functions.
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
import uuid
import math
import logging


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def uid() -> str:
    return str(uuid.uuid4())


@dataclass
class EvidenceRecord:
    id: str
    source: str
    signal: str
    value: Any
    confidence: float
    timestamp: str
    ref: Optional[str] = None

    @staticmethod
    def create(source: str, signal: str, value: Any, confidence: float = 1.0, ref: Optional[str] = None):
        return EvidenceRecord(id=uid(), source=source, signal=signal, value=value, confidence=confidence, timestamp=now_iso(), ref=ref)


@dataclass
class StateInstance:
    id: str
    canonical_name: Optional[str]
    dimensions: Dict[str, float]
    intensity: float = 0.0
    confidence: float = 0.0
    onset: str = field(default_factory=now_iso)
    first_onset: str = field(default_factory=now_iso)
    last_update: str = field(default_factory=now_iso)
    duration_seconds: float = 0.0
    decay_rate: float = 0.0001
    recurrence_count: int = 1
    persistence_tag: str = "brief"
    triggers: List[str] = field(default_factory=list)
    origin: Dict[str, Any] = field(default_factory=dict)
    maintaining_factors: List[str] = field(default_factory=list)
    influenced_by: List[str] = field(default_factory=list)
    influences: List[str] = field(default_factory=list)
    reinforced: bool = False
    manual: bool = False
    manual_reason: Optional[str] = None
    evidence: List[EvidenceRecord] = field(default_factory=list)
    conflict_info: Optional[Dict[str, Any]] = None

    def recompute_intensity(self):
        if not self.dimensions:
            self.intensity = 0.0
            return
        vals = [max(0.0, min(1.0, float(v))) for v in self.dimensions.values()]
        self.intensity = sum(vals) / len(vals)

    def touch(self):
        self.last_update = now_iso()


class StateManager:
    def __init__(self, person_state=None):
        self.person_state = person_state
        # simple baseline default
        self.default_baseline = {"attention": 0.5, "motivation": 0.2, "arousal": 0.3}
        self.REINFORCE_THRESHOLD = 3
        self.REINFORCE_WINDOW_SECONDS = 86400
        self.MIN_ACTIVE_INTENSITY = 0.10
        self.logger = logging.getLogger(__name__)

    # ------------------ creation & update ------------------
    def create_state_from_trigger(self, name: Optional[str], evidence: EvidenceRecord, initial_dims: Dict[str, float] = None) -> StateInstance:
        dims = dict(initial_dims or {})
        s = StateInstance(id=uid(), canonical_name=name, dimensions=dims)
        s.evidence.append(evidence)
        s.triggers.append(evidence.id)
        s.origin = {"cause_type": evidence.source, "cause_ref": evidence.ref, "cause_timestamp": evidence.timestamp}
        s.recurrence_count = 1
        s.recompute_intensity()
        s.touch()
        # add to person_state.states if available
        if self.person_state is not None:
            self.person_state.states["active"].append(s)
        return s

    def update_state_with_evidence(self, state: StateInstance, evidence: EvidenceRecord) -> StateInstance:
        state.evidence.append(evidence)
        state.triggers.append(evidence.id)
        # merge evidence value if structured dims provided
        if isinstance(evidence.value, dict):
            for k, v in evidence.value.items():
                old = state.dimensions.get(k, 0.0)
                # simple smoothing
                state.dimensions[k] = max(0.0, min(1.0, (old + float(v)) / 2.0))
        # update counts and timestamps
        state.recurrence_count += 1
        state.touch()
        state.recompute_intensity()
        return state

    def merge_compatible_evidence(self, states: List[StateInstance], new_evidence: EvidenceRecord, threshold: float = 0.2) -> List[StateInstance]:
        attached = []
        # if evidence.value is dims, find overlap
        if isinstance(new_evidence.value, dict):
            for s in states:
                score = self._overlap_score(s.dimensions, new_evidence.value)
                if score >= threshold:
                    self.update_state_with_evidence(s, new_evidence)
                    attached.append(s)
        return attached

    def create_or_update_from_trigger(self, evidence: EvidenceRecord) -> Tuple[List[StateInstance], List[StateInstance]]:
        created = []
        updated = []
        # attempt to attach to existing active states
        active = []
        if self.person_state is not None:
            active = self.person_state.states.get("active", [])
        attached = self.merge_compatible_evidence(active, evidence)
        if attached:
            updated.extend(attached)
            return created, updated
        # otherwise create new state named after signal
        new_state = self.create_state_from_trigger(evidence.signal, evidence, initial_dims=(evidence.value if isinstance(evidence.value, dict) else {}))
        created.append(new_state)
        return created, updated

    # ------------------ persistence & decay ------------------
    def evaluate_persistence(self, state: StateInstance, person_id: Optional[str] = None, system_memory=None):
        # Determine persistence and mark reinforcement when recurrence passes threshold.
        if state.recurrence_count >= self.REINFORCE_THRESHOLD:
            state.reinforced = True
            state.decay_rate = max(state.decay_rate * 0.5, 1e-6)
            # Emit a memory ref into person_state if available (backwards-compatible)
            try:
                # Use existing helper to append a minimal memory reference; do not remove or alter refs
                self.reinforce_state_to_memory(state)
            except Exception:
                # Keep pipeline robust; do not propagate memory export failures
                pass
        # update persistence_tag
        duration = self._duration_seconds(state)
        if duration < 600:
            state.persistence_tag = "brief"
        elif duration < 604800:
            state.persistence_tag = "sustained"
        else:
            state.persistence_tag = "persistent"
        return state

    def export_memory_refs_to_system_memory(self, person_id: str, system_memory) -> int:
        """
        Export reinforced memory references from `person_state.memory_refs` into `system_memory`.

        - Only exports refs that explicitly indicate reinforcement (`reinforced` key truthy).
        - Uses existing `system_memory` API (e.g., `add_history`) and does not modify refs.
        - Returns number of exported refs.
        """
        if system_memory is None or person_id is None:
            return 0

        exported = 0
        try:
            refs = getattr(self.person_state, "memory_refs", []) or []
        except Exception as exc:
            # log and continue with empty refs
            self.logger.exception("Failed to read person_state.memory_refs for %s: %s", person_id, exc)
            refs = []

        for ref in refs:
            try:
                if not isinstance(ref, dict):
                    continue
                # only export explicitly reinforced refs
                if not ref.get("reinforced"):
                    continue
                # create a compact event for SystemMemory; preserve original ref under "memory_ref"
                event = {
                    "type": "state_learning",
                    "memory_ref": ref,
                }
                # enrich event with a stable memory_id (prefer state_id) and canonical_name if available
                mem_id = ref.get("state_id") or ref.get("memory_id")
                if mem_id:
                    event["memory_id"] = mem_id
                # attempt to find a matching StateInstance to attach canonical_name/dimensions
                name = None
                try:
                    if getattr(self, "person_state", None) is not None:
                        states = list(self.person_state.states.get("active", []) or []) + list(self.person_state.states.get("recent", []) or [])
                        for s in states:
                            if getattr(s, "id", None) == mem_id:
                                name = getattr(s, "canonical_name", None)
                                dims = getattr(s, "dimensions", None) or {}
                                # keep only a small snapshot of dims
                                try:
                                    event["dimensions"] = {k: dims[k] for k in list(dims.keys())[:5]}
                                except Exception:
                                    pass
                                break
                except Exception:
                    name = None
                if name:
                    event["canonical_name"] = name
                # Prefer existing add_history API
                if hasattr(system_memory, "add_history"):
                    try:
                        system_memory.add_history(person_id, event)
                        exported += 1
                    except Exception as exc:
                        # log but remain failure-safe
                        self.logger.exception("Failed to add_history for person %s event %s: %s", person_id, event, exc)
                        continue
                else:
                    # fall back to naive insertion if structure is different
                    try:
                        system_memory.history.setdefault(person_id, []).append(event)
                        exported += 1
                    except Exception as exc:
                        self.logger.exception("Failed to append to system_memory.history for %s: %s", person_id, exc)
                        continue
            except Exception:
                # log unexpected per-ref errors and continue
                try:
                    self.logger.exception("Unexpected error exporting ref for person %s: %s", person_id, ref)
                except Exception:
                    pass
                continue

        return exported

    def decay_step(self, state: StateInstance, elapsed_seconds: float):
        # exponential decay on dimensions
        factor = math.exp(-state.decay_rate * elapsed_seconds)
        for k, v in list(state.dimensions.items()):
            state.dimensions[k] = max(0.0, min(1.0, v * factor))
        state.recompute_intensity()
        state.duration_seconds = self._duration_seconds(state)
        state.touch()
        # move to recent if below threshold
        if state.intensity < self.MIN_ACTIVE_INTENSITY and self.person_state is not None:
            if state in self.person_state.states.get("active", []):
                self.person_state.states["active"].remove(state)
                self.person_state.states["recent"].append(state)
        return state

    def return_toward_baseline(self, state: StateInstance, baseline: Optional[Dict[str, float]] = None, elapsed_seconds: float = 1.0):
        base = baseline or (self.person_state.states.get("baseline", {}).get("dimensions") if self.person_state else None) or self.default_baseline
        # proportional move toward baseline
        alpha = min(1.0, elapsed_seconds / 60.0) * 0.1
        for k, bv in base.items():
            sv = state.dimensions.get(k, 0.0)
            state.dimensions[k] = sv + (bv - sv) * alpha
        state.recompute_intensity()
        state.touch()
        return state

    def reinforce_state_to_memory(self, state: StateInstance, memory_manager=None):
        # minimal: append a marker to person_state.memory_refs
        if self.person_state is not None:
            self.person_state.add_memory_ref({"state_id": state.id, "reinforced": True, "timestamp": now_iso()})

    # ------------------ labels & conflicts ------------------
    def derive_labels_from_dimensions(self, state: StateInstance) -> List[str]:
        dims = state.dimensions
        labels = []

        if dims.get("attention", 0.0) >= 0.6 and dims.get("goal_relevance", 0.0) >= 0.6 and dims.get("motivation", 0.0) >= 0.5 and dims.get("arousal", 1.0) <= 0.85:
            labels.append("focused")

        if dims.get("motivation", 0.0) >= 0.6 and (dims.get("goal_relevance", 0.0) >= 0.6 or dims.get("confidence", 0.0) >= 0.5):
            labels.append("motivated")

        if dims.get("optimism", 0.0) >= 0.6 or (dims.get("confidence", 0.0) >= 0.7 and dims.get("motivation", 0.0) >= 0.4):
            labels.append("optimistic")

        if dims.get("sadness", 0.0) >= 0.5 or dims.get("coherence", 1.0) <= 0.3:
            labels.append("sad")

        if dims.get("threat", 0.0) >= 0.6 and (dims.get("arousal", 0.0) >= 0.5 or dims.get("self_regulation", 1.0) <= 0.4):
            labels.append("defensive")

        if dims.get("coherence", 1.0) <= 0.3 and dims.get("attention", 1.0) <= 0.4 and state.confidence <= 0.4:
            labels.append("confused")

        return list(dict.fromkeys(labels))

    def handle_manual_override(self, state_or_dimensions: Any, reason: str = "manual"): 
        if isinstance(state_or_dimensions, StateInstance):
            s = state_or_dimensions
            s.manual = True
            s.manual_reason = reason
            s.touch()
            return s
        else:
            # create a manual state from dims
            er = EvidenceRecord.create("manual", "manual", state_or_dimensions, confidence=1.0)
            return self.create_state_from_trigger("manual", er, initial_dims=state_or_dimensions)

    def resolve_contradictions(self, states: List[StateInstance]) -> List[StateInstance]:
        # naive conflict detector: if two states have opposing high dimensions, mark conflict
        for i, s in enumerate(states):
            for j, t in enumerate(states):
                if i >= j:
                    continue
                # if s.threat high and t.motivation high, report coexistence
                if s.dimensions.get("threat", 0.0) >= 0.6 and t.dimensions.get("motivation", 0.0) >= 0.6:
                    s.conflict_info = {"type": "coexistence", "other": t.id}
                    t.conflict_info = {"type": "coexistence", "other": s.id}
        return states

    # ------------------ influence ------------------
    def propagate_influence(self, source_state: StateInstance, target_state: StateInstance, influence_map: Dict[str, float]) -> Tuple[StateInstance, StateInstance]:
        # apply influence proportionally to source intensity
        for dim, weight in influence_map.items():
            delta = source_state.intensity * float(weight)
            old = target_state.dimensions.get(dim, 0.0)
            target_state.dimensions[dim] = max(0.0, min(1.0, old + delta))
        # record links
        if source_state.id not in target_state.influenced_by:
            target_state.influenced_by.append(source_state.id)
        if target_state.id not in source_state.influences:
            source_state.influences.append(target_state.id)
        target_state.recompute_intensity()
        target_state.touch()
        source_state.touch()
        return source_state, target_state

    # ------------------ helpers ------------------
    def _overlap_score(self, dims_a: Dict[str, float], dims_b: Dict[str, float]) -> float:
        # cosine similarity on shared dims
        keys = set(dims_a.keys()) & set(dims_b.keys())
        if not keys:
            return 0.0
        num = sum(dims_a[k] * dims_b[k] for k in keys)
        denom_a = math.sqrt(sum(dims_a[k] ** 2 for k in keys))
        denom_b = math.sqrt(sum(dims_b[k] ** 2 for k in keys))
        if denom_a == 0 or denom_b == 0:
            return 0.0
        return num / (denom_a * denom_b)

    def _duration_seconds(self, state: StateInstance) -> float:
        try:
            s = datetime.fromisoformat(state.onset)
            e = datetime.fromisoformat(state.last_update)
            return (e - s).total_seconds()
        except Exception:
            return 0.0