"""
Arbitration module: choose final action from candidate action scores.

This starter implementation uses a deterministic argmax with an optional
confidence calculation. It is intentionally simple so we can iterate.
"""
from typing import Dict, Tuple, Optional, List


def arbitrate(action_scores: Dict[str, float],
              contributions: Optional[Dict[str, List[Tuple[str, float, List[str]]]]] = None
              ) -> Tuple[Optional[str], float, str]:
    """Select the action with the highest score and return (action, confidence, reason).

    `contributions` is an optional mapping action -> list of tuples
      (system_name, contribution_value, reasons_list)

    Returns chosen_action (or None), confidence (0-100), and a brief reason string
    describing which systems proposed the chosen action and why.
    """

    if not action_scores:
        return None, 0.0, "No candidates"

    total = sum(action_scores.values())

    if total <= 0:
        return None, 0.0, "All-zero scores"

    # Choose argmax
    chosen = max(action_scores, key=action_scores.get)
    confidence = action_scores[chosen] / total * 100

    # Build reason from contributions if available
    reason_parts = []
    if contributions and chosen in contributions:
        parts = contributions[chosen]
        # sort parts by contribution descending
        parts_sorted = sorted(parts, key=lambda t: t[1], reverse=True)
        for sys_name, contrib, reasons in parts_sorted:
            reason_text = f"{sys_name}(+{contrib:.2f})"
            if reasons:
                reason_text += f" [{'; '.join(reasons[:2])}]"
            reason_parts.append(reason_text)

    if reason_parts:
        reason = f"Chosen because: {'; '.join(reason_parts)}"
    else:
        reason = f"Chosen by highest score ({chosen}={action_scores[chosen]:.2f})"

    return chosen, confidence, reason
