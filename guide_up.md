# Guide: Simulating Example 2.3 with Unified Planning

## 0) Install
```bash
pip install unified-planning
pip install up-pyperplan up-fast-downward
```

## 1) Model the domain
- Types: `Robot`, `Dock`, `Container`, `Pile`, plus `Nil`.
- Objects: r1, r2; d1–d3; c1–c3; p1–p3; nil.
- Static relations: `adjacent(d,d')`, `at(p,d)`.

### Fluents
- `cargo(r: Robot) -> ContainerOrNil`
- `loc(r: Robot) -> Dock`
- `occupied(d: Dock) -> Bool`
- `pos(c: Container) -> (Container|Robot|Nil)`
- `pile(c: Container) -> (Pile|Nil)`
- `top(p: Pile) -> (Container|Nil)`

### Actions
- **load(r,c,c',p,d):** Preconditions: at(p,d), cargo(r)=nil, loc(r)=d, pos(c)=c', top(p)=c.  
  Effects: cargo(r)=c, pile(c)=nil, pos(c)=r, top(p)=c'.

- **unload(r,c,c',p,d):** Preconditions: at(p,d), pos(c)=r, loc(r)=d, top(p)=c'.  
  Effects: cargo(r)=nil, pile(c)=p, pos(c)=c', top(p)=c.

- **move(r,d,d'):** Preconditions: adjacent(d,d'), loc(r)=d, occupied(d')=False.  
  Effects: loc(r)=d', occupied(d)=False, occupied(d')=True.

## 2) Initial State (Eq. 2.4)
- cargo(r1)=nil, cargo(r2)=nil  
- loc(r1)=d1, loc(r2)=d2  
- occupied(d1)=T, occupied(d2)=T, occupied(d3)=F  
- pile(c1)=p1, pile(c2)=p1, pile(c3)=p2  
- pos(c1)=c2, pos(c2)=nil, pos(c3)=nil  
- top(p1)=c1, top(p2)=c3, top(p3)=nil

## 3) Define Goals
Example: `loc(r1)=d3` OR `pile(c1)=p2` etc.

## 4) Solve
```python
from unified_planning.shortcuts import *

# Define problem, add fluents, objects, actions, init, goal
# Choose engine
with OneshotPlanner(name='pyperplan') as planner:
    result = planner.solve(problem)
    print(result.plan)
```

## 5) Extensions
- Add non-unit costs; run A* for cost-optimal.  
- Scale up: more robots, docks, containers.  
- Compare heuristics (h_add, h_ff, lmcut).  
- Export to PDDL and run Fast Downward.
