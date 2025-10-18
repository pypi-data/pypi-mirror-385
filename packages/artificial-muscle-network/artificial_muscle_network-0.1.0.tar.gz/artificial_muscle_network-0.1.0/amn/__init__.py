"""AMN: Artificial Muscle Network

Zero-dependency optimization library using physics-inspired dynamics.
"""
from .core.optimizer import AMNOptimizer as Optimizer, Objective, Solution
from .problems.scheduling import Scheduler, Resource, Task, Constraint

__all__ = [
    "Optimizer",
    "Objective",
    "Solution",
    "Scheduler",
    "Resource",
    "Task",
    "Constraint",
]
