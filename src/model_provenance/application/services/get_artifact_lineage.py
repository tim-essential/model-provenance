"""Use case: Get ancestor subgraph for a selected artifact."""

from __future__ import annotations

import uuid

from model_provenance.application.dto.graph_dto import (
    GraphEdgeView,
    GraphNodeView,
    GraphView,
)
from model_provenance.domain.repositories.provenance_repository import (
    ProvenanceRepository,
)
from model_provenance.domain.services.lineage_service import LineageService
from model_provenance.infrastructure.graph.graph_projection import project_subgraph
from model_provenance.infrastructure.graph.layout import compute_layers


def get_artifact_lineage(
    repo: ProvenanceRepository, artifact_id: uuid.UUID
) -> GraphView:
    service = LineageService(repo)
    lineage = service.compute_lineage(artifact_id)

    all_ids = {artifact_id} | set(lineage.ancestor_artifact_ids)
    projected = project_subgraph(repo, all_ids)
    layers = compute_layers(projected)

    nodes = [
        GraphNodeView(
            id=n.id,
            label=n.id[:8],
            kind=n.kind,
            layer=layers.get(n.id, 0),
            metadata=dict(n.metadata),
        )
        for n in projected.nodes
    ]
    edges = [
        GraphEdgeView(
            source=e.source,
            target=e.target,
            label=e.label,
            metadata=dict(e.metadata),
        )
        for e in projected.edges
    ]

    return GraphView(nodes=nodes, edges=edges)
