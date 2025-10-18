from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Set, Tuple
import random

from ..core.optimizer import AMNOptimizer, Objective, Solution, Matrix
from ..core.constraints import BoundsConstraint, MaskConstraint, CapacityConstraint, RowOneHotConstraint


@dataclass(frozen=True)
class Resource:
    """Represents a worker/machine/vehicle, with capacity and skills."""

    name: str
    capacity: float
    skills: Set[str]


@dataclass(frozen=True)
class Task:
    """Represents a job/shift/delivery with duration and required skills."""

    name: str
    duration: float
    required_skills: Set[str]


@dataclass(frozen=True)
class Constraint:
    """Scheduling constraint specification.

    Acts as a factory for constraint types; interpreted by Scheduler.
    """

    kind: str
    params: Dict[str, float]

    @staticmethod
    def no_overlap() -> "Constraint":
        return Constraint(kind="no_overlap", params={})

    @staticmethod
    def skill_match() -> "Constraint":
        return Constraint(kind="skill_match", params={})

    @staticmethod
    def capacity(max_hours: float) -> "Constraint":
        return Constraint(kind="capacity", params={"max_hours": float(max_hours)})


class CoverageObjective(Objective):
    """Encourage each task row to sum to 1 (exactly one resource).

    Energy: sum_i (sum_j y[i][j] - 1)^2
    dE/dy[i][j] = 2 * (sum_j y[i][j] - 1)
    """

    def evaluate(self, y: Matrix) -> float:
        e = 0.0
        for row in y:
            s = sum(row)
            d = s - 1.0
            e += d * d
        return e

    def gradient(self, y: Matrix) -> Matrix:
        g: Matrix = [[0.0 for _ in row] for row in y]
        for i, row in enumerate(y):
            d = sum(row) - 1.0
            val = 2.0 * d
            for j in range(len(row)):
                g[i][j] = val
        return g


class SparsityObjective(Objective):
    """Push variables toward 0 or 1.

    Energy: sum y*(1-y); gradient: (1 - 2y)
    """

    def evaluate(self, y: Matrix) -> float:
        return sum(val * (1.0 - val) for row in y for val in row)

    def gradient(self, y: Matrix) -> Matrix:
        return [[1.0 - 2.0 * v for v in row] for row in y]


class FairnessObjective(Objective):
    """Balance workload across resources based on task durations.

    Energy: sum_j (load_j - mean_load)^2 where load_j = sum_i y[i][j]*dur[i]
    Gradient: dE/dy[i][j] = 2*(load_j - mean)*dur[i]
    """

    def __init__(self, durations: Sequence[float], weight: float = 1.0) -> None:
        super().__init__(weight=weight)
        self._dur = [float(d) for d in durations]

    def _loads(self, y: Matrix) -> List[float]:
        n = len(y)
        m = len(y[0]) if n else 0
        loads = [0.0 for _ in range(m)]
        for j in range(m):
            s = 0.0
            for i in range(n):
                s += y[i][j] * self._dur[i]
            loads[j] = s
        return loads

    def evaluate(self, y: Matrix) -> float:
        loads = self._loads(y)
        if not loads:
            return 0.0
        mean = sum(loads) / len(loads)
        return sum((l - mean) * (l - mean) for l in loads)

    def gradient(self, y: Matrix) -> Matrix:
        n = len(y)
        m = len(y[0]) if n else 0
        loads = self._loads(y)
        mean = sum(loads) / m if m else 0.0
        g: Matrix = [[0.0 for _ in range(m)] for _ in range(n)]
        for i in range(n):
            di = self._dur[i]
            for j in range(m):
                g[i][j] = 2.0 * (loads[j] - mean) * di
        return g


class Scheduler:
    """High-level convenience wrapper for scheduling problems.

    Example:
        resources = [Resource("A", 40, {"welding"}), Resource("B", 35, {"painting"})]
        tasks = [Task("Job1", 4, {"welding"}), Task("Job2", 3, {"painting"})]
        constraints = [Constraint.no_overlap(), Constraint.skill_match(), Constraint.capacity(40)]
        scheduler = Scheduler(resources, tasks, constraints)
        solution = scheduler.optimize(max_iterations=300)
    """

    def __init__(
        self,
        resources: List[Resource],
        tasks: List[Task],
        constraints: List[Constraint],
        *,
        coverage_weight: float = 2.0,
        fairness_weight: float = 1.0,
        sparsity_weight: float = 0.5,
        dt: float = 0.1,
        damping: float = 0.1,
        seed: Optional[int] = None,
    ) -> None:
        if not resources:
            raise ValueError("resources must be non-empty")
        if not tasks:
            raise ValueError("tasks must be non-empty")
        self.resources = resources
        self.tasks = tasks
        self.constraint_specs = constraints
        self.coverage_weight = float(coverage_weight)
        self.fairness_weight = float(fairness_weight)
        self.sparsity_weight = float(sparsity_weight)
        self.dt = float(dt)
        self.damping = float(damping)
        self.seed = seed

    def _mask(self) -> List[List[int]]:
        n = len(self.tasks)
        m = len(self.resources)
        mask = [[0 for _ in range(m)] for _ in range(n)]
        for i, t in enumerate(self.tasks):
            for j, r in enumerate(self.resources):
                ok = t.required_skills.issubset(r.skills)
                mask[i][j] = 1 if ok else 0
        return mask

    def _durations(self) -> List[float]:
        return [float(t.duration) for t in self.tasks]

    def _capacities(self) -> List[float]:
        # If capacity constraint is provided with max_hours, cap each resource by min(resource.capacity, max_hours)
        max_hours_param = None
        for spec in self.constraint_specs:
            if spec.kind == "capacity" and "max_hours" in spec.params:
                max_hours_param = float(spec.params["max_hours"])
        caps: List[float] = []
        for r in self.resources:
            cap = float(r.capacity)
            if max_hours_param is not None:
                cap = min(cap, max_hours_param)
            caps.append(cap)
        return caps

    def _initial(self, mask: List[List[int]]) -> Matrix:
        n = len(self.tasks)
        m = len(self.resources)
        rng = random.Random(self.seed)
        y: Matrix = [[0.0 for _ in range(m)] for _ in range(n)]
        for i in range(n):
            # initialize only allowed entries
            for j in range(m):
                if mask[i][j]:
                    y[i][j] = rng.random()
            s = sum(y[i])
            if s > 0.0:
                inv = 1.0 / s
                for j in range(m):
                    y[i][j] *= inv
        return y

    def optimize(self, max_iterations: int = 500, tolerance: float = 1e-4) -> Solution:
        mask = self._mask()
        y0 = self._initial(mask)
        durations = self._durations()
        capacities = self._capacities()

        # Build objectives
        objectives: List[Objective] = [
            CoverageObjective(weight=self.coverage_weight),
            FairnessObjective(durations, weight=self.fairness_weight),
            SparsityObjective(weight=self.sparsity_weight),
        ]

        # Build constraints
        constraints_low = [
            BoundsConstraint(0.0, 1.0),
            MaskConstraint(mask),
            CapacityConstraint(durations=durations, capacities=capacities),
        ]
        if any(spec.kind == "no_overlap" for spec in self.constraint_specs):
            constraints_low.append(RowOneHotConstraint())

        opt = AMNOptimizer(
            variables=y0,
            constraints=constraints_low,
            objectives=objectives,
            dt=self.dt,
            damping=self.damping,
            seed=self.seed,
        )
        sol = opt.optimize(max_iterations=max_iterations, tolerance=tolerance)

        # Decode to discrete assignments with capacity and skills respected
        assignments = self._decode_with_capacities(opt)
        return Solution(
            assignments=assignments,
            energy=sol.energy,
            energies=sol.energies,
            converged=sol.converged,
            iterations=sol.iterations,
        )

    def _decode_with_capacities(self, opt: AMNOptimizer) -> List[Tuple[Task, Resource]]:
        y = opt.y
        durations = self._durations()
        capacities = self._capacities()
        mask = self._mask()
        remaining = [c for c in capacities]
        # Greedy: sort tasks by confidence (max y in row)
        task_order = list(range(len(self.tasks)))
        task_order.sort(key=lambda i: max(y[i]) if y[i] else 0.0, reverse=True)
        assignments: List[Tuple[Task, Resource]] = []
        for i in task_order:
            # Try best resource first
            prefs = list(range(len(self.resources)))
            prefs.sort(key=lambda j: y[i][j], reverse=True)
            for j in prefs:
                if mask[i][j] == 0:
                    continue
                d = durations[i]
                if remaining[j] >= d:
                    assignments.append((self.tasks[i], self.resources[j]))
                    remaining[j] -= d
                    break
        return assignments
