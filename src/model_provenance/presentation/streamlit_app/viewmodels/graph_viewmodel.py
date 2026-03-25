"""Viewmodel for building streamlit-agraph nodes/edges from GraphView."""

from __future__ import annotations

from streamlit_agraph import Config, Edge, Node

from model_provenance.application.dto.graph_dto import GraphView

NODE_COLORS = {
    "root": "#2e7d32",
    "checkpoint_artifact": "#e65100",
    "artifact": "#1565c0",
}

NODE_BG = {
    "root": "#e8f5e9",
    "checkpoint_artifact": "#fff3e0",
    "artifact": "#e3f2fd",
}

NODE_SHAPES = {
    "root": "diamond",
    "checkpoint_artifact": "box",
    "artifact": "dot",
}


def build_agraph_config() -> Config:
    return Config(
        directed=True,
        physics=False,
        hierarchical=True,
        direction="LR",
        sortMethod="directed",
        nodeHighlightBehavior=True,
        highlightColor="#d32f2f",
        collapsible=False,
        node={"highlightStrokeColor": "#d32f2f"},
        link={"highlightColor": "#6a1b9a"},
        width=1100,
        height=500,
        staticGraphWithDragAndDrop=True,
        key="provenance_graph",
    )


def build_agraph_nodes(
    graph: GraphView,
    *,
    highlight_artifact_ids: set[str] | None = None,
    selected_id: str | None = None,
) -> list[Node]:
    highlight = highlight_artifact_ids or set()
    nodes: list[Node] = []
    for n in graph.nodes:
        color = NODE_COLORS.get(n.kind, "#1565c0")
        bg = NODE_BG.get(n.kind, "#e3f2fd")
        shape = NODE_SHAPES.get(n.kind, "dot")
        size = 20

        ckpts = n.metadata.get("checkpoints", [])
        label_parts = [n.label]
        for h in ckpts:
            short = h.rsplit("/", 1)[-1] if "/" in h else h[:12]
            label_parts.append(f"📌 {short}")
        label = "\n".join(label_parts)

        if n.id in highlight:
            color = "#6a1b9a"
            size = 25

        is_selected = n.id == selected_id
        if is_selected:
            color = "#d32f2f"
            bg = "#ffcdd2"
            size = 30

        nodes.append(
            Node(
                id=n.id,
                label=label,
                size=size,
                color=color,
                shape=shape,
                font={"color": "#212121", "size": 11},
            )
        )
    return nodes


def build_agraph_edges(
    graph: GraphView,
    *,
    highlight_edge_pairs: set[tuple[str, str]] | None = None,
) -> list[Edge]:
    highlight = highlight_edge_pairs or set()
    edges: list[Edge] = []
    for e in graph.edges:
        is_hl = (e.source, e.target) in highlight
        deriv_id = e.metadata.get("derivation_id", "")
        edges.append(
            Edge(
                source=e.source,
                target=e.target,
                label=deriv_id[:8] if deriv_id else "",
                color="#6a1b9a" if is_hl else "#90a4ae",
                width=3 if is_hl else 1.5,
            )
        )
    return edges
