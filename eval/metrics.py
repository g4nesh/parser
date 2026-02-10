from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from runner.agent import AgentRunner
from runner.environment import MockBrowserEnv


@dataclass
class EvalSummary:
    episodes: int
    success_rate: float
    avg_steps: float


def evaluate_runner(
    runner: AgentRunner,
    env_factory: Callable[[], MockBrowserEnv],
    episodes: int = 5,
) -> EvalSummary:
    successes = 0
    steps = 0

    for _ in range(episodes):
        result = runner.run_episode(env_factory())
        successes += 1 if result.success else 0
        steps += result.steps

    return EvalSummary(
        episodes=episodes,
        success_rate=successes / episodes if episodes else 0.0,
        avg_steps=steps / episodes if episodes else 0.0,
    )
