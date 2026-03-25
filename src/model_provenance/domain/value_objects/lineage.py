from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class Lineage:
    """The ancestor subgraph of an Artifact induced by repeated
    parent-child derivations.
    """

    target_artifact_id: uuid.UUID
    ancestor_artifact_ids: tuple[uuid.UUID, ...]
    derivation_ids: tuple[uuid.UUID, ...]
