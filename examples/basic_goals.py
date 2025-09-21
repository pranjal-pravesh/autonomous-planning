"""
Basic goal examples for the logistics domain.
Demonstrates simple planning goals and their solutions.
"""

from unified_planning.shortcuts import *
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.problem import LogisticsProblem
from src.solver import LogisticsSolver


def example_1_move_robot():
    """Example 1: Move robot r1 to dock d3."""
    print("=" * 60)
    print("EXAMPLE 1: Move robot r1 to dock d3")
    print("=" * 60)
    
    problem_setup = LogisticsProblem()
    problem = problem_setup.create_problem("move_robot_example")
    problem_setup.create_robot_location_goal(problem_setup.domain.r1, problem_setup.domain.d3)
    
    solver = LogisticsSolver()
    result = solver.solve_and_display(problem)
    
    return result


def example_2_move_container():
    """Example 2: Move container c1 to pile p2."""
    print("=" * 60)
    print("EXAMPLE 2: Move container c1 to pile p2")
    print("=" * 60)
    
    problem_setup = LogisticsProblem()
    problem = problem_setup.create_problem("move_container_example")
    problem_setup.create_container_pile_goal(problem_setup.domain.c1, problem_setup.domain.p2)
    
    solver = LogisticsSolver()
    result = solver.solve_and_display(problem)
    
    return result


def example_3_robot_carrying_container():
    """Example 3: Get robot r1 to carry container c1."""
    print("=" * 60)
    print("EXAMPLE 3: Get robot r1 to carry container c1")
    print("=" * 60)
    
    problem_setup = LogisticsProblem()
    problem = problem_setup.create_problem("robot_carrying_example")
    problem_setup.create_container_position_goal(problem_setup.domain.c1, problem_setup.domain.r1)
    
    solver = LogisticsSolver()
    result = solver.solve_and_display(problem)
    
    return result


def example_4_complex_goal():
    """Example 4: Complex goal - Move r1 to d3 AND move c1 to p2."""
    print("=" * 60)
    print("EXAMPLE 4: Complex goal - Move r1 to d3 AND move c1 to p2")
    print("=" * 60)
    
    problem_setup = LogisticsProblem()
    problem = problem_setup.create_problem("complex_goal_example")
    
    goals = [
        problem_setup.domain.loc(problem_setup.domain.r1) == problem_setup.domain.d3,
        problem_setup.domain.pile(problem_setup.domain.c1) == problem_setup.domain.p2
    ]
    problem_setup.create_complex_goal(goals)
    
    solver = LogisticsSolver()
    result = solver.solve_and_display(problem)
    
    return result


def run_all_examples():
    """Run all basic goal examples."""
    examples = [
        example_1_move_robot,
        example_2_move_container,
        example_3_robot_carrying_container,
        example_4_complex_goal
    ]
    
    results = []
    for example_func in examples:
        try:
            result = example_func()
            results.append(result)
            print("\n" + "=" * 60 + "\n")
        except Exception as e:
            print(f"Error in {example_func.__name__}: {e}")
            results.append(None)
    
    # Summary
    print("SUMMARY:")
    print("=" * 60)
    for i, (example_func, result) in enumerate(zip(examples, results), 1):
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"Example {i}: {example_func.__name__} - {status}")


if __name__ == "__main__":
    run_all_examples()
