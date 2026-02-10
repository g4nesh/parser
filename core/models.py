from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DOMNode:
    """Canonical, model-friendly DOM node representation."""

    node_id: str
    tag: str
    text: str = ""
    attributes: dict[str, str] = field(default_factory=dict)
    visible: bool = True
    interactable: bool = False
    role: str | None = None
    children: list[str] = field(default_factory=list)


@dataclass
class DOMState:
    """Structured environment state used by search."""

    url: str
    nodes: dict[str, DOMNode]
    focused_node_id: str | None = None
    interaction_history: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)
    step: int = 0

    def clone(self) -> "DOMState":
        return DOMState(
            url=self.url,
            nodes={
                node_id: DOMNode(
                    node_id=node.node_id,
                    tag=node.tag,
                    text=node.text,
                    attributes=dict(node.attributes),
                    visible=node.visible,
                    interactable=node.interactable,
                    role=node.role,
                    children=list(node.children),
                )
                for node_id, node in self.nodes.items()
            },
            focused_node_id=self.focused_node_id,
            interaction_history=list(self.interaction_history),
            metadata=dict(self.metadata),
            step=self.step,
        )


@dataclass(frozen=True)
class TaskSpec:
    objective: str
    success_text: str = "success"


@dataclass
class RewardBreakdown:
    total: float
    progress: float
    risk: float
    efficiency: float
    terminal: float
