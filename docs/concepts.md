## Concepts

### What is automated planning
- Automated planning is a branch of classical AI that searches over possible world configurations (states) to find a sequence of actions that achieves a goal from an initial state.
- It uses symbolic models (types, objects, fluents, actions) and search algorithms guided by heuristics instead of learning from data.

### What are we trying to do
- Model a logistics world with robots, docks, piles, and containers.
- Define general actions (move, pickup, putdown) that respect constraints like LIFO and weight/capacity.
- Build demo problems that instantiate the world (objects, initial state, goals) and solve them using a UP planner.

### What is the scope of our project (research perspective)
- **Research questions**:
  - How far can a purely symbolic, boolean-fluent logistics model (with weights and LIFO) scale before heuristics degrade?
  - What is the empirical impact of explicit LIFO and weight-capacity modeling on planner performance and plan quality?
  - How does problem structure (dock topology, pile imbalance, object counts) influence heuristic accuracy and search effort?
- **Methodology / approach**:
  - Construct controlled benchmark families (vary robots/docks/containers/piles; vary weight/capacity distributions; vary adjacency graphs).
  - Use standardized planners (e.g., Fast Downward via UP) and compare heuristics (GBFS/A*, FF, h_add, h_max if available).
  - Record metrics: time-to-solve, nodes expanded, plan length, memory, and success rate.
- **Intended contributions**:
  - A clear, domain-agnostic UP-based modeling template separating domain vs. instance.
  - Reproducible logistics benchmarks stressing LIFO and weight-capacity interactions.
  - Initial empirical characterization of heuristic behavior under stacking and capacity constraints.
- **Evaluation plan**:
  - Sweep instance sizes and structural parameters; run multiple seeds where applicable.
  - Compare plan lengths against known baselines (e.g., 19-step tricky rearrangement) to verify correctness.
  - Analyze scaling curves and failure modes; identify bottlenecks due to constraint interactions.
- **Out-of-scope (current phase)**:
  - Learning-based planners or RL; numeric fluents beyond boolean encodings; temporal/continuous planning; execution under uncertainty.
- **Future directions**:
  - Hybrid numeric modeling (integer weights/capacities) and comparison with boolean encodings.
  - Learned heuristics or portfolio selection; symmetry breaking; domain-specific pruning.
  - Larger synthetic and real-world graphs; partial observability; online replanning.

### State Domain, Action domain, Algorithms, heuristics
- **State domain**: The set of all possible assignments of fluents (True/False). A single state is a complete snapshot of the world.
- **Action domain**: Parameterized operators with preconditions and effects (InstantaneousAction in UP): `move(r, d, d')`, `pickup(r, c, p, d)`, `putdown(r, c, p, d)`.
- **Algorithms**: Forward state-space search using planners like Fast Downward (via UP). Common strategies: A*, Greedy Best-First Search (GBFS), breadth-first variants.
- **Heuristics**: Goal-distance estimators that guide search (e.g., delete-relaxation-based heuristics such as h_max, h_add, FF). They help avoid exploring the full exponential state space.

### Progress
- Added boolean modeling for container weights (2t, 4t, 6t).
- Added robot slot capacity (up to 3 slots) and slot occupancy tracking.
- Added robot weight capacity levels (5t, 6t, 8t, 10t) and weight accumulation.
- Enforced LIFO for stacks both on piles and in robot slots.
- Expanded demos to include more docks, containers, and unequal pile sizes per dock.


