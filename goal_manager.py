"""Goal manager API: generate and manage active goals based on values, needs, identity, and beliefs.

This module provides a simple `GoalManager` class that exposes `generate_goals`.
It is intentionally lightweight and is intended to be expanded with planners.
"""
from typing import Any, Dict, List


def compute_identity_goal_relevance(identity_schema: Dict[str, Any], goal: Any, context: Any = None, *, require_context: bool = False) -> float:
    """Return a relevance score for an identity-protective goal.

    This is intentionally a shared primitive: it does not name a specific action,
    and it can be used both for goal generation and for action scoring. When
    `require_context` is true, the call only counts as relevant in threat-like
    situations such as insults, attacks, disrespect, or challenge.
    """
    if not isinstance(identity_schema, dict) or goal is None:
        return 0.0

    goal_text = str(goal).lower() if not isinstance(goal, dict) else " ".join(
        str(part).lower() for part in [
            goal.get("description", ""),
            goal.get("id", ""),
            goal.get("origin", {}).get("need", "") if isinstance(goal.get("origin", {}), dict) else "",
            goal.get("origin", {}).get("value", "") if isinstance(goal.get("origin", {}), dict) else "",
        ] if part is not None
    )
    if not goal_text.strip():
        return 0.0

    if require_context:
        context_text = str(context or "").lower()
        threat_words = (
            "insult", "disrespect", "attack", "threat", "mock", "taunt", "challenge",
            "offense", "humiliate", "provoke", "accusation", "confrontation"
        )
        if not context_text or not any(word in context_text for word in threat_words):
            return 0.0

    roles = identity_schema.get("roles", {}) or {}
    standards = identity_schema.get("standards", []) or []
    relevance = 0.0

    for role_name, weight in (roles.items() if isinstance(roles, dict) else []):
        role_text = str(role_name).lower()
        if role_text and (role_text in goal_text or goal_text in role_text):
            relevance += float(weight)

    for standard in standards:
        standard_text = str(standard).lower()
        if standard_text and (standard_text in goal_text or goal_text in standard_text):
            relevance += 0.25

    if isinstance(goal, dict):
        origin = goal.get("origin", {}) or {}
        if isinstance(origin, dict):
            for key in ("need", "value"):
                token = str(origin.get(key, "")).lower()
                if token and (token in goal_text or goal_text in token):
                    relevance += 0.5
        priority = float(goal.get("priority", 0.0) or 0.0)
        if priority > 0:
            relevance += min(priority / 10.0, 1.0)

    return max(0.0, relevance)


class GoalManager:
    def __init__(self):
        # Active goals is a list of goal dicts
        self.active_goals: List[Dict[str, Any]] = []

    def _normalize_value_weights(self, value_weights):
        if isinstance(value_weights, dict):
            return {str(k): float(v) for k, v in value_weights.items()}
        if isinstance(value_weights, list):
            normalized = {}
            for item in value_weights:
                if isinstance(item, dict):
                    key = item.get("id") or item.get("name") or item.get("value")
                    weight = item.get("weight", 0.0)
                    if key is not None:
                        normalized[str(key)] = float(weight)
                else:
                    normalized[str(item)] = 1.0
            return normalized
        return {}

    def _normalize_need_state(self, need_state):
        if isinstance(need_state, dict):
            return {str(k): float(v) for k, v in need_state.items()}
        return {}

    def _identity_boost(self, identity_schema: Dict[str, Any], need: str):
        """Goal generation compatibility wrapper around the shared identity relevance primitive."""
        if not isinstance(identity_schema, dict):
            return 0.0

        goal = {
            "description": f"Satisfy {need}",
            "origin": {"need": str(need), "value": str(need)},
        }
        return compute_identity_goal_relevance(identity_schema, goal, context=None, require_context=False)

    def generate_goals(self, value_weights: Dict[str, float], need_state: Dict[str, float], identity_schema: Dict[str, Any], max_goals: int = 5):
        """Generate prioritized goals from values, needs, and identity.

        This is a conservative default: combine value weight and need urgency
        to produce candidate goals. Identity can boost goals that match active roles.
        Returns a list of goal dicts with keys: id, description, priority, origin.
        """
        candidates = []
        normalized_values = self._normalize_value_weights(value_weights)
        normalized_needs = self._normalize_need_state(need_state)
        identity_roles = identity_schema.get("roles", {}) if isinstance(identity_schema, dict) else {}
        identity_standards = identity_schema.get("standards", []) if isinstance(identity_schema, dict) else []

        # Simple heuristic: for each need, propose a goal aligned with top values
        for need, urgency in normalized_needs.items():
            # pick top value to satisfy
            if normalized_values:
                top_value, top_weight = max(normalized_values.items(), key=lambda t: t[1])
            else:
                top_value, top_weight = None, 0.5

            identity_bonus = self._identity_boost(identity_schema, need)
            priority = float(urgency) * (top_weight if top_value else 0.5)
            priority += identity_bonus

            role_hint = ""
            if isinstance(identity_roles, dict):
                active_roles = [str(name) for name, weight in identity_roles.items() if float(weight) > 0]
                if active_roles:
                    role_hint = f" consistent with {', '.join(active_roles[:2])}"

            standard_hint = ""
            if isinstance(identity_standards, list) and identity_standards:
                standard_hint = f" and standards {', '.join(str(s) for s in identity_standards[:2])}"

            goal = {
                "id": f"goal:{need}:{top_value}",
                "description": f"Satisfy {need} in a way consistent with {top_value}{role_hint}{standard_hint}",
                "priority": priority,
                "origin": {"need": need, "value": top_value, "identity": identity_schema},
            }
            candidates.append(goal)

        # sort and trim
        candidates.sort(key=lambda g: g["priority"], reverse=True)
        self.active_goals = candidates[:max_goals]
        return self.active_goals
