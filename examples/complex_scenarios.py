"""
Complex planning scenarios for the logistics domain.
Demonstrates more challenging planning problems with multiple constraints.
"""

from unified_planning.shortcuts import *
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.problem import LogisticsProblem
from src.solver import LogisticsSolver


def scenario_1_swap_containers():
    """Scenario 1: Swap positions of containers c1 and c3."""
    print("=" * 60)
    print("SCENARIO 1: Swap positions of containers c1 and c3")
    print("=" * 60)
    
    problem_setup = LogisticsProblem()
    problem = problem_setup.create_problem("swap_containers_scenario")
    
    # Goal: c1 should be where c3 is (p2), and c3 should be where c1 is (p1)
    goals = [
        problem_setup.domain.pile(problem_setup.domain.c1) == problem_setup.domain.p2,
        problem_setup.domain.pile(problem_setup.domain.c3) == problem_setup.domain.p1
    ]
    problem_setup.create_complex_goal(goals)
    
    solver = LogisticsSolver()
    result = solver.solve_and_display(problem)
    
    return result


def scenario_2_reorganize_piles():
    """Scenario 2: Reorganize all containers - c1 to p3, c2 to p2, c3 to p1."""
    print("=" * 60)
    print("SCENARIO 2: Reorganize all containers")
    print("=" * 60)
    
    problem_setup = LogisticsProblem()
    problem = problem_setup.create_problem("reorganize_piles_scenario")
    
    # Goal: Complete reorganization
    goals = [
        problem_setup.domain.pile(problem_setup.domain.c1) == problem_setup.domain.p3,
        problem_setup.domain.pile(problem_setup.domain.c2) == problem_setup.domain.p2,
        problem_setup.domain.pile(problem_setup.domain.c3) == problem_setup.domain.p1
    ]
    problem_setup.create_complex_goal(goals)
    
    solver = LogisticsSolver()
    result = solver.solve_and_display(problem)
    
    return result


def scenario_3_robot_coordination():
    """Scenario 3: Both robots end up at dock d3."""
    print("=" * 60)
    print("SCENARIO 3: Both robots end up at dock d3")
    print("=" * 60)
    
    problem_setup = LogisticsProblem()
    problem = problem_setup.create_problem("robot_coordination_scenario")
    
    # Goal: Both robots at d3
    goals = [
        problem_setup.domain.loc(problem_setup.domain.r1) == problem_setup.domain.d3,
        problem_setup.domain.loc(problem_setup.domain.r2) == problem_setup.domain.d3
    ]
    problem_setup.create_complex_goal(goals)
    
    solver = LogisticsSolver()
    result = solver.solve_and_display(problem)
    
    return result


def scenario_4_container_delivery():
    """Scenario 4: Deliver container c1 to dock d3 (robot must carry it there)."""
    print("=" * 60)
    print("SCENARIO 4: Deliver container c1 to dock d3")
    print("=" * 60)
    
    problem_setup = LogisticsProblem()
    problem = problem_setup.create_problem("container_delivery_scenario")
    
    # Goal: c1 should be at d3 (carried by a robot at d3)
    # This requires: robot at d3 AND robot carrying c1
    goals = [
        problem_setup.domain.loc(problem_setup.domain.r1) == problem_setup.domain.d3,
        problem_setup.domain.cargo(problem_setup.domain.r1) == problem_setup.domain.c1
    ]
    problem_setup.create_complex_goal(goals)
    
    solver = LogisticsSolver()
    result = solver.solve_and_display(problem)
    
    return result


def scenario_5_empty_all_piles():
    """Scenario 5: Empty all piles (all containers carried by robots)."""
    print("=" * 60)
    print("SCENARIO 5: Empty all piles")
    print("=" * 60)
    
    problem_setup = LogisticsProblem()
    problem = problem_setup.create_problem("empty_piles_scenario")
    
    # Goal: All containers should be carried by robots (not in piles)
    goals = [
        problem_setup.domain.pile(problem_setup.domain.c1) == problem_setup.domain.nil,
        problem_setup.domain.pile(problem_setup.domain.c2) == problem_setup.domain.nil,
        problem_setup.domain.pile(problem_setup.domain.c3) == problem_setup.domain.nil
    ]
    problem_setup.create_complex_goal(goals)
    
    solver = LogisticsSolver()
    result = solver.solve_and_display(problem)
    
    return result


def run_all_scenarios():
    """Run all complex scenarios."""
    scenarios = [
        scenario_1_swap_containers,
        scenario_2_reorganize_piles,
        scenario_3_robot_coordination,
        scenario_4_container_delivery,
        scenario_5_empty_all_piles
    ]
    
    results = []
    for scenario_func in scenarios:
        try:
            result = scenario_func()
            results.append(result)
            print("\n" + "=" * 60 + "\n")
        except Exception as e:
            print(f"Error in {scenario_func.__name__}: {e}")
            results.append(None)
    
    # Summary
    print("SCENARIOS SUMMARY:")
    print("=" * 60)
    for i, (scenario_func, result) in enumerate(zip(scenarios, results), 1):
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"Scenario {i}: {scenario_func.__name__} - {status}")


if __name__ == "__main__":
    run_all_scenarios()
