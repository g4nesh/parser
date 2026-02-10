from __future__ import annotations

from core.models import DOMNode, DOMState


class DOMEncoder:
    """Converts raw browser snapshots into canonical DOMState objects."""

    def encode(self, snapshot: dict) -> DOMState:
        url = str(snapshot.get("url", "about:blank"))
        raw_nodes = snapshot.get("nodes", [])
        nodes: dict[str, DOMNode] = {}

        for index, raw_node in enumerate(raw_nodes):
            node_id = str(raw_node.get("id", f"n{index}"))
            node = DOMNode(
                node_id=node_id,
                tag=str(raw_node.get("tag", "div")).lower(),
                text=str(raw_node.get("text", "")),
                attributes={
                    str(key): str(value)
                    for key, value in dict(raw_node.get("attributes", {})).items()
                },
                visible=bool(raw_node.get("visible", True)),
                interactable=bool(raw_node.get("interactable", False)),
                role=(
                    str(raw_node.get("role"))
                    if raw_node.get("role") is not None
                    else None
                ),
                children=[str(child) for child in raw_node.get("children", [])],
            )
            nodes[node_id] = node

        state = DOMState(
            url=url,
            nodes=nodes,
            focused_node_id=(
                str(snapshot["focused_node_id"])
                if snapshot.get("focused_node_id") is not None
                else None
            ),
            interaction_history=[str(item) for item in snapshot.get("history", [])],
            metadata={
                str(key): str(value)
                for key, value in dict(snapshot.get("metadata", {})).items()
            },
            step=int(snapshot.get("step", 0)),
        )
        return self.canonicalize(state)

    def canonicalize(self, state: DOMState) -> DOMState:
        canonical_nodes = {
            node_id: state.nodes[node_id] for node_id in sorted(state.nodes.keys())
        }
        return DOMState(
            url=state.url,
            nodes=canonical_nodes,
            focused_node_id=state.focused_node_id,
            interaction_history=list(state.interaction_history),
            metadata={key: state.metadata[key] for key in sorted(state.metadata.keys())},
            step=state.step,
        )
