"""Artifact — the canonical node in the training provenance DAG."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from model_provenance.domain.value_objects.specification import Specification
from model_provenance.domain.value_objects.training_state import TrainingState


@dataclass(frozen=True)
class Artifact:
    """A fully specified training-time model object.

    Two Artifacts are distinct if either their Specification or
    Training State differs.  Identity is carried by ``artifact_id``.
    """

    artifact_id: uuid.UUID
    specification: Specification
    training_state: TrainingState
