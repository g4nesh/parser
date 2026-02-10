# Parser 

State-of-the-art Monte Carlo Tree Search (MCTS) for computer-use agents, built around the browser DOM as the primary planning interface.

## Why this project exists

Most computer-use agents still plan from pixels first and structure second. That makes long-horizon reasoning brittle, expensive, and hard to debug.

This project takes a DOM-first approach:

- Use structured page state (`DOM tree + metadata + interaction history`) as the search state.
- Use MCTS to plan multi-step action sequences before executing risky clicks or form edits.
- Keep the agent grounded in real browser affordances (click, type, select, scroll, navigate), not just token-level guesses.

## What I am building

I am building a new MCTS-type tool for computer-use agents that treats browser automation as a search problem over DOM states.

Core goals:

- Better long-horizon reliability on real web tasks.
- Lower action regret (fewer irreversible mistakes).
- Interpretable plans with inspectable search trees.
- Practical latency and token efficiency for production agent loops.

## State-of-the-art direction

This system is designed to push beyond baseline "act-react" agents by combining:

- **DOM-grounded state encoding**: semantic node features, visibility/interactability, form context, and ARIA/accessibility signals.
- **Action abstraction**: deduplicated high-level actions (`click(node)`, `type(node,text)`, `select(node,opt)`, `scroll(region,delta)`), not raw coordinates.
- **Learned + heuristic priors**: policy prior over candidate actions and value estimates for partial trajectories.
- **Constraint-aware expansion**: guardrails for unsafe/destructive operations and impossible transitions.
- **Tool-augmented rollouts**: optional model calls during simulation for uncertain branches.
- **Replayable traces**: tree snapshots, selected path, reward decomposition, and failure diagnostics.

## High-level architecture

1. **Perception Layer**
   - Capture DOM snapshot, URL, focused element, and optional visual context.
   - Normalize into a compact state representation.

2. **Proposal Layer**
   - Enumerate valid action candidates from the current DOM.
   - Rank/filter candidates with priors and task constraints.

3. **Search Layer (MCTS)**
   - Selection via PUCT-style scoring.
   - Expansion over top-k legal DOM actions.
   - Simulation with lightweight environment model and optional LLM guidance.
   - Backpropagation of task reward, risk penalties, and progress signals.

4. **Execution Layer**
   - Execute the best action sequence prefix.
   - Re-observe, detect divergence, and replan online.

## MCTS loop (DOM-adapted)

```text
while task_not_done:
  s0 = observe_dom_state()
  tree = init_tree(root=s0)

  for sim in 1..N:
    node = select(tree, puct)
    if not terminal(node):
      actions = enumerate_dom_actions(node.state)
      child = expand(node, actions, policy_prior)
      reward = rollout(child.state, horizon=H)
    else:
      reward = terminal_reward(node.state)
    backpropagate(node, reward)

  plan = best_path(tree)
  execute_prefix(plan, steps=M)
```

## Planned components

- `dom_encoder/`: state extraction + canonicalization
- `action_space/`: legal action generation and normalization
- `search/`: MCTS core (selection/expansion/simulation/backprop)
- `reward/`: progress, correctness, risk, and efficiency scoring
- `runner/`: browser control loop + replanning
- `eval/`: benchmark harness, metrics, and regression suite
- `traces/`: searchable debug artifacts for failed/successful runs

## Evaluation strategy

Primary metrics:

- Task success rate
- Steps to completion
- Irreversible-error rate
- Replan frequency
- Wall-clock latency
- Model/token cost per successful task

Benchmarks will focus on realistic web workflows:

- Form completion
- Multi-page navigation
- Information extraction with verification
- Stateful tasks (auth/session/cart-like flows)

## Current status

This repository is the build ground for the first production-quality version.

Near-term roadmap:

1. Implement DOM state schema and action canonicalization.
2. Ship baseline MCTS with deterministic rollout policy.
3. Add learned priors/value model interface.
4. Add trace viewer and regression benchmarks.
5. Optimize for parallel simulation + lower latency.

## Design principles

- **DOM over pixels** when possible; use pixels as supporting context.
- **Plan first, act carefully** on high-impact pages.
- **Every action must be explainable** through tree evidence.
- **Fail loudly and recover quickly** with automatic replanning.
- **Measure everything** and iterate on benchmarked deltas.

## Contributing

Contributions are welcome once the initial scaffold lands. If you want to collaborate early, open an issue describing:

- The workflow or benchmark you care about
- Failure cases you want the search stack to solve
- Proposed algorithmic or systems improvements

## License

TBD
