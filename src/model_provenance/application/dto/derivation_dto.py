from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DerivationDetailView:
    derivation_id: str
    parent_artifact_id: str
    child_artifact_id: str
    description: str
    update_definition: dict[str, Any] = field(default_factory=dict)
    training_input_descriptor: dict[str, Any] = field(default_factory=dict)
    execution_record: dict[str, Any] = field(default_factory=dict)
    parent_spec: dict[str, Any] = field(default_factory=dict)
    parent_training_state_summary: dict[str, Any] = field(default_factory=dict)
    child_spec: dict[str, Any] = field(default_factory=dict)
    child_training_state_summary: dict[str, Any] = field(default_factory=dict)
