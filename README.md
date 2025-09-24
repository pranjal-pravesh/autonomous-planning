# Automated Planning – Logistics Domain (Refactored)

This project models a logistics domain (robots, docks, piles, containers) using the Unified Planning (UP) library. The codebase is refactored to strictly separate the general domain from demo-specific problem instances.

## What’s New (Refactor Highlights)
- `src/domain.py` only defines general Types and Fluents. No hardcoded objects or initial states.
- `src/actions.py` defines general actions (`move`, `pickup`, `putdown`) that work for any problem instance.
- Demos are fully responsible for creating objects, setting initial state, goals, and calling `domain.assign_objects(...)`.
- All fluents are boolean for PDDL/UP compatibility; weights/capacities are represented via boolean levels.

## Quick Start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run Demos

Run any demo directly with Python (after activating the venv):

```bash
# Classic tricky weight rearrangement (19 steps)
python demos/tricky_weight_rearrangement.py

# Tricky swapping scenario (2 robots, all containers 2t)
python demos/tricky_swapping.py


## Architecture

- `src/domain.py`
  - Declares Types: `Robot`, `Dock`, `Container`, `Pile`.
  - Declares Fluents (all boolean), e.g. `robot_at`, `container_in_pile`, `robot_weight_4`, `robot_capacity_6`, etc.
  - Provides `assign_objects(objects_dict)` for demos to inject objects.
  - Provides `get_domain_objects()` for actions to query assigned objects.
  - No objects or initial states are created here.

- `src/actions.py`
  - Defines `move`, `pickup`, and `putdown` as `InstantaneousAction`s.
  - Enforces constraints: LIFO for piles and robot slots; weight and capacity limits; location and adjacency checks.
  - Uses `domain.get_domain_objects()` to iterate relevant objects (e.g., containers) without hardcoding names.

- Demos (`demos/*.py`)
  - Create objects locally: `Object("r1", domain.Robot)`, etc.
  - Call `domain.assign_objects({...})`.
  - Add fluents to the problem with `default_initial_value=False` (unspecified facts default to False).
  - Set initial values and goals, then solve with a UP planner (e.g., Fast Downward).

## Key Modeling Choices

### Fluents (All Boolean)
Examples:
- Location and carrying: `robot_at(r, d)`, `robot_carrying(r, c)`, `robot_free(r)`
- Capacity slots: `robot_can_carry_1/2/3`, `robot_has_container_1/2/3`, `container_in_robot_slot_1/2/3`
- Pile relations: `container_in_pile(c, p)`, `container_on_top_of_pile(c, p)`, `container_under_in_pile(c, c2, p)`
- Weights (levels): `container_weight_2/4/6(c)`, `robot_weight_0/2/4/6/8/10(r)`
- Capacity (levels): `robot_capacity_5/6/8/10(r)`
- Static relation: `adjacent(d1, d2)`

Why boolean? It keeps the model compatible with standard PDDL-style planning and widely supported heuristics.

### default_initial_value=False
When adding fluents to a problem, we use `default_initial_value=False`. Any fact not explicitly set in the initial state is assumed False, which keeps demos concise.

## State Space (Conceptual)
- A state is a complete assignment of all fluents (True/False).
- The theoretical state space size is `2^N` where `N` is the number of boolean fluent instances (after grounding by objects).
- Constraints (mutual exclusivity, LIFO, capacities, weights, adjacency) make most of those states unreachable. Planners use heuristics to explore only a tiny fraction.

## Adding a New Demo (Template)
1. Import domain/actions and create a domain instance:
   ```python
   domain = LogisticsDomain(auto_objects=False)
   problem = Problem("my_scenario")
   ```
2. Create objects and register them with the problem.
3. Call `domain.assign_objects({...})` with your created objects.
4. Add all domain fluents and static fluents:
   ```python
   for f in domain.fluents + domain.static_fluents:
       problem.add_fluent(f, default_initial_value=False)
   ```
5. Instantiate and add actions:
   ```python
   actions = LogisticsActions(domain)
   for a in actions.get_actions():
       problem.add_action(a)
   ```
6. Set initial state values and goals. Solve with a UP planner.

## Project Structure (Key Files)

```
automated-planning/
├── demos/
│   ├── tricky_weight_challenge.py
│   ├── tricky_swapping.py
│   ├── tricky_weight_arrangement.py
│   ├── container_redistribution.py
│   ├── large_scale_redistribution.py
│   ├── multi_robot_coordination.py
│   ├── boolean_weight_demo.py
│   └── robot_capacity_test.py
├── src/
│   ├── domain.py
│   ├── actions.py
│   ├── problem.py
│   └── solver.py
├── utils/
│   └── display.py
├── requirements.txt
└── README.md
```

## Planner
We typically use Fast Downward via UP’s `OneshotPlanner`. You can swap planners if installed.

---

If something doesn’t run or you want a new scenario added, open an issue or ask for a demo stub following the template above.
