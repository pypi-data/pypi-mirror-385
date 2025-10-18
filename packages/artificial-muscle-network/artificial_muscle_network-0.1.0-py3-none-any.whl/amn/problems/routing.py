from __future__ import annotations

"""Routing problem template.

This module provides a minimal template demonstrating how to adapt AMN to
routing-like problems. For full VRP/TSP features you'd extend with distance
matrices, time windows, and vehicle capacities, providing suitable objectives
and constraints.
"""

from dataclasses import dataclass
from typing import List, Tuple

from ..core.optimizer import AMNOptimizer, Objective, Solution, Matrix
from ..core.constraints import BoundsConstraint


@dataclass
class Node:
    name: str


class RouteCompactness(Objective):
    """Toy objective that prefers confident selections (values near 0 or 1)."""

    def evaluate(self, y: Matrix) -> float:
        return sum(v * (1 - v) for row in y for v in row)

    def gradient(self, y: Matrix) -> Matrix:
        return [[1.0 - 2.0 * v for v in row] for row in y]


def simple_router(selection: Matrix, weight: float = 1.0) -> Solution:
    """Demonstration router using AMN directly on a selection matrix.

    Args:
        selection: initial matrix (n_requests x n_vehicles) with confidences.
        weight: weight for compactness objective.
    """
    obj = RouteCompactness(weight=weight)
    opt = AMNOptimizer(selection, [BoundsConstraint()], [obj])
    return opt.optimize()
