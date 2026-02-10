from __future__ import annotations

from action_space.actions import Action
from core.models import DOMState, RewardBreakdown


class RewardModel:
    """Heuristic reward model for baseline planning and simulation."""

    def evaluate(
        self,
        prev_state: DOMState,
        action: Action,
        next_state: DOMState,
        is_terminal: bool,
        is_success: bool,
    ) -> RewardBreakdown:
        progress = self._progress_reward(prev_state, action, next_state)
        risk = self._risk_penalty(action)
        efficiency = -0.02
        terminal = 0.0

        if is_terminal:
            terminal = 1.0 if is_success else -1.0

        total = progress + risk + efficiency + terminal
        return RewardBreakdown(
            total=total,
            progress=progress,
            risk=risk,
            efficiency=efficiency,
            terminal=terminal,
        )

    def _progress_reward(
        self,
        prev_state: DOMState,
        action: Action,
        next_state: DOMState,
    ) -> float:
        reward = 0.0

        if action.action_type == "type" and action.node_id:
            was_filled = prev_state.metadata.get(f"filled:{action.node_id}") == "true"
            is_filled = next_state.metadata.get(f"filled:{action.node_id}") == "true"
            reward += 0.7 if not was_filled and is_filled else 0.1

        if action.action_type == "click":
            reward += 0.1
            if action.node_id == "n_submit" and next_state.metadata.get("all_required_filled") == "true":
                reward += 0.7

        if action.action_type == "select":
            reward += 0.2

        if action.action_type == "scroll":
            reward -= 0.05

        if len(next_state.interaction_history) > len(prev_state.interaction_history):
            reward += 0.02

        return reward

    def _risk_penalty(self, action: Action) -> float:
        if action.metadata.get("destructive") == "true":
            return -0.8
        return 0.0
