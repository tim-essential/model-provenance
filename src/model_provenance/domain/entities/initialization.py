"""Initialization — a root-producing derivation with no parent."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from model_provenance.domain.value_objects.execution_record import ExecutionRecord
from model_provenance.domain.value_objects.initialization_rule import InitializationRule


@dataclass(frozen=True)
class Initialization:
    """A special derivation with no parent Artifact that produces a root
    Artifact.

    Formally:  Initialization : (Specification, InitializationRule) -> Artifact
    """

    initialization_id: uuid.UUID
    child_artifact_id: uuid.UUID
    initialization_rule: InitializationRule
    execution_record: ExecutionRecord
