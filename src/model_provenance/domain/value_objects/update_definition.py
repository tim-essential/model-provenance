from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class UpdateDefinition:
    """The declarative definition of the transformation used by a Derivation.

    Includes algorithm identity, loss definition, gradient transformation,
    optimizer application rule, and any deterministic or declared stochastic
    transformation logic.
    """

    content: dict[str, Any]
