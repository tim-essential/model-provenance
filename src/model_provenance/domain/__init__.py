"""model_provenance.domain — pure DDD domain model for ML training provenance.

The domain models training provenance as a DAG where:
  nodes = Artifacts
  edges = Derivations
  root nodes = Artifacts produced by Initializations
  named persisted nodes = Checkpoints
  highlighted paths = Runs
"""

from model_provenance.domain.entities import (
    Artifact,
    Checkpoint,
    Derivation,
    Initialization,
    Run,
)
from model_provenance.domain.value_objects import (
    Batch,
    ExecutionRecord,
    InitializationRule,
    Lineage,
    Specification,
    TrainingInput,
    TrainingInputDescriptor,
    TrainingState,
    UpdateDefinition,
)

__all__ = [
    "Artifact",
    "Batch",
    "Checkpoint",
    "Derivation",
    "ExecutionRecord",
    "Initialization",
    "InitializationRule",
    "Lineage",
    "Run",
    "Specification",
    "TrainingInput",
    "TrainingInputDescriptor",
    "TrainingState",
    "UpdateDefinition",
]
