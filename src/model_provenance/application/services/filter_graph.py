"""Use case: Filter the provenance graph by run, checkpoint, artifact id, or metadata."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from model_provenance.application.dto.graph_dto import (
    GraphEdgeView,
    GraphNodeView,
    GraphView,
)
from model_provenance.domain.repositories.provenance_repository import (
    ProvenanceRepository,
)
from model_provenance.infrastructure.graph.graph_projection import project_subgraph
from model_provenance.infrastructure.graph.layout import compute_layers


@dataclass
class GraphFilter:
    run_id: uuid.UUID | None = None
    checkpoint_id: uuid.UUID | None = None
    artifact_ids: set[uuid.UUID] = field(default_factory=set)
    spec_key: str | None = None
    spec_value: str | None = None


def filter_graph(repo: ProvenanceRepository, filt: GraphFilter) -> GraphView:
    matching_ids: set[uuid.UUID] = set()

    if filt.run_id is not None:
        run = repo.get_run(filt.run_id)
        if run is not None:
            matching_ids.update(run.artifact_ids)

    if filt.checkpoint_id is not None:
        ckpt = repo.get_checkpoint(filt.checkpoint_id)
        if ckpt is not None:
            matching_ids.add(ckpt.artifact_id)

    if filt.artifact_ids:
        matching_ids.update(filt.artifact_ids)

    if filt.spec_key is not None:
        for artifact in repo.get_all_artifacts():
            val = artifact.specification.content.get(filt.spec_key)
            if val is not None and (
                filt.spec_value is None or str(val) == filt.spec_value
            ):
                matching_ids.add(artifact.artifact_id)

    if not matching_ids:
        matching_ids = {a.artifact_id for a in repo.get_all_artifacts()}

    projected = project_subgraph(repo, matching_ids)
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
