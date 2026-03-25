from __future__ import annotations

import uuid
from datetime import datetime

from model_provenance.domain.entities.artifact import Artifact
from model_provenance.domain.entities.checkpoint import Checkpoint
from model_provenance.domain.entities.derivation import Derivation
from model_provenance.domain.entities.initialization import Initialization
from model_provenance.domain.entities.run import Run
from model_provenance.domain.repositories.provenance_repository import ProvenanceRepository
from model_provenance.domain.value_objects.execution_record import ExecutionRecord
from model_provenance.domain.value_objects.initialization_rule import InitializationRule
from model_provenance.domain.value_objects.specification import Specification
from model_provenance.domain.value_objects.training_input_descriptor import TrainingInputDescriptor
from model_provenance.domain.value_objects.training_state import TrainingState
from model_provenance.domain.value_objects.update_definition import UpdateDefinition


def _parse_uuid(value: str | uuid.UUID) -> uuid.UUID:
    if isinstance(value, uuid.UUID):
        return value
    return uuid.UUID(value)


def _parse_iso_datetime(value: str) -> datetime:
    s = value
    if s.endswith("Z"):
        s = f"{s[:-1]}+00:00"
    return datetime.fromisoformat(s)


class InMemoryProvenanceRepository(ProvenanceRepository):
    _artifacts: dict[uuid.UUID, Artifact]
    _derivations: dict[uuid.UUID, Derivation]
    _initializations: dict[uuid.UUID, Initialization]
    _checkpoints: dict[uuid.UUID, Checkpoint]
    _runs: dict[uuid.UUID, Run]

    def __init__(
        self,
        artifacts: dict[uuid.UUID, Artifact] | None = None,
        derivations: dict[uuid.UUID, Derivation] | None = None,
        initializations: dict[uuid.UUID, Initialization] | None = None,
        checkpoints: dict[uuid.UUID, Checkpoint] | None = None,
        runs: dict[uuid.UUID, Run] | None = None,
    ) -> None:
        self._artifacts = dict(artifacts or {})
        self._derivations = dict(derivations or {})
        self._initializations = dict(initializations or {})
        self._checkpoints = dict(checkpoints or {})
        self._runs = dict(runs or {})

    @classmethod
    def from_dict(cls, data: dict) -> InMemoryProvenanceRepository:
        artifacts: dict[uuid.UUID, Artifact] = {}
        for row in data.get("artifacts", []):
            aid = _parse_uuid(row["artifact_id"])
            spec = row.get("specification") or {}
            ts = row.get("training_state") or {}
            artifacts[aid] = Artifact(
                artifact_id=aid,
                specification=Specification(content=dict(spec)),
                training_state=TrainingState(content=dict(ts)),
            )

        derivations: dict[uuid.UUID, Derivation] = {}
        for row in data.get("derivations", []):
            did = _parse_uuid(row["derivation_id"])
            derivations[did] = Derivation(
                derivation_id=did,
                parent_artifact_id=_parse_uuid(row["parent_artifact_id"]),
                child_artifact_id=_parse_uuid(row["child_artifact_id"]),
                update_definition=UpdateDefinition(content=dict(row.get("update_definition") or {})),
                training_input_descriptor=TrainingInputDescriptor(
                    content=dict(row.get("training_input_descriptor") or {})
                ),
                execution_record=ExecutionRecord(content=dict(row.get("execution_record") or {})),
            )

        initializations: dict[uuid.UUID, Initialization] = {}
        for row in data.get("initializations", []):
            iid = _parse_uuid(row["initialization_id"])
            initializations[iid] = Initialization(
                initialization_id=iid,
                child_artifact_id=_parse_uuid(row["child_artifact_id"]),
                initialization_rule=InitializationRule(
                    content=dict(row.get("initialization_rule") or {})
                ),
                execution_record=ExecutionRecord(content=dict(row.get("execution_record") or {})),
            )

        checkpoints: dict[uuid.UUID, Checkpoint] = {}
        for row in data.get("checkpoints", []):
            cid = _parse_uuid(row["checkpoint_id"])
            handle = row.get("handle")
            checkpoints[cid] = Checkpoint(
                checkpoint_id=cid,
                artifact_id=_parse_uuid(row["artifact_id"]),
                created_at=_parse_iso_datetime(row["created_at"]),
                handle=None if handle is None else str(handle),
            )

        runs: dict[uuid.UUID, Run] = {}
        for row in data.get("runs", []):
            rid = _parse_uuid(row["run_id"])
            d_ids = tuple(_parse_uuid(x) for x in row.get("derivation_ids") or [])
            a_ids = tuple(_parse_uuid(x) for x in row.get("artifact_ids") or [])
            runs[rid] = Run(
                run_id=rid,
                name=str(row["name"]),
                starting_artifact_id=_parse_uuid(row["starting_artifact_id"]),
                derivation_ids=d_ids,
                artifact_ids=a_ids,
            )

        return cls(
            artifacts=artifacts,
            derivations=derivations,
            initializations=initializations,
            checkpoints=checkpoints,
            runs=runs,
        )

    def get_artifact(self, artifact_id: uuid.UUID) -> Artifact | None:
        return self._artifacts.get(artifact_id)

    def get_all_artifacts(self) -> list[Artifact]:
        return [self._artifacts[k] for k in sorted(self._artifacts, key=lambda u: u.bytes)]

    def get_derivation(self, derivation_id: uuid.UUID) -> Derivation | None:
        return self._derivations.get(derivation_id)

    def get_all_derivations(self) -> list[Derivation]:
        return [self._derivations[k] for k in sorted(self._derivations, key=lambda u: u.bytes)]

    def get_derivation_by_child(self, child_artifact_id: uuid.UUID) -> Derivation | None:
        matches = [d for d in self._derivations.values() if d.child_artifact_id == child_artifact_id]
        if not matches:
            return None
        matches.sort(key=lambda d: d.derivation_id.bytes)
        return matches[0]

    def get_derivations_by_parent(self, parent_artifact_id: uuid.UUID) -> list[Derivation]:
        out = [d for d in self._derivations.values() if d.parent_artifact_id == parent_artifact_id]
        out.sort(key=lambda d: d.derivation_id.bytes)
        return out

    def get_initialization_by_child(self, child_artifact_id: uuid.UUID) -> Initialization | None:
        matches = [
            i for i in self._initializations.values() if i.child_artifact_id == child_artifact_id
        ]
        if not matches:
            return None
        matches.sort(key=lambda i: i.initialization_id.bytes)
        return matches[0]

    def get_all_initializations(self) -> list[Initialization]:
        return [
            self._initializations[k]
            for k in sorted(self._initializations, key=lambda u: u.bytes)
        ]

    def get_checkpoint(self, checkpoint_id: uuid.UUID) -> Checkpoint | None:
        return self._checkpoints.get(checkpoint_id)

    def get_all_checkpoints(self) -> list[Checkpoint]:
        return [self._checkpoints[k] for k in sorted(self._checkpoints, key=lambda u: u.bytes)]

    def get_checkpoints_for_artifact(self, artifact_id: uuid.UUID) -> list[Checkpoint]:
        out = [c for c in self._checkpoints.values() if c.artifact_id == artifact_id]
        out.sort(key=lambda c: (c.created_at, c.checkpoint_id.bytes))
        return out

    def get_run(self, run_id: uuid.UUID) -> Run | None:
        return self._runs.get(run_id)

    def get_all_runs(self) -> list[Run]:
        return [self._runs[k] for k in sorted(self._runs, key=lambda u: u.bytes)]
