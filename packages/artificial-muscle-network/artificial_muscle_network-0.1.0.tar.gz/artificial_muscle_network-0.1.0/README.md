# AMN (Artificial Muscle Network)

[![CI](https://github.com/eldm-ethanmoore/artificial-muscle-network/actions/workflows/ci.yml/badge.svg)](https://github.com/eldm-ethanmoore/artificial-muscle-network/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://eldm-ethanmoore.github.io/artificial-muscle-network/)
[![PyPI](https://img.shields.io/pypi/v/artificial-muscle-network.svg)](https://pypi.org/project/artificial-muscle-network/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A zero-dependency, physics-inspired optimization library for scheduling, routing, and allocation problems.

Why AMN:
- Free and open-source (MIT)
- Simple, Pythonic API (feels like scikit-learn)
- Multi-objective by design
- Continuous relaxation with discrete decoding
- Explainable via “forces” (objective gradients)
- Fast convergence (typically 100–500 iterations)

## Quickstart

```python
from amn import Scheduler, Resource, Task, Constraint

resources = [
    Resource("Worker A", capacity=40, skills={"welding", "assembly"}),
    Resource("Worker B", capacity=35, skills={"painting", "assembly"}),
]

tasks = [
    Task("Job 1", duration=4, required_skills={"welding"}),
    Task("Job 2", duration=3, required_skills={"painting"}),
]

constraints = [
    Constraint.no_overlap(),
    Constraint.skill_match(),
    Constraint.capacity(max_hours=40),
]

scheduler = Scheduler(resources, tasks, constraints)
solution = scheduler.optimize(max_iterations=300)

print(solution.assignments)
print(f"Energy: {solution.energy:.3f}")
print(f"Converged: {solution.converged}")
```

## Installation

AMN targets Python 3.9+. No external dependencies.

```
python -m pip install artificial-muscle-network  # once published
```

For now, clone this repo and install locally:

```
python -m pip install -e .
```

## How it works

- Variables are continuous (0–1) assignment strengths
- Objectives produce energy and gradients (forces)
- Dynamics: momentum-based gradient descent with damping
- Constraint projection keeps iterates feasible
- Decoder converts continuous solutions to discrete assignments

## Comparison

- Google OR-Tools: powerful but complex API, steep learning curve
- CPLEX/Gurobi: expensive commercial licenses
- Genetic algorithms: slow, unpredictable convergence
- Greedy heuristics: fast but often suboptimal

AMN advantages: open-source, simple API, multi-objective, explainable forces, fast convergence.

## Documentation

- docs/quickstart.md – start in minutes
- docs/api_reference.md – public API
- docs/how_it_works.md – algorithm details
- docs/tutorials/ – hands-on guides

Online docs (once GH Pages is enabled): https://eldm-ethanmoore.github.io/artificial-muscle-network/

## Contributing

Contributions welcome! See CONTRIBUTING.md and CODE_OF_CONDUCT.md.

## Security

Please see SECURITY.md for reporting vulnerabilities.

## License

MIT
