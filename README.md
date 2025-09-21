# Automated Planning - Example 2.3 Simulation

A B.Tech project implementing the logistics domain from **Example 2.3** in *Automated Planning and Acting* by Ghallab, Nau, and Traverso.

## Overview

This project simulates a logistics domain with:
- **3 Loading Docks** (d1, d2, d3) connected in a triangular network
- **2 Robots** (r1, r2) that can move between docks and carry containers
- **3 Containers** (c1, c2, c3) that can be stacked in piles or carried by robots
- **3 Piles** (p1, p2, p3) located at specific docks for container storage

## Domain Description

### Objects
- **Robots**: r1, r2 (can hold at most one container each)
- **Docks**: d1, d2, d3 (at most one robot per dock)
- **Containers**: c1, c2, c3
- **Piles**: p1 (at d1), p2 (at d2), p3 (at d2)

### State Variables
- `cargo(r)`: Container that robot r is carrying (or nil)
- `loc(r)`: Dock where robot r is located
- `occupied(d)`: Whether dock d is occupied by a robot
- `pos(c)`: Where container c is located (robot, pile, or nil)
- `pile(c)`: Which pile container c is in (or nil)
- `top(p)`: Top container of pile p (or nil)

### Actions
- **load(r, c, c', p, d)**: Robot r loads container c from pile p at dock d
- **unload(r, c, c', p, d)**: Robot r unloads container c onto pile p at dock d
- **move(r, d, d')**: Robot r moves from dock d to adjacent dock d'

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Simulation
```bash
python main.py
```

### Custom Goals
```bash
python main.py --goal "loc(r1)=d3"
python main.py --goal "pile(c1)=p2"
```

### Different Planners
```bash
python main.py --planner pyperplan
python main.py --planner fast-downward
```

## Project Structure

```
automated-planning/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── main.py                  # Main simulation script
├── src/
│   ├── __init__.py
│   ├── domain.py            # Domain definition (types, objects, fluents)
│   ├── actions.py           # Action definitions
│   ├── problem.py           # Problem setup and initial state
│   └── solver.py            # Planning solver with rich output
├── examples/
│   ├── basic_goals.py       # Example goal definitions
│   └── complex_scenarios.py # More complex planning scenarios
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
