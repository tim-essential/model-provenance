"""Tests for domain entities and value objects."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from model_provenance.domain.entities.artifact import Artifact
from model_provenance.domain.entities.checkpoint import Checkpoint
from model_provenance.domain.entities.derivation import Derivation
from model_provenance.domain.entities.initialization import Initialization
from model_provenance.domain.entities.run import Run
from model_provenance.domain.value_objects import (
    Batch,
    ExecutionRecord,
    InitializationRule,
    Specification,
    TrainingInput,
    TrainingInputDescriptor,
    TrainingState,
    UpdateDefinition,
)


class TestValueObjects:
    def test_specification_frozen(self):
        spec = Specification(content={"arch": "transformer"})
        with pytest.raises(Exception):
            spec.content = {}  # type: ignore[misc]

    def test_specification_equality(self):
        a = Specification(content={"arch": "transformer"})
        b = Specification(content={"arch": "transformer"})
        assert a == b
        assert a != Specification(content={"arch": "mlp"})

    def test_training_state_frozen(self):
        ts = TrainingState(content={"w": [0.1]})
        with pytest.raises(Exception):
            ts.content = {}  # type: ignore[misc]

    def test_batch_is_training_input(self):
        b = Batch(content={"tokens": [[1, 2]]})
        assert isinstance(b, TrainingInput)

    def test_update_definition_equality(self):
        a = UpdateDefinition(content={"algo": "adam"})
        b = UpdateDefinition(content={"algo": "adam"})
        assert a == b

    def test_training_input_descriptor_equality(self):
        a = TrainingInputDescriptor(content={"dataset": "pile"})
        b = TrainingInputDescriptor(content={"dataset": "pile"})
        assert a == b

    def test_execution_record_equality(self):
        a = ExecutionRecord(content={"gpu": "A100"})
        b = ExecutionRecord(content={"gpu": "A100"})
        assert a == b

    def test_initialization_rule_equality(self):
        a = InitializationRule(content={"method": "kaiming"})
        b = InitializationRule(content={"method": "kaiming"})
        assert a == b


class TestArtifact:
    def test_artifact_composition(self):
        aid = uuid.uuid4()
        spec = Specification(content={"arch": "transformer"})
        ts = TrainingState(content={"w": [0.0]})
        a = Artifact(artifact_id=aid, specification=spec, training_state=ts)
        assert a.artifact_id == aid
        assert a.specification == spec
        assert a.training_state == ts

    def test_artifact_frozen(self):
        a = Artifact(
            artifact_id=uuid.uuid4(),
            specification=Specification(content={}),
            training_state=TrainingState(content={}),
        )
        with pytest.raises(Exception):
            a.specification = Specification(content={})  # type: ignore[misc]

    def test_identity_by_id(self):
        aid = uuid.uuid4()
        a = Artifact(aid, Specification(content={}), TrainingState(content={}))
        b = Artifact(aid, Specification(content={}), TrainingState(content={}))
        assert a == b

    def test_different_ids_not_equal(self):
        a = Artifact(uuid.uuid4(), Specification(content={}), TrainingState(content={}))
        b = Artifact(uuid.uuid4(), Specification(content={}), TrainingState(content={}))
        assert a != b


class TestDerivation:
    def test_derivation_fields(self):
        d = Derivation(
            derivation_id=uuid.uuid4(),
            parent_artifact_id=uuid.uuid4(),
            child_artifact_id=uuid.uuid4(),
            update_definition=UpdateDefinition(content={"algo": "sgd"}),
            training_input_descriptor=TrainingInputDescriptor(content={"ds": "pile"}),
            execution_record=ExecutionRecord(content={"gpu": "A100"}),
        )
        assert d.parent_artifact_id != d.child_artifact_id

    def test_derivation_frozen(self):
        d = Derivation(
            derivation_id=uuid.uuid4(),
            parent_artifact_id=uuid.uuid4(),
            child_artifact_id=uuid.uuid4(),
            update_definition=UpdateDefinition(content={}),
            training_input_descriptor=TrainingInputDescriptor(content={}),
            execution_record=ExecutionRecord(content={}),
        )
        with pytest.raises(Exception):
            d.parent_artifact_id = uuid.uuid4()  # type: ignore[misc]


class TestInitialization:
    def test_initialization_fields(self):
        i = Initialization(
            initialization_id=uuid.uuid4(),
            child_artifact_id=uuid.uuid4(),
            initialization_rule=InitializationRule(content={"method": "zeros"}),
            execution_record=ExecutionRecord(content={}),
        )
        assert i.initialization_rule.content["method"] == "zeros"


class TestCheckpoint:
    def test_checkpoint_fields(self):
        c = Checkpoint(
            checkpoint_id=uuid.uuid4(),
            artifact_id=uuid.uuid4(),
            created_at=datetime.now(timezone.utc),
            handle="gs://bucket/ckpt",
        )
        assert c.handle == "gs://bucket/ckpt"

    def test_checkpoint_frozen(self):
        c = Checkpoint(
            checkpoint_id=uuid.uuid4(),
            artifact_id=uuid.uuid4(),
            created_at=datetime.now(timezone.utc),
        )
        with pytest.raises(Exception):
            c.artifact_id = uuid.uuid4()  # type: ignore[misc]


class TestRun:
    def test_run_fields(self):
        r = Run(
            run_id=uuid.uuid4(),
            name="pretrain-1",
            starting_artifact_id=uuid.uuid4(),
            derivation_ids=(uuid.uuid4(),),
            artifact_ids=(uuid.uuid4(), uuid.uuid4()),
        )
        assert r.name == "pretrain-1"
        assert len(r.artifact_ids) == 2
