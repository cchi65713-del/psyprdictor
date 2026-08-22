"""
Action selection heuristics for PsyPredictor.

Produces candidate actions and scores based on the current `PersonState`.
This is a lightweight, rule-based starter module that will be replaced
by more sophisticated selectors (RL, basal-ganglia-style, etc.) later.
"""
from typing import Dict, List
from dataclasses import dataclass

# Import BehavioralTendency for structured proposals
from competition import BehavioralTendency
from goal_manager import compute_identity_goal_relevance


@dataclass
class ProposalResult:
    """Backwards-compatible result wrapper.

    Supports unpacking into (scores, reasons) for existing callers,
    while exposing `.tendencies` for the new structured proposals.
    """
    scores: Dict[str, float]
    reasons: Dict[str, List[str]]
    tendencies: List[BehavioralTendency]

    def __iter__(self):
        # Allows `scores, reasons = propose_goal_directed(...)` to keep working
        yield self.scores
        yield self.reasons


class ActionSelector:

    DEFAULT_ACTIONS = [
        "RespondImmediately",
        "StayQuiet",
        "WalkAway",
        "Negotiation"
    ]

    def __init__(self):
        pass

    def apply_system_memory_influence(
        self,
        scores: Dict[str, float],
        person_state,
        system_memory,
        person_id: str
    ):
        """Apply SystemMemory influences to action scores.

        Considers beliefs, values, needs, goals, preferences, personality,
        identity, history, relationships, rules, and environment to modulate
        action tendencies.

        Returns (modified_scores, influences_dict).
        """

        if not system_memory or not person_id:
            return scores, {a: [] for a in self.DEFAULT_ACTIONS}

        # Retrieve person's system memory data
        beliefs = system_memory.beliefs.get(person_id, [])
        values = system_memory.values.get(person_id, [])
        history = system_memory.history.get(person_id, [])
        rules = system_memory.rules.get(person_id, [])
        relationships = system_memory.relationships.get(person_id, [])
        environment = system_memory.environment.get(person_id, None)

        # Initialize influence tracking
        influences = {a: [] for a in self.DEFAULT_ACTIONS}

        # Rule-based influences
        for rule in rules:
            rule_lower = rule.lower()
            if "attack" in rule_lower and "respond" in rule_lower and "immediate" in rule_lower:
                scores["RespondImmediately"] += 0.8
                influences["RespondImmediately"].append(f"Rule: {rule}")
            if "avoid" in rule_lower and "confront" in rule_lower:
                scores["WalkAway"] += 0.6
                scores["StayQuiet"] += 0.5
                influences["WalkAway"].append(f"Rule: {rule}")
                influences["StayQuiet"].append(f"Rule: {rule}")
            if "negotiat" in rule_lower or "discuss" in rule_lower:
                scores["Negotiation"] += 0.7
                influences["Negotiation"].append(f"Rule: {rule}")

        # Belief-based influences
        for belief in beliefs:
            belief_lower = belief.lower()
            if "respect" in belief_lower and "defend" in belief_lower:
                scores["RespondImmediately"] += 0.5
                influences["RespondImmediately"].append(f"Belief: {belief}")
            if "conflict" in belief_lower and "bad" in belief_lower:
                scores["StayQuiet"] += 0.4
                scores["WalkAway"] += 0.4
                influences["StayQuiet"].append(f"Belief: {belief}")
                influences["WalkAway"].append(f"Belief: {belief}")

        # Value-based influences
        for value in values:
            value_lower = value.lower()
            if "self" in value_lower and "respect" in value_lower:
                scores["RespondImmediately"] += 0.4
                scores["Negotiation"] += 0.3
                influences["RespondImmediately"].append(f"Value: {value}")
            if "harmony" in value_lower or "peace" in value_lower:
                scores["Negotiation"] += 0.6
                scores["StayQuiet"] += 0.3
                influences["Negotiation"].append(f"Value: {value}")

        # History-based influences
        for hist_event in history:
            hist_lower = hist_event.lower()
            if "conflict" in hist_lower and "ignored" in hist_lower:
                scores["RespondImmediately"] += 0.4
                influences["RespondImmediately"].append(f"History: {hist_event}")

        # Relationship influences
        for relationship in relationships:
            rel_lower = relationship.lower()
            if "difficult" in rel_lower:
                scores["StayQuiet"] += 0.3
                scores["WalkAway"] += 0.2
                influences["StayQuiet"].append(f"Relationship: {relationship}")

        # Environment influences
        if environment:
            env_lower = environment.lower()
            if "high" in env_lower and "conflict" in env_lower:
                scores["StayQuiet"] += 0.2
                scores["WalkAway"] += 0.1
                influences["StayQuiet"].append(f"Environment: {environment}")

        return scores, influences

    def score_actions(self, person_state, current_pattern_id=None, matching_experiences=None) -> Dict[str, float]:
        """Return a mapping action -> raw score (higher = more preferred).

        Uses simple, interpretable heuristics based on:
        - arousal, self_regulation, perceived_control
        - habit_strength for the current pattern (if available)
        - personality tendencies (aggression, avoidant)
        - awareness/confidence
        """

        scores = {a: 0.0 for a in self.DEFAULT_ACTIONS}

        # Basic personality / regulation influences
        aggression = person_state.personality.get("aggression", 0.5)
        avoidant = person_state.personality.get("avoidant", 0.5)

        arousal = getattr(person_state, "arousal", 0.0)
        self_reg = getattr(person_state, "self_regulation", 0.5)
        perceived_control = getattr(person_state, "perceived_control", 0.5)
        awareness = getattr(person_state, "awareness", 0.5)

        # Habit influence (if a habit exists for this pattern)
        habit_influence = 0.0
        if current_pattern_id and isinstance(person_state.habit_strength, dict):
            habit_entry = person_state.habit_strength.get(current_pattern_id, {})
            # habit_entry expected to be dict action->strength
            if isinstance(habit_entry, dict):
                for action, strength in habit_entry.items():
                    if action in scores:
                        scores[action] += strength
                        habit_influence += strength

        # Aggressive / immediate responding increases RespondImmediately
        scores["RespondImmediately"] += aggression * 0.6 + arousal * 0.4

        # Avoidant increases WalkAway and StayQuiet
        scores["WalkAway"] += avoidant * 0.7 + (1 - perceived_control) * 0.3
        scores["StayQuiet"] += avoidant * 0.4 + awareness * 0.2

        # Negotiation favored when self-regulation and perceived control are high
        scores["Negotiation"] += self_reg * 0.5 + perceived_control * 0.5

        # Normalize by simple scaling to avoid zero-sum issues
        # Add small awareness bias: more aware -> favors negotiation/stay quiet
        scores["StayQuiet"] += awareness * 0.1
        scores["Negotiation"] += awareness * 0.1

        # If habit influence dominates, slightly amplify habitual choices
        if habit_influence > 0:
            for a in scores:
                scores[a] += habit_influence * 0.2

        # Ensure positive scores
        for k in list(scores.keys()):
            if scores[k] < 0:
                scores[k] = 0.0

        return scores


def suggest_actions(person_state, current_pattern_id=None, matching_experiences=None) -> Dict[str, float]:
    selector = ActionSelector()
    return selector.score_actions(person_state, current_pattern_id, matching_experiences)


def propose_goal_directed(person_state, current_context=None, current_pattern_id=None):
    """Goal-directed system: proposes actions based on goals, needs, values, and beliefs.

    Returns (scores: Dict[action,float], reasons: Dict[action,List[str]])
    """
    selector = ActionSelector()
    # Start from a mild baseline influenced by personality/regulation
    base = selector.score_actions(person_state, current_pattern_id)
    scores = {a: 0.0 for a in selector.DEFAULT_ACTIONS}
    reasons = {a: [] for a in selector.DEFAULT_ACTIONS}

    # Inspect declared goals/needs/values on person_state if present
    goals = getattr(person_state, "goals", []) or []
    needs = getattr(person_state, "needs", {}) or {}
    values = getattr(person_state, "values", []) or []
    identity_schema = getattr(person_state, "identity", {}) or {}

    # Simple heuristics: defensive/restore-self goals favor immediate response
    for g in goals:
        goal_dict = g if isinstance(g, dict) else {"description": str(g)}
        goal_priority = float(goal_dict.get("priority", 0.0) or 0.0)
        identity_relevance = compute_identity_goal_relevance(
            identity_schema,
            goal_dict,
            context=current_context,
            require_context=True,
        )

        gl = str(goal_dict.get("description", g)).lower()
        if identity_relevance > 0.0:
            response_boost = 0.9 + identity_relevance + min(1.0, goal_priority / 5.0)
            scores["RespondImmediately"] += response_boost
            reasons["RespondImmediately"].append(
                f"Goal identity relevance: {goal_dict.get('description', g)} (priority={goal_priority:.2f})"
            )

        if "defend" in gl or "restore" in gl or "justice" in gl:
            scores["RespondImmediately"] += 1.0
            reasons["RespondImmediately"].append(f"Goal: {g}")
        if "avoid" in gl or "preserve" in gl:
            scores["WalkAway"] += 0.8
            reasons["WalkAway"].append(f"Goal: {g}")

    # Needs: safety/harmony mapping
    for n, v in needs.items():
        nl = str(n).lower()
        if "safety" in nl and v:
            scores["WalkAway"] += 0.6
            reasons["WalkAway"].append(f"Need: {n}={v}")
        if "esteem" in nl and v:
            scores["RespondImmediately"] += 0.6
            reasons["RespondImmediately"].append(f"Need: {n}={v}")

    # Values bias negotiation or restraint
    for val in values:
        vl = str(val).lower()
        if "harmony" in vl or "peace" in vl:
            scores["Negotiation"] += 0.8
            reasons["Negotiation"].append(f"Value: {val}")
        if "honor" in vl or "respect" in vl:
            scores["RespondImmediately"] += 0.5
            reasons["RespondImmediately"].append(f"Value: {val}")

    # Add a baseline influence from the general scoring to keep proposals sensible
    for a, v in base.items():
        scores[a] += v * 0.3

    # Build BehavioralTendency objects for actions with non-zero score
    tendencies: List[BehavioralTendency] = []
    for a, raw in scores.items():
        # confidence heuristic: higher when there is explicit reasoning
        conf = 0.9 if reasons.get(a) else 0.6
        bt = BehavioralTendency(
            action=a,
            raw_strength=raw,
            source="goal_directed",
            supporting_evidence=list(reasons.get(a, [])),
            reason="; ".join(reasons.get(a, [])) if reasons.get(a) else "",
            confidence_in_proposal=conf,
            context_tags={"current_context": current_context, "pattern_id": current_pattern_id},
        )
        # set normalized_strength for transparency (will be re-normalized later)
        if bt.source in ("goal_directed", "reactive"):
            bt.normalized_strength = min(max(raw / 100.0, 0.0), 1.0)
        elif bt.source in ("habit", "habitual"):
            bt.normalized_strength = min(max(raw / 10.0, 0.0), 1.0)
        else:
            bt.normalized_strength = min(max(raw, 0.0), 1.0)

        tendencies.append(bt)

    return ProposalResult(scores=scores, reasons=reasons, tendencies=tendencies)


def propose_habitual(person_state, current_pattern_id=None, pattern_learner=None):
    """Habitual system: proposes actions based on habit_strength and pattern history.

    Returns (scores, reasons)
    """
    selector = ActionSelector()
    scores = {a: 0.0 for a in selector.DEFAULT_ACTIONS}
    reasons = {a: [] for a in selector.DEFAULT_ACTIONS}

    # Use explicit habit_strength if present
    habit_strength = getattr(person_state, "habit_strength", {}) or {}

    if current_pattern_id and isinstance(habit_strength, dict):
        entry = habit_strength.get(current_pattern_id, {})
        if isinstance(entry, dict):
            for action, strength in entry.items():
                if action in scores:
                    scores[action] += strength
                    reasons[action].append(f"Habit strength: {strength:.2f}")

    # Also consult pattern learner occurrences (if passed)
    if pattern_learner and current_pattern_id:
        try:
            pattern = pattern_learner.get_pattern_by_id(current_pattern_id)
        except Exception:
            pattern = None

        if pattern:
            # If a given action/outcome was frequent, add modest weight
            for outcome, cnt in getattr(pattern, "outcomes", {}).items():
                # Map outcomes to actions heuristically
                if outcome == "B1":
                    scores["RespondImmediately"] += 0.2 * (cnt)
                    reasons["RespondImmediately"].append(f"Pattern outcome freq: {outcome}->{cnt}")
                if outcome == "B4":
                    scores["WalkAway"] += 0.15 * (cnt)
                    reasons["WalkAway"].append(f"Pattern outcome freq: {outcome}->{cnt}")

    # Build BehavioralTendency objects
    tendencies: List[BehavioralTendency] = []
    for a, raw in scores.items():
        conf = 0.9 if reasons.get(a) else 0.6
        bt = BehavioralTendency(
            action=a,
            raw_strength=raw,
            source="habitual",
            supporting_evidence=list(reasons.get(a, [])),
            reason="; ".join(reasons.get(a, [])) if reasons.get(a) else "",
            confidence_in_proposal=conf,
            context_tags={"pattern_id": current_pattern_id},
        )
        if bt.source in ("habit", "habitual"):
            bt.normalized_strength = min(max(raw / 10.0, 0.0), 1.0)
        else:
            bt.normalized_strength = min(max(raw, 0.0), 1.0)

        tendencies.append(bt)

    return ProposalResult(scores=scores, reasons=reasons, tendencies=tendencies)


def propose_integrated(person_state, current_context=None, current_pattern_id=None, pattern_learner=None):
    """Integrated minimal Values ↔ Personality ↔ Habits interaction.

    - Compute goal-directed scores from goals/needs/values (same heuristics).
    - Apply a lightweight personality modifier to those scores.
    - Add habit strengths as learned pressure.

    Returns a ProposalResult similar to other propose_* functions and is
    intentionally conservative to preserve existing behavior.
    """
    # Start with goal-directed base
    gd_result = propose_goal_directed(person_state, current_context, current_pattern_id)
    scores = {a: 0.0 for a in gd_result.scores.keys()}
    reasons = {a: [] for a in gd_result.reasons.keys()}

    # Copy goal-directed contributions
    for a, v in gd_result.scores.items():
        scores[a] += v
        if gd_result.reasons.get(a):
            reasons[a].extend([f"GoalInfluence: {r}" for r in gd_result.reasons.get(a)])

    # Personality modifier: small, interpretable multipliers
    pers = getattr(person_state, "personality", {}) or {}
    aggression = float(pers.get("aggression", 0.5) or 0.5)
    avoidant = float(pers.get("avoidant", 0.5) or 0.5)

    # Apply additive personality bias (conservative magnitude)
    scores["RespondImmediately"] += aggression * 0.5
    reasons["RespondImmediately"].append(f"Personality: aggression={aggression:.2f}")

    scores["WalkAway"] += avoidant * 0.4
    reasons["WalkAway"].append(f"Personality: avoidant={avoidant:.2f}")

    scores["StayQuiet"] += avoidant * 0.25
    reasons["StayQuiet"].append(f"Personality: avoidant={avoidant:.2f}")

    # Habitual pressure (learned) — additive
    habit_strength = getattr(person_state, "habit_strength", {}) or {}
    if current_pattern_id and isinstance(habit_strength, dict):
        entry = habit_strength.get(current_pattern_id, {})
        if isinstance(entry, dict):
            for action, strength in entry.items():
                if action in scores:
                    scores[action] += strength
                    reasons[action].append(f"Habit pressure: {strength:.2f}")

    # Build BehavioralTendency list by reusing the same construction logic
    tendencies: List[BehavioralTendency] = []
    for a, raw in scores.items():
        conf = 0.9 if reasons.get(a) else 0.6
        bt = BehavioralTendency(
            action=a,
            raw_strength=raw,
            source="integrated",
            supporting_evidence=list(reasons.get(a, [])),
            reason="; ".join(reasons.get(a, [])) if reasons.get(a) else "",
            confidence_in_proposal=conf,
            context_tags={"current_context": current_context, "pattern_id": current_pattern_id},
        )
        bt.normalized_strength = min(max(raw / 10.0, 0.0), 1.0)
        tendencies.append(bt)

    return ProposalResult(scores=scores, reasons=reasons, tendencies=tendencies)


def propose_reactive(person_state):
    """Reactive/emotional system: immediate proposals from EFMSOMB and arousal.

    Returns (scores, reasons)
    """
    selector = ActionSelector()
    scores = {a: 0.0 for a in selector.DEFAULT_ACTIONS}
    reasons = {a: [] for a in selector.DEFAULT_ACTIONS}

    emotion = getattr(person_state, "emotion", "")
    feeling = getattr(person_state, "feeling", "")
    mood = getattr(person_state, "mood", "")
    # Prefer canonical split fields, fall back to legacy `state_of_mind`
    state_appraisal = getattr(person_state, "state_appraisal", None)
    state_emotion = getattr(person_state, "state_emotion", None)
    state_of_mind = getattr(person_state, "state_of_mind", {})
    arousal = getattr(person_state, "arousal", 0.0)

    # Heuristics: anger/frustration increase immediate responding
    combined = " ".join([str(emotion), str(feeling), str(mood)]).lower()
    # include canonical state_emotion if present
    if state_emotion:
        try:
            combined = combined + " " + " ".join(map(str, state_emotion)).lower()
        except Exception:
            combined = combined + " " + str(state_emotion).lower()
    if "anger" in combined or "frustrated" in combined or "irritated" in combined or "e4" in combined:
        scores["RespondImmediately"] += 0.9 + arousal * 0.5
        reasons["RespondImmediately"].append(f"Emotion-driven: {emotion}/{feeling}/{mood}")

    # High arousal and low self-regulation -> reactive walk away or lash out
    # Prefer canonical regulation field
    self_reg = getattr(person_state, "state_regulation", getattr(person_state, "self_regulation", 0.5))
    if arousal > 0.6 and self_reg < 0.4:
        scores["RespondImmediately"] += 0.7
        reasons["RespondImmediately"].append(f"High arousal {arousal:.2f} & low regulation {self_reg:.2f}")

    # Low arousal -> stay quiet or negotiate
    if arousal < 0.3:
        scores["StayQuiet"] += 0.5
        scores["Negotiation"] += 0.3
        reasons["StayQuiet"].append("Low arousal")

    # State-of-mind flags: prefer `state_appraisal` then legacy `state_of_mind`
    if isinstance(state_appraisal, dict) and state_appraisal.get("defensive"):
        scores["RespondImmediately"] += 0.4
        reasons["RespondImmediately"].append("State: defensive")
    elif isinstance(state_of_mind, dict) and state_of_mind.get("defensive"):
        scores["RespondImmediately"] += 0.4
        reasons["RespondImmediately"].append("State: defensive")

    # Build BehavioralTendency objects
    tendencies: List[BehavioralTendency] = []
    for a, raw in scores.items():
        conf = 0.9 if reasons.get(a) else 0.6
        bt = BehavioralTendency(
            action=a,
            raw_strength=raw,
            source="reactive",
            supporting_evidence=list(reasons.get(a, [])),
            reason="; ".join(reasons.get(a, [])) if reasons.get(a) else "",
            confidence_in_proposal=conf,
            context_tags={"emotion": getattr(person_state, "emotion", None), "arousal": getattr(person_state, "arousal", None)},
        )
        if bt.source in ("goal_directed", "reactive"):
            bt.normalized_strength = min(max(raw / 100.0, 0.0), 1.0)
        else:
            bt.normalized_strength = min(max(raw, 0.0), 1.0)

        tendencies.append(bt)

    return ProposalResult(scores=scores, reasons=reasons, tendencies=tendencies)
