"""Use case: Get full inspectable details for a selected artifact."""

from __future__ import annotations

import uuid

from model_provenance.application.dto.artifact_dto import (
    ArtifactDetailView,
    CheckpointSummary,
    DerivationSummary,
)
from model_provenance.application.services.summarize_derivation import (
    summarize_derivation,
)
from model_provenance.domain.exceptions import ArtifactNotFoundError
from model_provenance.domain.repositories.provenance_repository import (
    ProvenanceRepository,
)


def get_artifact_details(
    repo: ProvenanceRepository, artifact_id: uuid.UUID
) -> ArtifactDetailView:
    artifact = repo.get_artifact(artifact_id)
    if artifact is None:
        raise ArtifactNotFoundError(artifact_id)

    deriv = repo.get_derivation_by_child(artifact_id)
    init = repo.get_initialization_by_child(artifact_id)

    incoming: DerivationSummary | None = None
    if deriv is not None:
        incoming = DerivationSummary(
            derivation_id=str(deriv.derivation_id),
            parent_artifact_id=str(deriv.parent_artifact_id),
            update_definition=deriv.update_definition.content,
            training_input_descriptor=deriv.training_input_descriptor.content,
            execution_record=deriv.execution_record.content,
            description=summarize_derivation(repo, deriv.derivation_id),
        )

    init_summary: str | None = None
    if init is not None:
        rule = init.initialization_rule.content
        method = rule.get("method", "unknown")
        init_summary = f"Initialized via {method}"

    checkpoints = repo.get_checkpoints_for_artifact(artifact_id)
    ckpt_summaries = [
        CheckpointSummary(
            checkpoint_id=str(c.checkpoint_id),
            created_at=c.created_at.isoformat(),
            handle=c.handle,
        )
        for c in checkpoints
    ]

    run_names: list[str] = []
    for run in repo.get_all_runs():
        if artifact_id in run.artifact_ids:
            run_names.append(run.name)

    return ArtifactDetailView(
        artifact_id=str(artifact_id),
        specification=artifact.specification.content,
        training_state=artifact.training_state.content,
        is_root=init is not None,
        incoming_derivation=incoming,
        initialization_summary=init_summary,
        checkpoints=ckpt_summaries,
        run_names=run_names,
    )
