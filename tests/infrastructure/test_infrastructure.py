from __future__ import annotations

import json
import uuid
from pathlib import Path

from model_provenance.infrastructure.graph.graph_projection import project_graph, project_subgraph
from model_provenance.infrastructure.graph.layout import compute_layers
from model_provenance.infrastructure.repositories.json_provenance_repository import (
    InMemoryProvenanceRepository,
)
from model_provenance.infrastructure.serializers.json_loader import load_provenance_file


def _minimal_fixture(
    root_id: uuid.UUID,
    child_id: uuid.UUID,
    deriv_id: uuid.UUID,
    init_id: uuid.UUID,
    cp_id: uuid.UUID,
    run_id: uuid.UUID,
) -> dict:
    return {
        "artifacts": [
            {
                "artifact_id": str(root_id),
                "specification": {"a": 1},
                "training_state": {"s": 0},
            },
            {
                "artifact_id": str(child_id),
                "specification": {"a": 2},
                "training_state": {"s": 1},
            },
        ],
        "derivations": [
            {
                "derivation_id": str(deriv_id),
                "parent_artifact_id": str(root_id),
                "child_artifact_id": str(child_id),
                "update_definition": {"u": 1},
                "training_input_descriptor": {"t": 1},
                "execution_record": {"e": 1},
            }
        ],
        "initializations": [
            {
                "initialization_id": str(init_id),
                "child_artifact_id": str(root_id),
                "initialization_rule": {"r": 1},
                "execution_record": {"e": 0},
            }
        ],
        "checkpoints": [
            {
                "checkpoint_id": str(cp_id),
                "artifact_id": str(child_id),
                "created_at": "2024-01-15T12:00:00Z",
                "handle": "gs://bucket/cp",
            }
        ],
        "runs": [
            {
                "run_id": str(run_id),
                "name": "run-a",
                "starting_artifact_id": str(root_id),
                "derivation_ids": [str(deriv_id)],
                "artifact_ids": [str(root_id), str(child_id)],
            }
        ],
    }


class TestInMemoryProvenanceRepositoryFromDict:
    def test_round_trip_fixture(self) -> None:
        root_id = uuid.uuid4()
        child_id = uuid.uuid4()
        deriv_id = uuid.uuid4()
        init_id = uuid.uuid4()
        cp_id = uuid.uuid4()
        run_id = uuid.uuid4()
        data = _minimal_fixture(root_id, child_id, deriv_id, init_id, cp_id, run_id)
        repo = InMemoryProvenanceRepository.from_dict(data)

        root = repo.get_artifact(root_id)
        assert root is not None
        assert root.specification.content == {"a": 1}

        d = repo.get_derivation(deriv_id)
        assert d is not None
        assert d.parent_artifact_id == root_id
        assert d.child_artifact_id == child_id

        assert repo.get_derivation_by_child(child_id) == d
        assert repo.get_derivations_by_parent(root_id) == [d]

        init = repo.get_initialization_by_child(root_id)
        assert init is not None
        assert init.initialization_id == init_id

        cp = repo.get_checkpoint(cp_id)
        assert cp is not None
        assert cp.handle == "gs://bucket/cp"
        assert cp.created_at.year == 2024

        r = repo.get_run(run_id)
        assert r is not None
        assert r.name == "run-a"
        assert r.derivation_ids == (deriv_id,)
        assert r.artifact_ids == (root_id, child_id)


class TestLoadProvenanceFile:
    def test_loads_json(self, tmp_path: Path) -> None:
        p = tmp_path / "p.json"
        payload = {"artifacts": [], "runs": []}
        p.write_text(json.dumps(payload), encoding="utf-8")
        assert load_provenance_file(p) == payload


class TestProjectGraph:
    def test_kinds_and_edges(self) -> None:
        root_id = uuid.uuid4()
        child_id = uuid.uuid4()
        deriv_id = uuid.uuid4()
        init_id = uuid.uuid4()
        cp_id = uuid.uuid4()
        run_id = uuid.uuid4()
        data = _minimal_fixture(root_id, child_id, deriv_id, init_id, cp_id, run_id)
        repo = InMemoryProvenanceRepository.from_dict(data)
        g = project_graph(repo)
        kinds = {n.id: n.kind for n in g.nodes}
        assert kinds[str(root_id)] == "root"
        assert kinds[str(child_id)] == "checkpoint_artifact"
        assert len(g.edges) == 1
        assert g.edges[0].source == str(root_id)
        assert g.edges[0].target == str(child_id)

    def test_subgraph_filters(self) -> None:
        root_id = uuid.uuid4()
        child_id = uuid.uuid4()
        deriv_id = uuid.uuid4()
        init_id = uuid.uuid4()
        cp_id = uuid.uuid4()
        run_id = uuid.uuid4()
        data = _minimal_fixture(root_id, child_id, deriv_id, init_id, cp_id, run_id)
        repo = InMemoryProvenanceRepository.from_dict(data)
        sg = project_subgraph(repo, {root_id})
        assert len(sg.nodes) == 1
        assert sg.edges == []


class TestComputeLayers:
    def test_chain_increases_layer(self) -> None:
        a = uuid.uuid4()
        b = uuid.uuid4()
        c = uuid.uuid4()
        from model_provenance.infrastructure.graph.graph_projection import (
            GraphEdge,
            GraphNode,
            ProjectedGraph,
        )

        g = ProjectedGraph(
            nodes=[
                GraphNode(id=str(a), label=str(a), kind="artifact", metadata={}),
                GraphNode(id=str(b), label=str(b), kind="artifact", metadata={}),
                GraphNode(id=str(c), label=str(c), kind="artifact", metadata={}),
            ],
            edges=[
                GraphEdge(source=str(a), target=str(b), label="derivation", metadata={}),
                GraphEdge(source=str(b), target=str(c), label="derivation", metadata={}),
            ],
        )
        layers = compute_layers(g)
        assert layers[str(a)] == 0
        assert layers[str(b)] == 1
        assert layers[str(c)] == 2
