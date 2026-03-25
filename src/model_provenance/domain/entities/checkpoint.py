"""Checkpoint — a persisted, addressable snapshot of an Artifact."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Checkpoint:
    """A persisted, addressable snapshot of an Artifact.

    Many runs can branch from the same Checkpoint because many
    Derivations can name the same underlying Artifact as parent.
    """

    checkpoint_id: uuid.UUID
    artifact_id: uuid.UUID
    created_at: datetime
    handle: str | None = None
