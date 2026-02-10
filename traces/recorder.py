from __future__ import annotations

from dataclasses import asdict, dataclass

from action_space.actions import Action
from core.models import DOMState


@dataclass
class TraceEvent:
    step: int
    action: str
    url: str
    success: bool


class TraceRecorder:
    """Minimal in-memory recorder for baseline replayability."""

    def __init__(self) -> None:
        self.events: list[TraceEvent] = []
        self.plans: list[list[str]] = []

    def record_plan(self, actions: list[Action]) -> None:
        self.plans.append([action.canonical() for action in actions])

    def record_action(
        self,
        prev_state: DOMState,
        action: Action,
        next_state: DOMState,
    ) -> None:
        self.events.append(
            TraceEvent(
                step=next_state.step,
                action=action.canonical(),
                url=prev_state.url,
                success=next_state.metadata.get("success") == "true",
            )
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "plans": self.plans,
            "events": [asdict(event) for event in self.events],
        }
