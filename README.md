# model-provenance

Provenance visualization app for ML training artifacts.

Models training provenance as a rooted acyclic DAG using
DDD with strict separation between domain, application,
infrastructure, and presentation layers.


## Core transformation

```
Update : (Artifact, TrainingInput) -> Artifact'

where  Artifact = (Specification, TrainingState)
```

An Update is a pure function.  Nothing is mutated.


## The graph

```
nodes  = Artifacts
edges  = Derivations
roots  = Artifacts produced by Initializations
named  = Checkpoints (persisted snapshots)
paths  = Runs (contiguous traversals)
```


## Domain model

```
Initialization
  |  (no parent)
  v
+-------------------------------+
|  Artifact  (DAG node)         |
|  +-------------+ +---------+ |
|  |Specification| |Training | |
|  |             | |State    | |
|  +-------------+ +---------+ |
+-------------------------------+
  |                          |
  | Derivation               | Derivation
  |                          |
  | +--------------------+  |
  | | UpdateDefinition   |  |
  | | TrainingInput      |  |
  | |   Descriptor       |  |
  | | ExecutionRecord    |  |
  | +--------------------+  |
  v                          v
+----------------+   +----------------+
| Artifact'      |   | Artifact''     |
| (successor)    |   | (branch)       |
+----------------+   +----------------+
  |                          |
  v                          v
Checkpoint              Checkpoint

Run = one highlighted path through the DAG
Lineage = ancestor subgraph of an Artifact
```


## Architecture

```
+------------------+
| presentation/    |  Streamlit UI, viewmodels
+------------------+
        |
+------------------+
| application/     |  Use-case services, DTOs
+------------------+
        |
+------------------+
| domain/          |  Pure: entities, value objects,
|                  |  services, repository interfaces
+------------------+
        |
+------------------+
| infrastructure/  |  JSON repo, serializers,
|                  |  graph projection, layout
+------------------+
```

Dependencies flow inward only.  The domain layer has
no imports from application, infrastructure, or UI.


## Layer boundaries

| Layer          | Contains | Does NOT contain |
|----------------|----------|-----------------|
| Domain         | Entities, value objects, domain services, repo interfaces, exceptions | JSON, Streamlit, Graphviz, file I/O |
| Application    | Use-case orchestration, DTOs | Persistence impl, UI widgets |
| Infrastructure | InMemoryRepo, JSON loader, graph projection, layout | Domain logic, UI state |
| Presentation   | Streamlit app, viewmodels, components | Domain entities, persistence |


## Project layout

```
src/model_provenance/
  domain/
    entities/          Artifact, Derivation, Initialization,
                       Checkpoint, Run
    value_objects/     Specification, TrainingState,
                       UpdateDefinition, TrainingInputDescriptor,
                       ExecutionRecord, InitializationRule, Lineage
    services/          LineageService, ProvenanceService,
                       ReproductionService
    repositories/      ProvenanceRepository (ABC)
    exceptions.py

  application/
    dto/               ArtifactDetailView, GraphView, RunView
    services/          8 use-case services:
                         LoadProvenanceGraph
                         GetArtifactDetails
                         GetArtifactLineage
                         GetRunView
                         GetCheckpointBranches
                         FindReproductionInputs
                         FilterGraph
                         SummarizeDerivation

  infrastructure/
    repositories/      InMemoryProvenanceRepository
    serializers/       JSON loader
    graph/             GraphProjection, layout helpers

  presentation/
    streamlit_app/     Streamlit UI
      app.py           Main app entry point
      components/      Detail panel
      viewmodels/      Graphviz DOT builder

data/
  sample_provenance.json   Sample DAG fixture

tests/
  domain/             Entity, value object, invariant tests
  application/        Use-case integration tests
  infrastructure/     Repo, projection, layout tests
```


## Quickstart

```fish
uv sync
uv run pytest                 # 52 tests
uv run streamlit run \
  src/model_provenance/presentation/streamlit_app/app.py
```


## Sample DAG

The fixture in `data/sample_provenance.json` models:

```
art-1 (root, kaiming init)
  -> art-2 -> art-3 -> art-4 [ckpt] -> art-5 -> art-6 [ckpt]
                          |             (pretrain-run-1)
                          |
                          +-> art-7 -> art-8 -> art-9 [ckpt]
                          |         (finetune-run-1, dolly-15k)
                          |
                          +-> art-10 -> art-11 [ckpt]
                                    (finetune-run-2, oasst1)
```

Three runs, four checkpoints, branching from a shared
pretrain checkpoint at step 3.


## Adding new provenance data

Create a JSON file matching this schema:

```json
{
  "artifacts": [
    {"artifact_id": "uuid",
     "specification": {...},
     "training_state": {...}}
  ],
  "derivations": [
    {"derivation_id": "uuid",
     "parent_artifact_id": "uuid",
     "child_artifact_id": "uuid",
     "update_definition": {...},
     "training_input_descriptor": {...},
     "execution_record": {...}}
  ],
  "initializations": [
    {"initialization_id": "uuid",
     "child_artifact_id": "uuid",
     "initialization_rule": {...},
     "execution_record": {...}}
  ],
  "checkpoints": [
    {"checkpoint_id": "uuid",
     "artifact_id": "uuid",
     "created_at": "ISO8601",
     "handle": "gs://..."}
  ],
  "runs": [
    {"run_id": "uuid",
     "name": "run-name",
     "starting_artifact_id": "uuid",
     "derivation_ids": [...],
     "artifact_ids": [...]}
  ]
}
```

Point the Streamlit app at your file using the sidebar
text input.


## Domain invariants enforced

1. Every non-root Artifact has exactly one incoming
   Derivation
2. Every Derivation has exactly one parent and one child
3. Initialization has no parent, produces one root
4. The provenance graph must be acyclic
5. Artifact identity is explicit (UUID), not inferred
6. Checkpoint identity is distinct from Artifact identity
