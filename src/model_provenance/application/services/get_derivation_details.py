"""Use case: Get full details for a derivation (edge)."""

from __future__ import annotations

import uuid

from model_provenance.application.dto.derivation_dto import DerivationDetailView
from model_provenance.application.services.summarize_derivation import (
    summarize_derivation,
)
from model_provenance.domain.repositories.provenance_repository import (
    ProvenanceRepository,
)


def get_derivation_details(
    repo: ProvenanceRepository, derivation_id: uuid.UUID
) -> DerivationDetailView | None:
    deriv = repo.get_derivation(derivation_id)
    if deriv is None:
        return None

    parent = repo.get_artifact(deriv.parent_artifact_id)
    child = repo.get_artifact(deriv.child_artifact_id)

    return DerivationDetailView(
        derivation_id=str(deriv.derivation_id),
        parent_artifact_id=str(deriv.parent_artifact_id),
        child_artifact_id=str(deriv.child_artifact_id),
        description=summarize_derivation(repo, deriv.derivation_id),
        update_definition=deriv.update_definition.content,
        training_input_descriptor=deriv.training_input_descriptor.content,
        execution_record=deriv.execution_record.content,
        parent_spec=parent.specification.content if parent else {},
        parent_training_state_summary=parent.training_state.content if parent else {},
        child_spec=child.specification.content if child else {},
        child_training_state_summary=child.training_state.content if child else {},
    )


def get_derivation_details_by_edge(
    repo: ProvenanceRepository,
    parent_artifact_id: uuid.UUID,
    child_artifact_id: uuid.UUID,
) -> DerivationDetailView | None:
    """Look up a derivation by its parent->child pair."""
    derivations = repo.get_derivations_by_parent(parent_artifact_id)
    for d in derivations:
        if d.child_artifact_id == child_artifact_id:
            return get_derivation_details(repo, d.derivation_id)
    return None
