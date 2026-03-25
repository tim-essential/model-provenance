from __future__ import annotations

from collections import deque

from model_provenance.infrastructure.graph.graph_projection import ProjectedGraph


def compute_layers(graph: ProjectedGraph) -> dict[str, int]:
    ids = {n.id for n in graph.nodes}
    preds: dict[str, list[str]] = {nid: [] for nid in ids}
    succ: dict[str, list[str]] = {nid: [] for nid in ids}
    for e in graph.edges:
        if e.source in ids and e.target in ids:
            preds[e.target].append(e.source)
            succ[e.source].append(e.target)
    indeg = {nid: len(preds[nid]) for nid in ids}
    q = deque(nid for nid in ids if indeg[nid] == 0)
    topo: list[str] = []
    while q:
        u = q.popleft()
        topo.append(u)
        for v in succ[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    layers: dict[str, int] = {}
    for nid in topo:
        ps = preds[nid]
        layers[nid] = 0 if not ps else 1 + max(layers[p] for p in ps)
    for nid in ids:
        if nid not in layers:
            ps = preds[nid]
            layers[nid] = 0 if not ps else 1 + max(layers.get(p, 0) for p in ps)
    return layers
