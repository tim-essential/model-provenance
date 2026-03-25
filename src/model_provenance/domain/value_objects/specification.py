from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Specification:
    """The interpretation-defining description of an Artifact.

    Determines how the Training State is to be understood and operated on.
    Contains architecture, parameterisation schema, optimizer definition,
    scheduler definition, training hyperparameters, tokenizer or I/O
    interface assumptions, and any other fixed or slowly changing
    training-time settings.
    """

    content: dict[str, Any]
