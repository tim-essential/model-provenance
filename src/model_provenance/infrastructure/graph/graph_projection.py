from __future__ import annotations

import uuid
from dataclasses import dataclass

from model_provenance.domain.repositories.provenance_repository import ProvenanceRepository


@dataclass(frozen=True)
class GraphNode:
    id: str
    label: str
    kind: str
    metadata: dict


@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    label: str
    metadata: dict


@dataclass(frozen=True)
class ProjectedGraph:
    nodes: list[GraphNode]
    edges: list[GraphEdge]


def project_graph(repo: ProvenanceRepository) -> ProjectedGraph:
    root_ids = {i.child_artifact_id for i in repo.get_all_initializations()}
    checkpoint_artifact_ids = {c.artifact_id for c in repo.get_all_checkpoints()}
    nodes: list[GraphNode] = []
    for a in repo.get_all_artifacts():
        aid = a.artifact_id
        nid = str(aid)
        if aid in root_ids:
            kind = "root"
        elif aid in checkpoint_artifact_ids:
            kind = "checkpoint_artifact"
        else:
            kind = "artifact"
        nodes.append(GraphNode(id=nid, label=nid, kind=kind, metadata={}))
    edges: list[GraphEdge] = []
    for d in repo.get_all_derivations():
        edges.append(
            GraphEdge(
                source=str(d.parent_artifact_id),
                target=str(d.child_artifact_id),
                label="derivation",
                metadata={"derivation_id": str(d.derivation_id)},
            )
        )
    return ProjectedGraph(nodes=nodes, edges=edges)


def project_subgraph(repo: ProvenanceRepository, artifact_ids: set[uuid.UUID]) -> ProjectedGraph:
    full = project_graph(repo)
    wanted = {str(a) for a in artifact_ids}
    nodes = [n for n in full.nodes if n.id in wanted]
    edges = [e for e in full.edges if e.source in wanted and e.target in wanted]
    return ProjectedGraph(nodes=nodes, edges=edges)
