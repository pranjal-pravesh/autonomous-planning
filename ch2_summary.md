# CH2 – Deliberation with Deterministic Models (Quick Reference)

## 1) State-Variable Modeling
- **Universe of objects & rigid facts.** Choose a finite set **B** (robots, docks, containers, piles, Booleans, `nil`) and rigid relations like `adjacent(d,d')`, `at(p,d)`.
- **State variables X.** Typical set for the toy domain:  
  `cargo(r)`, `loc(r)`, `occupied(d)`, `pos(c)`, `pile(c)`, `top(p)` with finite ranges.  
- **Initial state example (Eq. 2.4).** Two robots at docks d1,d2; occupancy, piles/stacks and tops enumerated.

## 2) Actions (State-Variable Form)
- **Template form:** `act(...) pre: ... eff: ... cost: ...`
- **Toy domain actions (Example 2.12):** `load`, `unload`, `move` with explicit preconditions/effects.

## 3) Forward State-Space Search Algorithms
- **Uniform-Cost Search (UCS):** Optimal, exponential time/memory.  
- **A\***: Optimal with admissible h, pruning duplicates.  
- **DFBB:** Memory-light, DFS with bound, can recompute.  
- **GBFS:** Fast with good h, not optimal.  
- **IDS / IDA\***: Low memory, revisits states often.

## 4) Heuristic Functions
- **Admissibility & dominance.**  
- **Relaxed-planning heuristics:** `h_max`, `h_add`, **h_FF**.  
- **Landmark heuristics:** discover mandatory disjunctive formulas.

## 5) Practical Optimizations
- Duplicate detection, cycle checking.  
- Anytime/limits, randomized/hill-climbing variants.

## 6) Classical (STRIPS-style) View
- Represent states as sets of atoms; operators with add/delete effects (STRIPS).  
