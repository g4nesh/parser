from __future__ import annotations

import unittest

from action_space import ActionGenerator
from reward import RewardModel
from runner import AgentRunner, MockBrowserEnv
from search import MCTSConfig, MCTSPlanner, PriorPolicy


class BaselineFrameworkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.action_generator = ActionGenerator(default_input_text="seed")
        self.reward_model = RewardModel()
        self.prior_policy = PriorPolicy()
        self.planner = MCTSPlanner(
            action_generator=self.action_generator,
            reward_model=self.reward_model,
            prior_policy=self.prior_policy,
            config=MCTSConfig(simulations=60, rollout_depth=5, top_k_actions=8),
        )

    def test_action_generator_emits_required_actions(self) -> None:
        state = MockBrowserEnv().observe()
        actions = self.action_generator.enumerate(state)
        canonical = {action.canonical() for action in actions}

        self.assertIn("type:n_name:name_text:", canonical)
        self.assertIn("type:n_email:email_text:", canonical)
        self.assertIn("click:n_submit:_:", canonical)

    def test_planner_prefers_non_destructive_first_move(self) -> None:
        plan = self.planner.plan(MockBrowserEnv())
        self.assertTrue(plan.actions)
        self.assertNotEqual(plan.actions[0].canonical(), "click:n_cancel:_:destructive=true")

    def test_runner_solves_mock_form_task(self) -> None:
        runner = AgentRunner(planner=self.planner, execute_prefix=1)
        result = runner.run_episode(MockBrowserEnv())
        self.assertTrue(result.success)
        self.assertGreaterEqual(result.steps, 1)


if __name__ == "__main__":
    unittest.main()
