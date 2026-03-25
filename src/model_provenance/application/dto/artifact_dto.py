from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DerivationSummary:
    derivation_id: str
    parent_artifact_id: str
    update_definition: dict[str, Any]
    training_input_descriptor: dict[str, Any]
    execution_record: dict[str, Any]
    description: str


@dataclass(frozen=True)
class CheckpointSummary:
    checkpoint_id: str
    created_at: str
    handle: str | None


@dataclass(frozen=True)
class ArtifactDetailView:
    artifact_id: str
    specification: dict[str, Any]
    training_state: dict[str, Any]
    is_root: bool
    incoming_derivation: DerivationSummary | None
    initialization_summary: str | None
    checkpoints: list[CheckpointSummary] = field(default_factory=list)
    run_names: list[str] = field(default_factory=list)
