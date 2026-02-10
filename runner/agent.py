from __future__ import annotations

from dataclasses import dataclass

from action_space.actions import Action
from search.mcts import MCTSPlanner, PlanResult
from traces.recorder import TraceRecorder


@dataclass
class EpisodeResult:
    success: bool
    steps: int
    executed_actions: list[Action]
    final_plan: PlanResult | None


class AgentRunner:
    """Runs online re-planning loop: observe -> search -> execute prefix."""

    def __init__(
        self,
        planner: MCTSPlanner,
        execute_prefix: int = 1,
        trace_recorder: TraceRecorder | None = None,
    ) -> None:
        self.planner = planner
        self.execute_prefix = max(1, execute_prefix)
        self.trace_recorder = trace_recorder

    def run_episode(self, env: object, max_iterations: int = 10) -> EpisodeResult:
        executed_actions: list[Action] = []
        final_plan: PlanResult | None = None

        for _ in range(max_iterations):
            if env.is_terminal():
                break

            plan_result = self.planner.plan(env)
            final_plan = plan_result
            if not plan_result.actions:
                break

            if self.trace_recorder:
                self.trace_recorder.record_plan(plan_result.actions)

            for action in plan_result.actions[: self.execute_prefix]:
                prev_state = env.observe()
                next_state = env.apply(action)
                executed_actions.append(action)
                if self.trace_recorder:
                    self.trace_recorder.record_action(prev_state, action, next_state)
                if env.is_terminal():
                    break

        return EpisodeResult(
            success=env.is_success(),
            steps=len(executed_actions),
            executed_actions=executed_actions,
            final_plan=final_plan,
        )
