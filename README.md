# Parser 

State-of-the-art Monte Carlo Tree Search (MCTS) for computer-use agents, built around the browser DOM as the primary planning interface.

## Why this project exists

Most computer-use agents still plan from pixels first and structure second. That makes long-horizon reasoning brittle, expensive, and hard to debug.

This project takes a DOM-first approach:

- Use structured page state (`DOM tree + metadata + interaction history`) as the search state.
- Use MCTS to plan multi-step action sequences before executing risky clicks or form edits.
- Keep the agent grounded in real browser affordances (click, type, select, scroll, navigate), not just token-level guesses.
