# Scientific Experiments for Logistics Planning

This folder contains systematic experiments to evaluate planning performance, scalability, and constraint impacts in our logistics domain.

## Experiment Categories

### 1. **Scaling Analysis** (`scaling/`)

**Goal**: Understand how planning performance scales with problem size and complexity.

**Setup**:
- **Small problems**: 1-2 robots, 3-4 docks, 4-6 containers, 3-4 piles
- **Medium problems**: 2-3 robots, 5-6 docks, 8-12 containers, 5-6 piles  
- **Large problems**: 3-4 robots, 7-8 docks, 14-18 containers, 7-8 piles
- **Robot capacity**: 6t (small/medium), 5t (large for tight capacity)
- **Container weights**: Mixed (2t, 4t, 6t) based on problem size
- **Goals**: Simple swap, complex redistribution, weight-constrained patterns

**Methodology**:
- 5 runs per configuration for statistical reliability
- Fast Downward planner with default settings
- Challenging goals that require actual planning (not trivially satisfied)

**Metrics**: Solve time, plan length, success rate, scalability trends

---

### 2. **Heuristic Comparison** (`heuristics/`)

**Goal**: Compare performance of different Fast Downward heuristics on logistics problems.

**Setup**:
- **Easy problems**: 1 robot, 3-4 docks, 4-6 containers, 3-4 piles, simple swap goals
- **Medium problems**: 2 robots, 4-6 docks, 8-12 containers, 4-6 piles, complex redistribution
- **Hard problems**: 3 robots, 6-7 docks, 14-18 containers, 6-7 piles, weight-constrained goals
- **Extreme problems**: 4 robots, 8 docks, 25 containers, 8 piles, weight-constrained goals
- **Heuristics tested**: 
  - `gbfs(ff())` - Greedy Best-First Search with Fast Forward heuristic
  - `gbfs(hadd())` - Greedy Best-First Search with hAdd heuristic  
  - `gbfs(hmax())` - Greedy Best-First Search with hMax heuristic

**Methodology**:
- 3 runs per heuristic per problem difficulty
- UP Fast Downward interface for consistent execution
- Non-trivial goals requiring 6-18 actions across problem sizes

**Metrics**: Solve time, plan length, success rate, heuristic efficiency

---

### 3. **Constraint Impact** (`constraints/`)

**Goal**: Analyze how different constraint types affect planning performance and plan quality.

**Setup**:
- **no_constraints**: All containers 2t, normal capacity (6t), no LIFO
- **lifo_only**: All containers 2t, normal capacity (6t), with LIFO constraints
- **weight_only**: Mixed weights (2t/4t/6t), normal capacity (6t), no LIFO
- **tight_capacity_only**: All containers 2t, tight capacity (5t), no LIFO
- **all_constraints**: Mixed weights (2t/4t/6t), tight capacity (5t), with LIFO

**Methodology**:
- 3 runs per constraint configuration
- Same problem size (2 robots, 3-4 docks, 6-8 containers, 3-4 piles)
- Challenging redistribution goals requiring cross-pile movement

**Metrics**: Solve time, plan length, constraint impact ratios, efficiency analysis

---

### 4. **Topology Analysis** (`topology/`)

**Goal**: Study how different dock network topologies affect planning efficiency and routing.

**Setup**:
- **Linear topology**: Docks in a line (d1-d2-d3-d4...)
- **Star topology**: Central hub with spokes (center connected to all others)
- **Grid topology**: 2D grid arrangement (2×2, 3×2 grids)
- **Ring topology**: Circular arrangement (d1-d2-d3-d4-d1...)
- **Problem sizes**: 4-8 docks, 2-3 robots, 8-18 containers, 4-8 piles

**Methodology**:
- 5 runs per topology configuration
- Cross-topology movement goals requiring navigation between distant docks
- Mixed container weights (2t, 4t, 6t) for realistic constraints

**Metrics**: Solve time, plan length, topology efficiency, routing patterns

---

### 5. **Weight Distribution** (`weights/`)

**Goal**: Investigate how different container weight distributions impact planning complexity.

**Setup**:
- **Uniform distributions**: All containers same weight (2t, 4t, or 6t)
- **Mixed balanced**: Equal mix of 2t, 4t, 6t containers
- **Light-biased**: 70% light (2t), 30% medium (4t) containers
- **Heavy-biased**: 30% light (2t), 70% heavy (6t) containers
- **Extreme scenarios**: Heavy containers with tight robot capacity (5t)

**Methodology**:
- 5 runs per weight distribution
- Weight-aware redistribution goals requiring capacity management
- Robot capacity: 6t (normal) or 5t (tight capacity scenarios)

**Metrics**: Solve time, plan length, capacity utilization, weight constraint impact

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

## Expected Results & Insights

### Scaling Analysis
- **Expected**: Solve time increases non-linearly with problem size
- **Key insight**: Robot capacity constraints become bottlenecks at larger scales
- **Typical results**: 7-20 actions, 0.2-5.3s solve time across problem sizes

### Heuristic Comparison  
- **Expected**: All heuristics perform similarly on this domain
- **Key insight**: Logistics domain may not expose significant heuristic differences
- **Typical results**: 6-18 actions, 0.21-9.97s solve time, 100% success rate
- **Scaling pattern**: Solve time increases dramatically with problem size (0.2s → 10s for 4→25 containers)

### Constraint Impact
- **Expected**: Weight constraints improve efficiency, tight capacity increases solve time
- **Key insight**: Some constraints can actually help planning by reducing search space
- **Typical results**: 13-17 actions, 0.30-0.57s solve time, tight capacity is main bottleneck

### Topology Analysis
- **Expected**: Star topology may create bottlenecks, grid provides redundancy
- **Key insight**: Network structure significantly affects routing efficiency
- **Typical results**: 6-20 actions, 0.2-5.3s solve time, topology-dependent performance

### Weight Distribution
- **Expected**: Heavy-biased distributions require more careful planning
- **Key insight**: Weight distribution affects both plan length and solve time
- **Typical results**: 6-20 actions, 0.2-5.3s solve time, capacity utilization varies

## Output Format

All experiments generate:
- **`raw_results.json`**: Complete experimental data with all runs
- **`summary.csv`**: Statistical summaries (mean, std, min, max)
- **`*_analysis.png`**: Visualization plots (bar charts, scatter plots, comparisons)
- **`report.md`**: Detailed analysis with findings and insights

## Statistical Methodology

- **Multiple runs**: 3-5 runs per configuration for statistical reliability
- **Descriptive statistics**: Mean, standard deviation, min, max for all metrics
- **Comparative analysis**: Impact ratios and efficiency comparisons
- **Visualization**: Bar charts, scatter plots, and trend analysis
- **Robust error handling**: Graceful handling of timeouts and failures

## Technical Details

- **Planner**: Fast Downward via Unified Planning interface
- **Timeout**: 60 seconds per planning attempt
- **Environment**: Python 3.12, Unified Planning 1.2.0, Fast Downward
- **Reproducibility**: Fixed random seeds, consistent problem generation
- **Hardware**: Results may vary based on system performance

## Key Research Questions Addressed

1. **Scalability**: How does planning performance scale with problem size?
2. **Heuristic effectiveness**: Which heuristics work best for logistics planning?
3. **Constraint impact**: How do different constraints affect planning efficiency?
4. **Topology effects**: How does network structure influence planning?
5. **Weight distribution**: How do container weight patterns affect complexity?

## Future Extensions

- **Additional heuristics**: A*, IDA*, different search strategies
- **More constraints**: Time windows, energy constraints, multi-objective planning
- **Larger problems**: 50+ containers, 10+ robots, warehouse-scale scenarios
- **Real-world data**: Integration with actual logistics data and constraints
