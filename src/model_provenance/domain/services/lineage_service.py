"""Domain service for computing artifact lineage."""

from __future__ import annotations

import uuid

from model_provenance.domain.exceptions import ArtifactNotFoundError
from model_provenance.domain.repositories.provenance_repository import (
    ProvenanceRepository,
)
from model_provenance.domain.value_objects.lineage import Lineage


class LineageService:
    """Computes lineage (ancestor subgraph) for an artifact."""

    def __init__(self, repo: ProvenanceRepository) -> None:
        self._repo = repo

    def compute_lineage(self, artifact_id: uuid.UUID) -> Lineage:
        if self._repo.get_artifact(artifact_id) is None:
            raise ArtifactNotFoundError(artifact_id)

        ancestors: list[uuid.UUID] = []
        derivation_ids: list[uuid.UUID] = []
        current_id = artifact_id

        while True:
            deriv = self._repo.get_derivation_by_child(current_id)
            if deriv is None:
                break
            derivation_ids.append(deriv.derivation_id)
            ancestors.append(deriv.parent_artifact_id)
            current_id = deriv.parent_artifact_id

        return Lineage(
            target_artifact_id=artifact_id,
            ancestor_artifact_ids=tuple(ancestors),
            derivation_ids=tuple(derivation_ids),
        )
