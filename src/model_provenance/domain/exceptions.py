"""Domain exceptions for provenance invariant violations."""

from __future__ import annotations

import uuid


class DomainError(Exception):
    """Base for all domain errors."""


class CycleDetectedError(DomainError):
    """The provenance graph would contain a cycle."""

    def __init__(self, artifact_id: uuid.UUID) -> None:
        super().__init__(f"Cycle detected involving artifact {artifact_id}")
        self.artifact_id = artifact_id


class DuplicateDerivationError(DomainError):
    """A non-root artifact already has an incoming derivation."""

    def __init__(self, artifact_id: uuid.UUID) -> None:
        super().__init__(
            f"Artifact {artifact_id} already has an incoming derivation"
        )
        self.artifact_id = artifact_id


class ArtifactNotFoundError(DomainError):
    """Referenced artifact does not exist in the graph."""

    def __init__(self, artifact_id: uuid.UUID) -> None:
        super().__init__(f"Artifact {artifact_id} not found")
        self.artifact_id = artifact_id


class DerivationNotFoundError(DomainError):
    """Referenced derivation does not exist in the graph."""

    def __init__(self, derivation_id: uuid.UUID) -> None:
        super().__init__(f"Derivation {derivation_id} not found")
        self.derivation_id = derivation_id
