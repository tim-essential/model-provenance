"""Components for the detail side panel."""

from __future__ import annotations

import streamlit as st

from model_provenance.application.dto.artifact_dto import ArtifactDetailView
from model_provenance.application.dto.derivation_dto import DerivationDetailView
from model_provenance.application.services.find_reproduction_inputs import (
    ReproductionView,
)


def render_artifact_detail(detail: ArtifactDetailView) -> None:
    st.markdown(f"### Artifact `{detail.artifact_id[:12]}...`")

    if detail.is_root:
        st.success(f"**Root artifact** — {detail.initialization_summary}")
    elif detail.incoming_derivation:
        d = detail.incoming_derivation
        st.info(f"**Derived:** {d.description}")

    tab_spec, tab_state, tab_deriv, tab_meta = st.tabs(
        ["Specification", "Training State", "Derivation", "Metadata"]
    )

    with tab_spec:
        st.json(detail.specification)

    with tab_state:
        st.json(detail.training_state)

    with tab_deriv:
        if detail.incoming_derivation:
            d = detail.incoming_derivation
            st.caption("Update Definition")
            st.json(d.update_definition)
            st.caption("Training Input Descriptor")
            st.json(d.training_input_descriptor)
            st.caption("Execution Record")
            st.json(d.execution_record)
        elif detail.is_root:
            st.markdown(f"_Root artifact:_ {detail.initialization_summary}")
        else:
            st.markdown("_No incoming derivation found_")

    with tab_meta:
        if detail.checkpoints:
            st.caption("Checkpoints")
            for c in detail.checkpoints:
                handle = c.handle or "no handle"
                st.markdown(
                    f"- `{c.checkpoint_id[:12]}...` — {handle} ({c.created_at})"
                )

        if detail.run_names:
            st.caption("Part of runs")
            st.markdown(", ".join(f"**{name}**" for name in detail.run_names))

        st.caption("Full Artifact ID")
        st.code(detail.artifact_id, language=None)


def render_derivation_detail(detail: DerivationDetailView) -> None:
    st.markdown(f"### Derivation `{detail.derivation_id[:12]}...`")
    st.info(f"**{detail.description}**")

    tab_update, tab_data, tab_exec, tab_artifacts = st.tabs(
        ["Update Definition", "Training Data", "Execution", "Artifacts"]
    )

    with tab_update:
        st.json(detail.update_definition)

    with tab_data:
        st.json(detail.training_input_descriptor)

    with tab_exec:
        st.json(detail.execution_record)

    with tab_artifacts:
        col_p, col_c = st.columns(2)
        with col_p:
            st.caption(f"Parent `{detail.parent_artifact_id[:8]}...`")
            st.caption("Specification")
            st.json(detail.parent_spec)
            st.caption("Training State")
            st.json(detail.parent_training_state_summary)
        with col_c:
            st.caption(f"Child `{detail.child_artifact_id[:8]}...`")
            st.caption("Specification")
            st.json(detail.child_spec)
            st.caption("Training State")
            st.json(detail.child_training_state_summary)


def render_reproduction_panel(repro: ReproductionView) -> None:
    if repro.is_complete:
        st.success("Complete reproduction chain available")
    else:
        st.warning("Incomplete — missing initialization record")

    if repro.initialization_rule:
        st.caption("Initialization Rule")
        st.json(repro.initialization_rule)

    if repro.root_specification:
        st.caption("Root Specification")
        st.json(repro.root_specification)

    if repro.steps:
        st.caption(f"Derivation chain ({len(repro.steps)} steps)")
        for i, step in enumerate(repro.steps):
            with st.expander(
                f"Step {i + 1}: {step.parent_artifact_id[:8]}... → {step.child_artifact_id[:8]}..."
            ):
                st.caption("Update Definition")
                st.json(step.update_definition)
                st.caption("Training Input Descriptor")
                st.json(step.training_input_descriptor)
                st.caption("Execution Record")
                st.json(step.execution_record)
