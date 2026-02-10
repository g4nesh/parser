from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from core.models import DOMState

ActionType = Literal["click", "type", "select", "scroll", "navigate"]


@dataclass(frozen=True)
class Action:
    action_type: ActionType
    node_id: str | None = None
    value: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def canonical(self) -> str:
        metadata_repr = "|".join(
            f"{key}={value}" for key, value in sorted(self.metadata.items())
        )
        return (
            f"{self.action_type}:"
            f"{self.node_id or '_'}:"
            f"{self.value or '_'}:"
            f"{metadata_repr}"
        )


class ActionGenerator:
    """Generates deterministic, canonical action candidates from DOMState."""

    def __init__(self, default_input_text: str = "sample_value") -> None:
        self.default_input_text = default_input_text

    def enumerate(self, state: DOMState) -> list[Action]:
        candidates: list[Action] = []

        for node_id in sorted(state.nodes.keys()):
            node = state.nodes[node_id]
            if not node.visible:
                continue

            if node.interactable:
                metadata: dict[str, str] = {}
                if node.attributes.get("destructive") == "true":
                    metadata["destructive"] = "true"
                candidates.append(
                    Action(action_type="click", node_id=node_id, metadata=metadata)
                )

            if node.tag in {"input", "textarea"} and node.interactable:
                placeholder = node.attributes.get("placeholder", self.default_input_text)
                value = f"{placeholder}_text"
                candidates.append(
                    Action(action_type="type", node_id=node_id, value=value)
                )

            if node.tag == "select" and node.interactable:
                options = node.attributes.get("options", "")
                first_option = options.split(",")[0].strip() if options else "option_1"
                candidates.append(
                    Action(action_type="select", node_id=node_id, value=first_option)
                )

        if state.metadata.get("scrollable", "true") == "true":
            candidates.append(
                Action(
                    action_type="scroll",
                    node_id="viewport",
                    value="300",
                )
            )

        return self._deduplicate(candidates)

    def _deduplicate(self, actions: list[Action]) -> list[Action]:
        deduped: dict[str, Action] = {}
        for action in actions:
            deduped[action.canonical()] = action
        return [deduped[key] for key in sorted(deduped.keys())]
