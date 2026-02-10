# Parser Agent Explanation

This document explains the architecture and workflow of the current agent implementation in the `parser` repository.

## Overview

The agent is designed to perform tasks in a web browser environment using **Monte Carlo Tree Search (MCTS)** for planning. It moves away from pixel-based planning to a **DOM-based** approach, using the capabilities of the browser's Document Object Model to understand and interact with the page.

## Key Components

The codebase is modular, with each component handling a specific aspect of the agent's lifecycle:

### 1. `main.py` (Entry Point)
- **Role**: Configures and launches the agent.
- **Functionality**:
    - Instantiates specific implementations of `ActionGenerator`, `RewardModel`, and `PriorPolicy`.
    - Configures the `MCTSPlanner` with search parameters (simulations, depth, top-k).
    - Creates an `AgentRunner` and a `MockBrowserEnv`.
    - Runs a baseline episode and prints the results.

### 2. `runner/` (Execution Loop)
- **`AgentRunner`**: The main loop that orchestrates the agent-environment interaction.
    - Observes the current state.
    - Queries the `planner` for the next best action.
    - Executes the action in the environment.
    - Records the trace of events.
- **`MockBrowserEnv`**: A placeholder environment that simulates a browser's state and responses for testing purposes without a real browser instance.

### 3. `search/` (Planning Core)
- **`MCTSPlanner`**: Implements the Monte Carlo Tree Search algorithm.
    - Uses `ActionGenerator` to expand the tree.
    - Uses `PriorPolicy` to guide selection.
    - Uses `RewardModel` to evaluate leaf nodes.
- **`MCTSConfig`**: define hyperparameters like number of simulations (`simulations=80`), rollout depth (`rollout_depth=5`), etc.
- **`PriorPolicy`**: A heuristic or learned model that suggests promising actions to explore first.

### 4. `action_space/` (Action Generation)
- **`ActionGenerator`**: Responsible for analyzing the current DOM state and enforcing rules to generate a list of valid, executable actions (e.g., `click`, `type`, `scroll`).

### 5. `dom_encoder/` (Perception)
- **`Encoder`**: Transforms the raw DOM tree into a structured state representation (embedding or feature vector) that the models and planner can process.

### 6. `reward/` (Evaluation)
- **`RewardModel`**: A component that assigns a scalar value to a state or action sequence, indicating how close the agent is to completing the user's objective.

### 7. `traces/` (Debugging)
- **`TraceRecorder`**: Captures the full history of the agent's reasoning process, including search trees, selected actions, and environment feedback, for later analysis.

## Workflow

1.  **Initialize**: `main.py` builds the components and the runner.
2.  **Observe**: The runner asks the environment for the current state (DOM).
3.  **Plan**: The `MCTSPlanner` builds a search tree:
    *   **Select**: Choose a promising node using Upper Confidence Bound (UCB).
    *   **Expand**: Generate possible next actions using `ActionGenerator`.
    *   **Simulate**: Estimate the value of the new state using the `RewardModel` or a rollout policy.
    *   **Backpropagate**: Update the values of ancestor nodes.
4.  **Act**: The best action from the search is selected and executed in the real (or mock) environment.
5.  **Repeat**: The loop continues until the task is done or a limit is reached.
