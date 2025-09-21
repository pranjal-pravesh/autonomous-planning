# Automated Planning - Example 2.3 Simulation

A B.Tech project implementing the logistics domain from **Example 2.3** in *Automated Planning and Acting* by Ghallab, Nau, and Traverso.

## Overview

This project simulates a logistics domain with:
- **Multiple Loading Docks** connected in various network topologies
- **Robots with Different Capacities** (1, 2, or 3 containers) that can move between docks
- **Containers** that can be stacked in piles or carried by robots
- **Piles** located at specific docks for container storage
- **LIFO Stacking System** for realistic container handling

## Domain Description

### Objects
- **Robots**: r1 (capacity 1), r2 (capacity 2), r3 (capacity 3)
- **Docks**: Multiple docks with various connectivity patterns
- **Containers**: Multiple containers for redistribution scenarios
- **Piles**: Located at specific docks for container storage

### State Variables
- `robot_at(r, d)`: Whether robot r is at dock d
- `robot_carrying(r, c)`: Whether robot r is carrying container c
- `robot_free(r)`: Whether robot r is free to pick up containers
- `robot_can_carry_X(r)`: Whether robot r can carry X containers (1, 2, or 3)
- `robot_has_container_X(r)`: Whether robot r has container in slot X
- `container_in_pile(c, p)`: Whether container c is in pile p
- `pile_at_dock(p, d)`: Whether pile p is at dock d
- `adjacent(d1, d2)`: Whether dock d1 is adjacent to dock d2

### Actions
- **pickup(r, c, p, d)**: Robot r picks up container c from pile p at dock d (capacity-aware)
- **putdown(r, c, p, d)**: Robot r puts down container c onto pile p at dock d (LIFO)
- **move(r, d1, d2)**: Robot r moves from dock d1 to adjacent dock d2

## Robot Capacity System

The project implements a realistic robot capacity system:

### Capacity Types
- **r1**: Capacity 1 - Can carry 1 container
- **r2**: Capacity 2 - Can carry up to 2 containers  
- **r3**: Capacity 3 - Can carry up to 3 containers

### LIFO Stacking
- **Last In, First Out**: New containers are stacked on top
- **Unloading Constraint**: Only the top container can be unloaded
- **Realistic Operations**: Mimics real-world container handling

### Capacity Constraints
- Robots can only pick up containers if they have available capacity
- Load tracking prevents overloading
- Efficient multi-container transport for high-capacity robots

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Simulation
```bash
python main.py run
```

### List Available Problems
```bash
python main.py run --list
```

### Run Specific Problem
```bash
python main.py run --problem move_robot --planner fast-downward
```

### Interactive Mode
```bash
python main.py interactive
```

### Advanced Demos
```bash
python main.py demos
```

### Run All Examples
```bash
python main.py demo
```

## Project Structure

```
automated-planning/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── main.py                  # Main CLI interface
├── src/
│   ├── __init__.py
│   ├── domain.py            # Domain definition (types, objects, fluents)
│   ├── actions.py           # Action definitions
│   ├── problem.py           # Problem setup and initial state
│   └── solver.py            # Planning solver with rich output
├── examples/
│   ├── basic_goals.py       # Example goal definitions
│   └── complex_scenarios.py # More complex planning scenarios
├── demos/
│   ├── multi_robot_coordination.py    # Multi-robot coordination scenarios
│   ├── container_redistribution.py    # Container redistribution with piles and target counts
│   ├── large_scale_redistribution.py  # Large-scale redistribution with 8 docks, 12 piles, 15 containers, 3 robots
│   └── robot_capacity_demo.py         # Robot capacity demonstration (capacities 1, 2, 3 with LIFO stacking)
└── docs/
    ├── ch2_summary.md       # Chapter 2 theory summary
    ├── guide_up.md          # Unified Planning implementation guide
    └── project_context.md   # Project context and aims
```

## Example Output

The simulation provides rich console output showing:
- Initial state visualization
- Goal specification
- Planning process
- Found plan with step-by-step actions
- Final state verification

## Theory Background

This implementation is based on:
- **Chapter 2** of *Automated Planning and Acting*
- **Example 2.3** logistics domain
- **State-variable modeling** approach
- **Forward state-space search** algorithms

## Extensions

Future enhancements include:
- Multiple planning algorithms (UCS, A*, GBFS)
- Different heuristics (h_add, h_max, h_ff, landmarks)
- Scaling to more robots, docks, and containers
- Performance analysis and comparison
