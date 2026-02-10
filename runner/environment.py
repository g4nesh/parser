from __future__ import annotations

import copy

from action_space.actions import Action
from core.models import DOMNode, DOMState, TaskSpec


class MockBrowserEnv:
    """Deterministic browser-like env for baseline development and tests."""

    def __init__(self, max_steps: int = 8) -> None:
        self.task = TaskSpec(objective="Fill required fields and submit the form")
        self.max_steps = max_steps
        self._step = 0
        self._success = False
        self._failed = False
        self._submitted = False
        self._field_values: dict[str, str] = {"n_name": "", "n_email": ""}
        self._history: list[str] = []

    def clone(self) -> "MockBrowserEnv":
        return copy.deepcopy(self)

    def observe(self) -> DOMState:
        required_filled = all(bool(value.strip()) for value in self._field_values.values())
        status_text = "success" if self._success else "pending"
        if self._failed:
            status_text = "failed"

        nodes = {
            "n_form": DOMNode(
                node_id="n_form",
                tag="form",
                interactable=False,
                visible=True,
                children=["n_name", "n_email", "n_submit", "n_cancel"],
            ),
            "n_name": DOMNode(
                node_id="n_name",
                tag="input",
                interactable=True,
                visible=True,
                text=self._field_values["n_name"],
                attributes={
                    "placeholder": "name",
                    "required": "true",
                },
            ),
            "n_email": DOMNode(
                node_id="n_email",
                tag="input",
                interactable=True,
                visible=True,
                text=self._field_values["n_email"],
                attributes={
                    "placeholder": "email",
                    "required": "true",
                },
            ),
            "n_submit": DOMNode(
                node_id="n_submit",
                tag="button",
                text="submit",
                interactable=True,
                visible=True,
                attributes={"id": "submit"},
            ),
            "n_cancel": DOMNode(
                node_id="n_cancel",
                tag="button",
                text="cancel",
                interactable=True,
                visible=True,
                attributes={"destructive": "true"},
            ),
            "n_status": DOMNode(
                node_id="n_status",
                tag="div",
                text=status_text,
                interactable=False,
                visible=True,
            ),
        }

        metadata = {
            "all_required_filled": "true" if required_filled else "false",
            "submitted": "true" if self._submitted else "false",
            "success": "true" if self._success else "false",
            "scrollable": "true",
            "filled:n_name": "true" if bool(self._field_values["n_name"].strip()) else "false",
            "filled:n_email": "true" if bool(self._field_values["n_email"].strip()) else "false",
        }

        return DOMState(
            url="https://mock.local/form",
            nodes=nodes,
            focused_node_id=None,
            interaction_history=list(self._history),
            metadata=metadata,
            step=self._step,
        )

    def apply(self, action: Action) -> DOMState:
        if self.is_terminal():
            return self.observe()

        self._step += 1
        self._history.append(action.canonical())

        if action.action_type == "type" and action.node_id in self._field_values:
            self._field_values[action.node_id] = (action.value or "").strip()

        if action.action_type == "click":
            if action.node_id == "n_submit":
                self._submitted = True
                if all(bool(value.strip()) for value in self._field_values.values()):
                    self._success = True
                else:
                    self._failed = True
            elif action.node_id == "n_cancel":
                self._failed = True

        if self._step >= self.max_steps and not self._success:
            self._failed = True

        return self.observe()

    def is_terminal(self) -> bool:
        return self._success or self._failed

    def is_success(self) -> bool:
        return self._success
