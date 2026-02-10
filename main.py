from __future__ import annotations

from action_space import ActionGenerator
from eval import evaluate_runner
from reward import RewardModel
from runner import AgentRunner, MockBrowserEnv
from search import MCTSConfig, MCTSPlanner, PriorPolicy
from traces import TraceRecorder


def build_runner() -> AgentRunner:
    action_generator = ActionGenerator(default_input_text="seed")
    reward_model = RewardModel()
    prior_policy = PriorPolicy()
    planner = MCTSPlanner(
        action_generator=action_generator,
        reward_model=reward_model,
        prior_policy=prior_policy,
        config=MCTSConfig(simulations=80, rollout_depth=5, top_k_actions=8),
    )
    return AgentRunner(planner=planner, execute_prefix=1, trace_recorder=TraceRecorder())


def main() -> None:
    runner = build_runner()
    env = MockBrowserEnv()
    result = runner.run_episode(env)

    print("DOM-MCTS baseline run")
    print(f"success: {result.success}")
    print(f"steps: {result.steps}")
    print("executed actions:")
    for index, action in enumerate(result.executed_actions, start=1):
        print(f"  {index}. {action.canonical()}")

    summary = evaluate_runner(runner=runner, env_factory=MockBrowserEnv, episodes=3)
    print("\nquick eval:")
    print(f"  episodes: {summary.episodes}")
    print(f"  success_rate: {summary.success_rate:.2f}")
    print(f"  avg_steps: {summary.avg_steps:.2f}")


if __name__ == "__main__":
    main()
