"""Run — a named, contiguous traversal through the Artifact DAG."""

from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class Run:
    """A named contiguous path through the training provenance graph.

    Consists of a starting Artifact, an ordered sequence of Derivations,
    and the Artifacts reached by those Derivations.
    """

    run_id: uuid.UUID
    name: str
    starting_artifact_id: uuid.UUID
    derivation_ids: tuple[uuid.UUID, ...]
    artifact_ids: tuple[uuid.UUID, ...]
