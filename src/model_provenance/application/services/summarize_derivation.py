"""Use case: Human-readable description of how a child artifact came from its parent."""

from __future__ import annotations

import uuid

from model_provenance.domain.repositories.provenance_repository import (
    ProvenanceRepository,
)


def summarize_derivation(
    repo: ProvenanceRepository, derivation_id: uuid.UUID
) -> str:
    deriv = repo.get_derivation(derivation_id)
    if deriv is None:
        return "Unknown derivation"

    ud = deriv.update_definition.content
    tid = deriv.training_input_descriptor.content

    algo = ud.get("algorithm", "unknown algorithm")
    loss = ud.get("loss", "")
    dataset = tid.get("dataset", "unknown data")

    parent_short = str(deriv.parent_artifact_id)[:8]
    child_short = str(deriv.child_artifact_id)[:8]

    parts = [f"{algo}"]
    if loss:
        parts.append(f"loss={loss}")
    parts.append(f"on {dataset}")

    return f"{parent_short} -> {child_short} via {', '.join(parts)}"
