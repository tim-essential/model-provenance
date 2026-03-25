"""Domain service for provenance graph invariant checking."""

from __future__ import annotations

import uuid

from model_provenance.domain.exceptions import (
    ArtifactNotFoundError,
    CycleDetectedError,
    DuplicateDerivationError,
)
from model_provenance.domain.repositories.provenance_repository import (
    ProvenanceRepository,
)


class ProvenanceService:
    """Validates provenance graph invariants."""

    def __init__(self, repo: ProvenanceRepository) -> None:
        self._repo = repo

    def validate_acyclicity(self) -> None:
        """Verify the provenance graph is acyclic."""
        derivations = self._repo.get_all_derivations()
        parent_map: dict[uuid.UUID, uuid.UUID] = {
            d.child_artifact_id: d.parent_artifact_id for d in derivations
        }

        for start_id in parent_map:
            visited: set[uuid.UUID] = set()
            current = start_id
            while current in parent_map:
                if current in visited:
                    raise CycleDetectedError(current)
                visited.add(current)
                current = parent_map[current]

    def validate_single_parent(self) -> None:
        """Every non-root artifact has at most one incoming derivation."""
        derivations = self._repo.get_all_derivations()
        seen_children: set[uuid.UUID] = set()
        for d in derivations:
            if d.child_artifact_id in seen_children:
                raise DuplicateDerivationError(d.child_artifact_id)
            seen_children.add(d.child_artifact_id)

    def get_root_artifact_ids(self) -> list[uuid.UUID]:
        """Return artifact ids that have no incoming derivation (roots)."""
        inits = self._repo.get_all_initializations()
        return [i.child_artifact_id for i in inits]

    def get_descendant_artifact_ids(self, artifact_id: uuid.UUID) -> list[uuid.UUID]:
        """Return all descendant artifact ids (BFS)."""
        if self._repo.get_artifact(artifact_id) is None:
            raise ArtifactNotFoundError(artifact_id)

        descendants: list[uuid.UUID] = []
        queue = [artifact_id]
        visited: set[uuid.UUID] = set()

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            children = self._repo.get_derivations_by_parent(current)
            for d in children:
                descendants.append(d.child_artifact_id)
                queue.append(d.child_artifact_id)

        return descendants
