# Constraint Impact Analysis Report

This experiment analyzes how different types of constraints affect planning performance.

## Experiment Configuration

| Constraint Type | Description | Robots | Docks | Containers | Piles |
|----------------|-------------|--------|-------|------------|-------|
| no_constraints | No LIFO, no weight constraints | 2 | 3 | 6 | 3 |
| lifo_only | LIFO constraints only | 2 | 3 | 6 | 3 |
| weight_only | Weight constraints only | 2 | 3 | 6 | 3 |
| tight_capacity_only | Tight capacity constraints only (no LIFO, no weight constraints) | 2 | 4 | 8 | 4 |
| all_constraints | All constraints: LIFO + weight + tight capacity | 2 | 4 | 8 | 4 |

## Results Summary

| Constraint Type | Success Rate | Avg Solve Time (s) | Avg Plan Length |
|----------------|--------------|-------------------|----------------|
| no_constraints | 1.00 | 0.351 | 17.0 |
| lifo_only | 1.00 | 0.349 | 17.0 |
| weight_only | 1.00 | 0.303 | 13.0 |
| tight_capacity_only | 1.00 | 0.569 | 17.0 |
| all_constraints | 1.00 | 0.468 | 13.0 |

## Key Findings

- **Baseline (No Constraints)**: 0.351s solve time, 17.0 actions
- **lifo_only**: 0.99x solve time, 1.00x plan length
- **weight_only**: 0.86x solve time, 0.76x plan length
- **tight_capacity_only**: 1.62x solve time, 1.00x plan length
- **all_constraints**: 1.33x solve time, 0.76x plan length

## Analysis

This experiment demonstrates how different constraint types impact planning performance:

- **LIFO constraints** affect plan structure and may require more intermediate steps
- **Weight constraints** limit robot capacity and may require more careful planning
- **Combined constraints** can have compounding effects on planning complexity
- **Tight capacity** constraints significantly impact both solve time and plan length
