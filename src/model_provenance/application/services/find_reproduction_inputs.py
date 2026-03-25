"""Use case: Given an artifact, return the provenance chain needed to reproduce it."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from model_provenance.domain.repositories.provenance_repository import (
    ProvenanceRepository,
)
from model_provenance.domain.services.reproduction_service import ReproductionService


@dataclass(frozen=True)
class ReproductionStep:
    derivation_id: str
    parent_artifact_id: str
    child_artifact_id: str
    update_definition: dict[str, Any]
    training_input_descriptor: dict[str, Any]
    execution_record: dict[str, Any]


@dataclass(frozen=True)
class ReproductionView:
    target_artifact_id: str
    is_complete: bool
    initialization_rule: dict[str, Any] | None = None
    initialization_execution_record: dict[str, Any] | None = None
    root_specification: dict[str, Any] | None = None
    steps: list[ReproductionStep] = field(default_factory=list)


def find_reproduction_inputs(
    repo: ProvenanceRepository, artifact_id: uuid.UUID
) -> ReproductionView:
    service = ReproductionService(repo)
    chain = service.find_reproduction_chain(artifact_id)

    steps = [
        ReproductionStep(
            derivation_id=str(d.derivation_id),
            parent_artifact_id=str(d.parent_artifact_id),
            child_artifact_id=str(d.child_artifact_id),
            update_definition=d.update_definition.content,
            training_input_descriptor=d.training_input_descriptor.content,
            execution_record=d.execution_record.content,
        )
        for d in chain.derivations
    ]
    steps.reverse()

    init_rule: dict[str, Any] | None = None
    init_exec: dict[str, Any] | None = None
    root_spec: dict[str, Any] | None = None

    if chain.root_initialization is not None:
        init_rule = chain.root_initialization.initialization_rule.content
        init_exec = chain.root_initialization.execution_record.content
        root_artifact = repo.get_artifact(
            chain.root_initialization.child_artifact_id
        )
        if root_artifact is not None:
            root_spec = root_artifact.specification.content

    return ReproductionView(
        target_artifact_id=str(artifact_id),
        is_complete=chain.is_complete,
        initialization_rule=init_rule,
        initialization_execution_record=init_exec,
        root_specification=root_spec,
        steps=steps,
    )
