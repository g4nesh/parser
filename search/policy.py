from __future__ import annotations

from action_space.actions import Action
from core.models import DOMState


class PriorPolicy:
    """Simple heuristic prior over candidate actions."""

    def score(self, state: DOMState, action: Action) -> float:
        score = 0.05

        if action.action_type == "type":
            score += 0.45
            if action.node_id and state.metadata.get(f"filled:{action.node_id}") == "true":
                score -= 0.35
            if action.node_id:
                node = state.nodes.get(action.node_id)
                if node and node.attributes.get("required") == "true":
                    score += 0.4

        if action.action_type == "click":
            score += 0.2
            if action.node_id == "n_submit":
                score += 0.4
                if state.metadata.get("all_required_filled") != "true":
                    score -= 0.45

        if action.action_type == "select":
            score += 0.15

        if action.action_type == "scroll":
            score -= 0.08

        if action.metadata.get("destructive") == "true":
            score -= 0.5

        return max(score, 0.01)
