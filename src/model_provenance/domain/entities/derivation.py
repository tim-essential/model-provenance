"""Derivation — the canonical edge in the training provenance DAG."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from model_provenance.domain.entities.artifact import Artifact
from model_provenance.domain.value_objects.execution_record import ExecutionRecord
from model_provenance.domain.value_objects.specification import Specification
from model_provenance.domain.value_objects.training_input_descriptor import (
    TrainingInputDescriptor,
)
from model_provenance.domain.value_objects.training_state import TrainingState
from model_provenance.domain.value_objects.update_definition import UpdateDefinition


@dataclass(frozen=True)
class Derivation:
    """A provenance record describing the pure production of one Artifact
    from another.

    Links one parent Artifact to one child Artifact, together with the
    Update Definition, Training Input Descriptor, and Execution Record
    that fully describe how the child came to be.
    """

    derivation_id: uuid.UUID
    parent_artifact_id: uuid.UUID
    child_artifact_id: uuid.UUID
    update_definition: UpdateDefinition
    training_input_descriptor: TrainingInputDescriptor
    execution_record: ExecutionRecord
