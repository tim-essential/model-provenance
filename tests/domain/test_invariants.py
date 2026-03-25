"""Tests for domain invariants: acyclicity, single-parent, root correctness."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from model_provenance.domain.entities.artifact import Artifact
from model_provenance.domain.entities.checkpoint import Checkpoint
from model_provenance.domain.entities.derivation import Derivation
from model_provenance.domain.entities.initialization import Initialization
from model_provenance.domain.exceptions import (
    CycleDetectedError,
    DuplicateDerivationError,
)
from model_provenance.domain.services.lineage_service import LineageService
from model_provenance.domain.services.provenance_service import ProvenanceService
from model_provenance.domain.services.reproduction_service import ReproductionService
from model_provenance.domain.value_objects import (
    ExecutionRecord,
    InitializationRule,
    Specification,
    TrainingInputDescriptor,
    TrainingState,
    UpdateDefinition,
)
from model_provenance.infrastructure.repositories.json_provenance_repository import (
    InMemoryProvenanceRepository,
)


def _art(n: int) -> uuid.UUID:
    return uuid.UUID(f"00000000-0000-0000-0000-{n:012d}")


def _der(n: int) -> uuid.UUID:
    return uuid.UUID(f"11111111-1111-1111-1111-{n:012d}")


def _make_artifact(n: int) -> Artifact:
    return Artifact(
        artifact_id=_art(n),
        specification=Specification(content={"n": n}),
        training_state=TrainingState(content={"step": n}),
    )


def _make_derivation(n: int, parent_n: int, child_n: int) -> Derivation:
    return Derivation(
        derivation_id=_der(n),
        parent_artifact_id=_art(parent_n),
        child_artifact_id=_art(child_n),
        update_definition=UpdateDefinition(content={"algo": "sgd"}),
        training_input_descriptor=TrainingInputDescriptor(content={"ds": "pile"}),
        execution_record=ExecutionRecord(content={}),
    )


class TestAcyclicity:
    def test_linear_chain_is_acyclic(self):
        arts = {_art(i): _make_artifact(i) for i in range(1, 4)}
        derivs = {
            _der(1): _make_derivation(1, 1, 2),
            _der(2): _make_derivation(2, 2, 3),
        }
        init_id = uuid.uuid4()
        inits = {
            init_id: Initialization(
                initialization_id=init_id,
                child_artifact_id=_art(1),
                initialization_rule=InitializationRule(content={}),
                execution_record=ExecutionRecord(content={}),
            )
        }
        repo = InMemoryProvenanceRepository(
            artifacts=arts, derivations=derivs, initializations=inits
        )
        prov = ProvenanceService(repo)
        prov.validate_acyclicity()

    def test_cycle_detected(self):
        arts = {_art(i): _make_artifact(i) for i in range(1, 4)}
        derivs = {
            _der(1): _make_derivation(1, 1, 2),
            _der(2): _make_derivation(2, 2, 3),
            _der(3): _make_derivation(3, 3, 1),
        }
        repo = InMemoryProvenanceRepository(artifacts=arts, derivations=derivs)
        prov = ProvenanceService(repo)
        with pytest.raises(CycleDetectedError):
            prov.validate_acyclicity()


class TestSingleParent:
    def test_single_parent_valid(self):
        arts = {_art(i): _make_artifact(i) for i in range(1, 4)}
        derivs = {
            _der(1): _make_derivation(1, 1, 2),
            _der(2): _make_derivation(2, 1, 3),
        }
        repo = InMemoryProvenanceRepository(artifacts=arts, derivations=derivs)
        prov = ProvenanceService(repo)
        prov.validate_single_parent()

    def test_duplicate_parent_detected(self):
        arts = {_art(i): _make_artifact(i) for i in range(1, 4)}
        derivs = {
            _der(1): _make_derivation(1, 1, 2),
            _der(2): _make_derivation(2, 3, 2),
        }
        repo = InMemoryProvenanceRepository(artifacts=arts, derivations=derivs)
        prov = ProvenanceService(repo)
        with pytest.raises(DuplicateDerivationError):
            prov.validate_single_parent()


class TestRootCorrectness:
    def test_root_identified_by_initialization(self):
        arts = {_art(1): _make_artifact(1)}
        init_id = uuid.uuid4()
        inits = {
            init_id: Initialization(
                initialization_id=init_id,
                child_artifact_id=_art(1),
                initialization_rule=InitializationRule(content={}),
                execution_record=ExecutionRecord(content={}),
            )
        }
        repo = InMemoryProvenanceRepository(
            artifacts=arts, initializations=inits
        )
        prov = ProvenanceService(repo)
        roots = prov.get_root_artifact_ids()
        assert roots == [_art(1)]


class TestLineage:
    def test_lineage_of_leaf(self):
        arts = {_art(i): _make_artifact(i) for i in range(1, 4)}
        derivs = {
            _der(1): _make_derivation(1, 1, 2),
            _der(2): _make_derivation(2, 2, 3),
        }
        repo = InMemoryProvenanceRepository(artifacts=arts, derivations=derivs)
        svc = LineageService(repo)
        lin = svc.compute_lineage(_art(3))
        assert _art(2) in lin.ancestor_artifact_ids
        assert _art(1) in lin.ancestor_artifact_ids

    def test_lineage_of_root(self):
        arts = {_art(1): _make_artifact(1)}
        repo = InMemoryProvenanceRepository(artifacts=arts)
        svc = LineageService(repo)
        lin = svc.compute_lineage(_art(1))
        assert len(lin.ancestor_artifact_ids) == 0


class TestReproduction:
    def test_reproduction_chain_complete(self):
        arts = {_art(i): _make_artifact(i) for i in range(1, 4)}
        derivs = {
            _der(1): _make_derivation(1, 1, 2),
            _der(2): _make_derivation(2, 2, 3),
        }
        init_id = uuid.uuid4()
        inits = {
            init_id: Initialization(
                initialization_id=init_id,
                child_artifact_id=_art(1),
                initialization_rule=InitializationRule(content={"method": "zeros"}),
                execution_record=ExecutionRecord(content={}),
            )
        }
        repo = InMemoryProvenanceRepository(
            artifacts=arts, derivations=derivs, initializations=inits
        )
        svc = ReproductionService(repo)
        chain = svc.find_reproduction_chain(_art(3))
        assert chain.is_complete
        assert len(chain.derivations) == 2
        assert chain.root_initialization is not None

    def test_reproduction_chain_incomplete_without_init(self):
        arts = {_art(i): _make_artifact(i) for i in range(1, 3)}
        derivs = {_der(1): _make_derivation(1, 1, 2)}
        repo = InMemoryProvenanceRepository(artifacts=arts, derivations=derivs)
        svc = ReproductionService(repo)
        chain = svc.find_reproduction_chain(_art(2))
        assert not chain.is_complete
