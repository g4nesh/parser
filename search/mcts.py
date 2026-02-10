from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from action_space.actions import Action, ActionGenerator
from core.models import DOMState
from reward.scoring import RewardModel
from search.policy import PriorPolicy


@dataclass
class MCTSConfig:
    simulations: int = 96
    exploration_constant: float = 1.4
    rollout_depth: int = 5
    top_k_actions: int = 12
    discount: float = 0.96


@dataclass
class TreeNode:
    state: DOMState
    parent: TreeNode | None = None
    action_from_parent: Action | None = None
    prior: float = 1.0
    visits: int = 0
    value_sum: float = 0.0
    children: dict[str, TreeNode] = field(default_factory=dict)

    @property
    def q_value(self) -> float:
        if self.visits == 0:
            return 0.0
        return self.value_sum / self.visits


@dataclass
class PlanResult:
    actions: list[Action]
    estimated_value: float
    simulations_run: int
    root: TreeNode


class MCTSPlanner:
    """Baseline PUCT planner for DOM-grounded action search."""

    def __init__(
        self,
        action_generator: ActionGenerator,
        reward_model: RewardModel,
        prior_policy: PriorPolicy,
        config: MCTSConfig | None = None,
    ) -> None:
        self.action_generator = action_generator
        self.reward_model = reward_model
        self.prior_policy = prior_policy
        self.config = config or MCTSConfig()

    def plan(self, env: Any) -> PlanResult:
        root_state = env.observe()
        root = TreeNode(state=root_state)

        for _ in range(self.config.simulations):
            sim_env = env.clone()
            node = root
            path = [root]
            depth = 0

            while True:
                if sim_env.is_terminal() or depth >= self.config.rollout_depth:
                    break

                candidate_actions = self._candidate_actions(node.state)
                unexpanded = [
                    action
                    for action in candidate_actions
                    if action.canonical() not in node.children
                ]

                if unexpanded:
                    action = unexpanded[0]
                    prior = self.prior_policy.score(node.state, action)
                    next_state = sim_env.apply(action)
                    child = TreeNode(
                        state=next_state,
                        parent=node,
                        action_from_parent=action,
                        prior=prior,
                    )
                    node.children[action.canonical()] = child
                    node = child
                    path.append(node)
                    depth += 1
                    break

                if not node.children:
                    break

                child = self._select_child(node)
                if child.action_from_parent is None:
                    break
                sim_env.apply(child.action_from_parent)
                node = child
                path.append(node)
                depth += 1

            value = self._rollout(sim_env, depth)
            self._backpropagate(path, value)

        actions = self._extract_best_plan(root)
        return PlanResult(
            actions=actions,
            estimated_value=root.q_value,
            simulations_run=self.config.simulations,
            root=root,
        )

    def _candidate_actions(self, state: DOMState) -> list[Action]:
        actions = self.action_generator.enumerate(state)
        ranked = sorted(
            actions,
            key=lambda action: self.prior_policy.score(state, action),
            reverse=True,
        )
        return ranked[: self.config.top_k_actions]

    def _select_child(self, node: TreeNode) -> TreeNode:
        assert node.children, "Cannot select a child from a leaf node"
        parent_visits = max(node.visits, 1)

        def score(child: TreeNode) -> float:
            exploration = (
                self.config.exploration_constant
                * child.prior
                * math.sqrt(parent_visits)
                / (1 + child.visits)
            )
            return child.q_value + exploration

        return max(node.children.values(), key=score)

    def _rollout(self, sim_env: Any, depth: int) -> float:
        total = 0.0
        discount = 1.0
        current_depth = depth

        while not sim_env.is_terminal() and current_depth < self.config.rollout_depth:
            state = sim_env.observe()
            candidates = self._candidate_actions(state)
            if not candidates:
                break

            action = candidates[0]
            prev_state = state
            next_state = sim_env.apply(action)
            breakdown = self.reward_model.evaluate(
                prev_state=prev_state,
                action=action,
                next_state=next_state,
                is_terminal=sim_env.is_terminal(),
                is_success=sim_env.is_success(),
            )
            total += discount * breakdown.total
            discount *= self.config.discount
            current_depth += 1

        return total

    def _backpropagate(self, path: list[TreeNode], value: float) -> None:
        running = value
        for node in reversed(path):
            node.visits += 1
            node.value_sum += running
            running *= self.config.discount

    def _extract_best_plan(self, root: TreeNode) -> list[Action]:
        plan: list[Action] = []
        node = root

        for _ in range(self.config.rollout_depth):
            if not node.children:
                break
            best_child = max(
                node.children.values(),
                key=lambda child: (child.visits, child.q_value),
            )
            if best_child.action_from_parent is None:
                break
            plan.append(best_child.action_from_parent)
            node = best_child

        return plan
