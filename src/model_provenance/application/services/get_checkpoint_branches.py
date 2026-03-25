"""Use case: Given a checkpoint, show descendant runs/branches."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from model_provenance.application.dto.run_dto import RunView
from model_provenance.domain.repositories.provenance_repository import (
    ProvenanceRepository,
)
from model_provenance.domain.services.provenance_service import ProvenanceService


@dataclass(frozen=True)
class CheckpointBranchesView:
    checkpoint_id: str
    artifact_id: str
    descendant_artifact_ids: list[str] = field(default_factory=list)
    runs: list[RunView] = field(default_factory=list)


def get_checkpoint_branches(
    repo: ProvenanceRepository, checkpoint_id: uuid.UUID
) -> CheckpointBranchesView | None:
    ckpt = repo.get_checkpoint(checkpoint_id)
    if ckpt is None:
        return None

    prov = ProvenanceService(repo)
    descendants = prov.get_descendant_artifact_ids(ckpt.artifact_id)

    descendant_set = set(descendants) | {ckpt.artifact_id}
    runs: list[RunView] = []
    for run in repo.get_all_runs():
        if any(aid in descendant_set for aid in run.artifact_ids):
            runs.append(
                RunView(
                    run_id=str(run.run_id),
                    name=run.name,
                    starting_artifact_id=str(run.starting_artifact_id),
                    artifact_ids=[str(a) for a in run.artifact_ids],
                    derivation_ids=[str(d) for d in run.derivation_ids],
                )
            )

    return CheckpointBranchesView(
        checkpoint_id=str(ckpt.checkpoint_id),
        artifact_id=str(ckpt.artifact_id),
        descendant_artifact_ids=[str(d) for d in descendants],
        runs=runs,
    )
