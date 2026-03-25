"""Repository interface for provenance data.

This is a domain-layer port.  Concrete implementations belong in
the infrastructure layer.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from model_provenance.domain.entities.artifact import Artifact
from model_provenance.domain.entities.checkpoint import Checkpoint
from model_provenance.domain.entities.derivation import Derivation
from model_provenance.domain.entities.initialization import Initialization
from model_provenance.domain.entities.run import Run


class ProvenanceRepository(ABC):
    """Abstract repository for loading/saving provenance data."""

    @abstractmethod
    def get_artifact(self, artifact_id: uuid.UUID) -> Artifact | None: ...

    @abstractmethod
    def get_all_artifacts(self) -> list[Artifact]: ...

    @abstractmethod
    def get_derivation(self, derivation_id: uuid.UUID) -> Derivation | None: ...

    @abstractmethod
    def get_all_derivations(self) -> list[Derivation]: ...

    @abstractmethod
    def get_derivation_by_child(self, child_artifact_id: uuid.UUID) -> Derivation | None: ...

    @abstractmethod
    def get_derivations_by_parent(self, parent_artifact_id: uuid.UUID) -> list[Derivation]: ...

    @abstractmethod
    def get_initialization_by_child(self, child_artifact_id: uuid.UUID) -> Initialization | None: ...

    @abstractmethod
    def get_all_initializations(self) -> list[Initialization]: ...

    @abstractmethod
    def get_checkpoint(self, checkpoint_id: uuid.UUID) -> Checkpoint | None: ...

    @abstractmethod
    def get_all_checkpoints(self) -> list[Checkpoint]: ...

    @abstractmethod
    def get_checkpoints_for_artifact(self, artifact_id: uuid.UUID) -> list[Checkpoint]: ...

    @abstractmethod
    def get_run(self, run_id: uuid.UUID) -> Run | None: ...

    @abstractmethod
    def get_all_runs(self) -> list[Run]: ...
