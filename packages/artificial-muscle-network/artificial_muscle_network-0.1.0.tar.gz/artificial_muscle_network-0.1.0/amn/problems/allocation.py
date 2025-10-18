from __future__ import annotations

"""Resource allocation problem template.

Use AMNOptimizer with custom objectives/constraints to allocate limited
resources to competing demands. See examples/portfolio_optimization.py for
how to use the core optimizer directly.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Item:
    name: str
    value: float
    demand: float
