"""Use case: Get the ordered path/subgraph for a selected run."""

from __future__ import annotations

import uuid

from model_provenance.application.dto.run_dto import RunView
from model_provenance.domain.repositories.provenance_repository import (
    ProvenanceRepository,
)


def get_run_view(repo: ProvenanceRepository, run_id: uuid.UUID) -> RunView | None:
    run = repo.get_run(run_id)
    if run is None:
        return None

    return RunView(
        run_id=str(run.run_id),
        name=run.name,
        starting_artifact_id=str(run.starting_artifact_id),
        artifact_ids=[str(a) for a in run.artifact_ids],
        derivation_ids=[str(d) for d in run.derivation_ids],
    )
