# Scientific Experiments for Logistics Planning

This folder contains systematic experiments to evaluate planning performance, scalability, and constraint impacts in our logistics domain.

## Experiment Categories

### 1. **Scaling Analysis** (`scaling/`)
- Tests how planning performance scales with problem size
- Variables: robots, docks, containers, piles
- Metrics: time, memory, nodes expanded, success rate

### 2. **Heuristic Comparison** (`heuristics/`)
- Compares different planning heuristics
- Variables: GBFS, A*, FF, h_add, h_max
- Metrics: solve time, plan length, search effort

### 3. **Constraint Impact** (`constraints/`)
- Analyzes impact of LIFO and weight constraints
- Variables: with/without constraints, different configurations
- Metrics: difficulty, plan quality, search efficiency

### 4. **Problem Structure** (`topology/`)
- Tests different dock topologies and pile distributions
- Variables: linear, star, grid topologies; balanced/unbalanced piles
- Metrics: planning efficiency, structural insights

### 5. **Weight Distribution** (`weights/`)
- Studies impact of different weight distributions
- Variables: uniform vs. mixed weights, capacity ratios
- Metrics: planning difficulty, capacity utilization

## Running Experiments

```bash
# Run all experiments
python experiments/run_all_experiments.py

# Run specific experiment
python experiments/scaling/scaling_analysis.py
python experiments/heuristics/heuristic_comparison.py
python experiments/constraints/constraint_impact.py
python experiments/topology/topology_analysis.py
python experiments/weights/weight_distribution.py
```

## Output Format

All experiments generate:
- **CSV files** with raw data
- **JSON files** with metadata
- **Plots** (PNG/PDF) for visualization
- **Summary reports** (Markdown) with analysis

## Statistical Analysis

- **Descriptive statistics**: mean, median, std, quartiles
- **Statistical tests**: t-tests, ANOVA, correlation analysis
- **Effect sizes**: Cohen's d, eta-squared
- **Confidence intervals**: 95% CI for key metrics

## Reproducibility

- **Random seeds**: Fixed for reproducibility
- **Multiple runs**: 10+ runs per configuration
- **Environment info**: Python version, UP version, system specs
- **Configuration files**: All parameters saved as JSON
