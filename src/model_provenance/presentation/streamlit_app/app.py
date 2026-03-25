"""Streamlit app for interactive ML training provenance visualization."""

from __future__ import annotations

import uuid
from pathlib import Path

import streamlit as st
from streamlit_agraph import Config, agraph

from model_provenance.application.dto.graph_dto import GraphView
from model_provenance.application.services.filter_graph import (
    GraphFilter,
    filter_graph,
)
from model_provenance.application.services.find_reproduction_inputs import (
    find_reproduction_inputs,
)
from model_provenance.application.services.get_artifact_details import (
    get_artifact_details,
)
from model_provenance.application.services.get_artifact_lineage import (
    get_artifact_lineage,
)
from model_provenance.application.services.get_checkpoint_branches import (
    get_checkpoint_branches,
)
from model_provenance.application.services.get_derivation_details import (
    get_derivation_details_by_edge,
)
from model_provenance.application.services.get_run_view import get_run_view
from model_provenance.application.services.load_provenance_graph import (
    load_provenance_graph,
)
from model_provenance.infrastructure.repositories.json_provenance_repository import (
    InMemoryProvenanceRepository,
)
from model_provenance.presentation.streamlit_app.components.detail_panel import (
    render_artifact_detail,
    render_derivation_detail,
    render_reproduction_panel,
)
from model_provenance.presentation.streamlit_app.viewmodels.graph_viewmodel import (
    build_agraph_config,
    build_agraph_edges,
    build_agraph_nodes,
)

st.set_page_config(page_title="Model Provenance", layout="wide")

DEFAULT_DATA = Path(__file__).resolve().parents[4] / "data" / "sample_provenance.json"


def _try_uuid(s: str) -> uuid.UUID | None:
    try:
        return uuid.UUID(s)
    except (ValueError, AttributeError):
        return None


def _resolve_artifact_prefix(
    repo: InMemoryProvenanceRepository, prefix: str
) -> uuid.UUID | None:
    if not prefix:
        return None
    for a in repo.get_all_artifacts():
        if str(a.artifact_id).startswith(prefix):
            return a.artifact_id
    return None


def _find_edge_derivation_id(
    graph: GraphView, source: str, target: str
) -> str | None:
    for e in graph.edges:
        if e.source == source and e.target == target:
            return e.metadata.get("derivation_id")
    return None


def main() -> None:
    st.title("Model Provenance Explorer")
    st.caption("Click any node to inspect an artifact. Click an edge to see derivation details.")

    # --- Sidebar ---
    with st.sidebar:
        st.header("Data Source")
        data_path = st.text_input(
            "Provenance JSON path", value=str(DEFAULT_DATA)
        )
        if not Path(data_path).exists():
            st.error(f"File not found: {data_path}")
            return

        repo, full_graph = load_provenance_graph(data_path)

        st.divider()
        st.header("Filters")

        all_runs = repo.get_all_runs()
        run_options = {
            f"{r.name} ({str(r.run_id)[:8]})": r.run_id for r in all_runs
        }
        selected_run_label = st.selectbox("Run", ["All"] + list(run_options.keys()))

        all_checkpoints = repo.get_all_checkpoints()
        ckpt_options = {
            f"{(c.handle or str(c.checkpoint_id))[:40]} ({str(c.checkpoint_id)[:8]})": c.checkpoint_id
            for c in all_checkpoints
        }
        selected_ckpt_label = st.selectbox(
            "Checkpoint", ["None"] + list(ckpt_options.keys())
        )

        st.divider()
        st.header("View Mode")
        view_mode = st.radio(
            "Graph view",
            ["Full DAG", "Lineage", "Reproduction chain"],
            index=0,
        )

    # --- Resolve filter selections ---
    selected_run_id: uuid.UUID | None = None
    if selected_run_label != "All":
        selected_run_id = run_options.get(selected_run_label)

    selected_ckpt_id: uuid.UUID | None = None
    if selected_ckpt_label != "None":
        selected_ckpt_id = ckpt_options.get(selected_ckpt_label)

    # --- Session state for selections ---
    if "selected_node" not in st.session_state:
        st.session_state.selected_node = None

    selected_artifact_id: uuid.UUID | None = None
    if st.session_state.selected_node:
        selected_artifact_id = _try_uuid(st.session_state.selected_node)

    # --- Highlight run path ---
    highlight_ids: set[str] = set()
    highlight_edges: set[tuple[str, str]] = set()
    if selected_run_id is not None:
        run = repo.get_run(selected_run_id)
        if run:
            highlight_ids = {str(aid) for aid in run.artifact_ids}
            for did in run.derivation_ids:
                d = repo.get_derivation(did)
                if d:
                    highlight_edges.add(
                        (str(d.parent_artifact_id), str(d.child_artifact_id))
                    )

    # --- Choose what subgraph to display ---
    display_graph = full_graph

    if view_mode == "Lineage" and selected_artifact_id is not None:
        display_graph = get_artifact_lineage(repo, selected_artifact_id)
    elif view_mode == "Full DAG":
        has_filter = selected_run_id or selected_ckpt_id
        if has_filter:
            filt = GraphFilter(
                run_id=selected_run_id,
                checkpoint_id=selected_ckpt_id,
            )
            display_graph = filter_graph(repo, filt)

    # --- Layout: graph left, detail right ---
    graph_col, detail_col = st.columns([3, 2])

    with graph_col:
        nodes = build_agraph_nodes(
            display_graph,
            highlight_artifact_ids=highlight_ids or None,
            selected_id=str(selected_artifact_id) if selected_artifact_id else None,
        )
        edges = build_agraph_edges(
            display_graph,
            highlight_edge_pairs=highlight_edges or None,
        )

        config = build_agraph_config()
        clicked = agraph(nodes=nodes, edges=edges, config=config)

        if clicked and clicked != st.session_state.selected_node:
            st.session_state.selected_node = clicked
            st.rerun()

        if selected_run_id:
            rv = get_run_view(repo, selected_run_id)
            if rv:
                st.caption(
                    f"**{rv.name}** — {len(rv.artifact_ids)} artifacts, "
                    f"{len(rv.derivation_ids)} derivations"
                )

        if selected_ckpt_id:
            branches = get_checkpoint_branches(repo, selected_ckpt_id)
            if branches:
                st.caption(
                    f"Checkpoint on `{branches.artifact_id[:8]}...` — "
                    f"{len(branches.descendant_artifact_ids)} descendants"
                )
                for r in branches.runs:
                    st.markdown(f"  - **{r.name}**")

    with detail_col:
        if selected_artifact_id is not None:
            detail = get_artifact_details(repo, selected_artifact_id)
            render_artifact_detail(detail)

            if detail.incoming_derivation:
                parent_id = _try_uuid(detail.incoming_derivation.parent_artifact_id)
                if parent_id:
                    st.button(
                        f"← Go to parent ({detail.incoming_derivation.parent_artifact_id[:8]}...)",
                        key="go_parent",
                        on_click=_select_node,
                        args=(detail.incoming_derivation.parent_artifact_id,),
                    )

            child_derivs = repo.get_derivations_by_parent(selected_artifact_id)
            if child_derivs:
                st.caption("Children")
                for cd in child_derivs:
                    child_str = str(cd.child_artifact_id)
                    dataset = cd.training_input_descriptor.content.get("dataset", "?")
                    st.button(
                        f"→ {child_str[:8]}... ({dataset})",
                        key=f"go_child_{cd.derivation_id}",
                        on_click=_select_node,
                        args=(child_str,),
                    )

            if view_mode == "Reproduction chain":
                st.divider()
                st.markdown("### Reproduction Chain")
                repro = find_reproduction_inputs(repo, selected_artifact_id)
                render_reproduction_panel(repro)

        else:
            st.info(
                "👆 **Click a node** in the graph to inspect its artifact, "
                "specification, training state, and derivation details."
            )
            _render_artifact_list(repo)


def _select_node(node_id: str) -> None:
    st.session_state.selected_node = node_id


def _render_artifact_list(repo: InMemoryProvenanceRepository) -> None:
    st.markdown("### All Artifacts")
    for a in repo.get_all_artifacts():
        aid_str = str(a.artifact_id)
        step = a.training_state.content.get("step", "?")
        summary = a.training_state.content.get("summary", "")
        ckpts = repo.get_checkpoints_for_artifact(a.artifact_id)
        ckpt_badge = f" 📌×{len(ckpts)}" if ckpts else ""
        st.button(
            f"{aid_str[:12]}... step={step}{ckpt_badge} — {summary}",
            key=f"list_{aid_str}",
            on_click=_select_node,
            args=(aid_str,),
        )


if __name__ == "__main__":
    main()
