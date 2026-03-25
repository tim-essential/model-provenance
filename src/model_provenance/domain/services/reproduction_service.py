"""Domain service for computing reproduction chains."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from model_provenance.domain.entities.derivation import Derivation
from model_provenance.domain.entities.initialization import Initialization
from model_provenance.domain.exceptions import ArtifactNotFoundError
from model_provenance.domain.repositories.provenance_repository import (
    ProvenanceRepository,
)


@dataclass(frozen=True)
class ReproductionChain:
    """The full provenance chain required to reproduce an artifact."""

    target_artifact_id: uuid.UUID
    derivations: tuple[Derivation, ...]
    root_initialization: Initialization | None

    @property
    def is_complete(self) -> bool:
        return self.root_initialization is not None


class ReproductionService:
    """Computes the full provenance chain needed to reproduce an artifact."""

    def __init__(self, repo: ProvenanceRepository) -> None:
        self._repo = repo

    def find_reproduction_chain(self, artifact_id: uuid.UUID) -> ReproductionChain:
        if self._repo.get_artifact(artifact_id) is None:
            raise ArtifactNotFoundError(artifact_id)

        derivations: list[Derivation] = []
        current_id = artifact_id

        while True:
            deriv = self._repo.get_derivation_by_child(current_id)
            if deriv is None:
                break
            derivations.append(deriv)
            current_id = deriv.parent_artifact_id

        root_init = self._repo.get_initialization_by_child(current_id)

        return ReproductionChain(
            target_artifact_id=artifact_id,
            derivations=tuple(derivations),
            root_initialization=root_init,
        )
