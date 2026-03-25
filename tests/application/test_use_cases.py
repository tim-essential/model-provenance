"""Tests for application-layer use cases against the sample fixture."""

from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from model_provenance.application.services.load_provenance_graph import (
    load_provenance_graph,
)
from model_provenance.application.services.get_artifact_details import (
    get_artifact_details,
)
from model_provenance.application.services.get_artifact_lineage import (
    get_artifact_lineage,
)
from model_provenance.application.services.get_run_view import get_run_view
from model_provenance.application.services.get_checkpoint_branches import (
    get_checkpoint_branches,
)
from model_provenance.application.services.find_reproduction_inputs import (
    find_reproduction_inputs,
)
from model_provenance.application.services.filter_graph import (
    GraphFilter,
    filter_graph,
)
from model_provenance.application.services.summarize_derivation import (
    summarize_derivation,
)
from model_provenance.infrastructure.repositories.json_provenance_repository import (
    InMemoryProvenanceRepository,
)


FIXTURE = Path(__file__).resolve().parents[2] / "data" / "sample_provenance.json"

ART_1 = uuid.UUID("00000000-0000-0000-0000-000000000001")
ART_4 = uuid.UUID("00000000-0000-0000-0000-000000000004")
ART_6 = uuid.UUID("00000000-0000-0000-0000-000000000006")
ART_9 = uuid.UUID("00000000-0000-0000-0000-000000000009")
ART_11 = uuid.UUID("00000000-0000-0000-0000-000000000011")
DER_1 = uuid.UUID("11111111-1111-1111-1111-000000000001")
CKPT_1 = uuid.UUID("33333333-3333-3333-3333-000000000001")
RUN_PRETRAIN = uuid.UUID("44444444-4444-4444-4444-000000000001")
RUN_FT1 = uuid.UUID("44444444-4444-4444-4444-000000000002")
RUN_FT2 = uuid.UUID("44444444-4444-4444-4444-000000000003")


@pytest.fixture()
def repo_and_graph():
    return load_provenance_graph(FIXTURE)


@pytest.fixture()
def repo(repo_and_graph):
    return repo_and_graph[0]


@pytest.fixture()
def graph_view(repo_and_graph):
    return repo_and_graph[1]


class TestLoadProvenanceGraph:
    def test_loads_all_artifacts(self, repo: InMemoryProvenanceRepository):
        assert len(repo.get_all_artifacts()) == 11

    def test_loads_all_derivations(self, repo: InMemoryProvenanceRepository):
        assert len(repo.get_all_derivations()) == 10

    def test_graph_view_has_nodes_and_edges(self, graph_view):
        assert len(graph_view.nodes) == 11
        assert len(graph_view.edges) == 10

    def test_graph_view_root_node(self, graph_view):
        root_nodes = [n for n in graph_view.nodes if n.kind == "root"]
        assert len(root_nodes) == 1

    def test_graph_view_layers_increase(self, graph_view):
        layers = {n.id: n.layer for n in graph_view.nodes}
        root_id = str(ART_1)
        leaf_id = str(ART_6)
        assert layers[root_id] < layers[leaf_id]


class TestGetArtifactDetails:
    def test_root_artifact(self, repo):
        detail = get_artifact_details(repo, ART_1)
        assert detail.is_root
        assert detail.initialization_summary is not None
        assert "kaiming_normal" in detail.initialization_summary
        assert detail.incoming_derivation is None

    def test_derived_artifact(self, repo):
        detail = get_artifact_details(repo, ART_9)
        assert not detail.is_root
        assert detail.incoming_derivation is not None
        assert "dolly-15k" in detail.incoming_derivation.description

    def test_checkpointed_artifact(self, repo):
        detail = get_artifact_details(repo, ART_4)
        assert len(detail.checkpoints) >= 1

    def test_runs_containing_artifact(self, repo):
        detail = get_artifact_details(repo, ART_4)
        assert "pretrain-run-1" in detail.run_names


class TestGetArtifactLineage:
    def test_lineage_of_finetune_endpoint(self, repo):
        lineage_graph = get_artifact_lineage(repo, ART_9)
        node_ids = {n.id for n in lineage_graph.nodes}
        assert str(ART_9) in node_ids
        assert str(ART_4) in node_ids
        assert str(ART_1) in node_ids

    def test_root_lineage_is_just_itself(self, repo):
        lineage_graph = get_artifact_lineage(repo, ART_1)
        assert len(lineage_graph.nodes) == 1


class TestGetRunView:
    def test_pretrain_run(self, repo):
        view = get_run_view(repo, RUN_PRETRAIN)
        assert view is not None
        assert view.name == "pretrain-run-1"
        assert len(view.artifact_ids) == 6
        assert len(view.derivation_ids) == 5

    def test_finetune_run(self, repo):
        view = get_run_view(repo, RUN_FT1)
        assert view is not None
        assert view.name == "finetune-run-1"
        assert view.starting_artifact_id == str(ART_4)


class TestGetCheckpointBranches:
    def test_branch_point_checkpoint(self, repo):
        view = get_checkpoint_branches(repo, CKPT_1)
        assert view is not None
        assert len(view.descendant_artifact_ids) > 0
        run_names = {r.name for r in view.runs}
        assert "pretrain-run-1" in run_names
        assert "finetune-run-1" in run_names
        assert "finetune-run-2" in run_names


class TestFindReproductionInputs:
    def test_reproduction_of_finetune_artifact(self, repo):
        view = find_reproduction_inputs(repo, ART_9)
        assert view.is_complete
        assert view.initialization_rule is not None
        assert len(view.steps) > 0
        assert view.root_specification is not None

    def test_reproduction_of_root(self, repo):
        view = find_reproduction_inputs(repo, ART_1)
        assert view.is_complete
        assert len(view.steps) == 0


class TestFilterGraph:
    def test_filter_by_run(self, repo):
        filt = GraphFilter(run_id=RUN_FT1)
        view = filter_graph(repo, filt)
        node_ids = {n.id for n in view.nodes}
        assert str(ART_4) in node_ids
        assert str(ART_9) in node_ids
        assert str(ART_6) not in node_ids

    def test_filter_by_artifact_ids(self, repo):
        filt = GraphFilter(artifact_ids={ART_1, ART_4})
        view = filter_graph(repo, filt)
        assert len(view.nodes) == 2

    def test_empty_filter_returns_all(self, repo):
        filt = GraphFilter()
        view = filter_graph(repo, filt)
        assert len(view.nodes) == 11


class TestSummarizeDerivation:
    def test_summary_includes_algorithm_and_dataset(self, repo):
        s = summarize_derivation(repo, DER_1)
        assert "adamw" in s
        assert "pile" in s
