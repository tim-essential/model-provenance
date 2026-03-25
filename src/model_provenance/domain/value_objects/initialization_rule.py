from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class InitializationRule:
    """The declarative rule that creates an initial Training State
    for a Specification.

    Examples: random init, imported pretrained weights, partial parameter
    transplant, zero-init adapters, architecture conversion from prior
    artifact.
    """

    content: dict[str, Any]
