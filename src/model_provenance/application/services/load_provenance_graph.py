"""Use case: Load provenance graph from a data source."""

from __future__ import annotations

from pathlib import Path

from model_provenance.application.dto.graph_dto import (
    GraphEdgeView,
    GraphNodeView,
    GraphView,
)
from model_provenance.infrastructure.graph.graph_projection import project_graph
from model_provenance.infrastructure.graph.layout import compute_layers
from model_provenance.infrastructure.repositories.json_provenance_repository import (
    InMemoryProvenanceRepository,
)
from model_provenance.infrastructure.serializers.json_loader import (
    load_provenance_file,
)


def load_provenance_graph(path: str | Path) -> tuple[InMemoryProvenanceRepository, GraphView]:
    """Load provenance data and return the repository + projected graph view."""
    data = load_provenance_file(path)
    repo = InMemoryProvenanceRepository.from_dict(data)
    projected = project_graph(repo)
    layers = compute_layers(projected)

    checkpoints = repo.get_all_checkpoints()
    ckpt_artifact_ids = {str(c.artifact_id) for c in checkpoints}
    ckpt_handles: dict[str, list[str]] = {}
    for c in checkpoints:
        ckpt_handles.setdefault(str(c.artifact_id), []).append(
            c.handle or str(c.checkpoint_id)
        )

    nodes = []
    for n in projected.nodes:
        label = n.id[:8]
        meta = dict(n.metadata)
        if n.id in ckpt_artifact_ids:
            meta["checkpoints"] = ckpt_handles.get(n.id, [])
        nodes.append(
            GraphNodeView(
                id=n.id,
                label=label,
                kind=n.kind,
                layer=layers.get(n.id, 0),
                metadata=meta,
            )
        )

    edges = [
        GraphEdgeView(
            source=e.source,
            target=e.target,
            label=e.label,
            metadata=dict(e.metadata),
        )
        for e in projected.edges
    ]

    return repo, GraphView(nodes=nodes, edges=edges)
