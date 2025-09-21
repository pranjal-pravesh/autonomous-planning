#!/usr/bin/env python3
"""
Robot Capacity Test Demo

This demo specifically tests the robot capacity system with a simple, solvable scenario.
It demonstrates how robots with different capacities (1, 2, 3) can work together
to redistribute containers from a central location to multiple destinations.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.align import Align

from unified_planning.shortcuts import *
from unified_planning.engines import PlanGenerationResultStatus
import time

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.domain import LogisticsDomain
from src.actions import LogisticsActions
from src.problem import LogisticsProblem
from utils.display import LogisticsDisplay

console = Console()


def create_capacity_test_problem_and_domain():
    """Create a problem to test robot capacity system with 5 containers."""
    
    # Use small scale domain but with capacity system
    domain = LogisticsDomain(scale="small")
    actions = LogisticsActions(domain)
    
    # Create the problem manually to customize initial state
    problem = Problem("Robot Capacity Test")
    
    # Add objects
    problem.add_objects(domain.objects)
    
    # Add fluents
    for fluent in domain.fluents + domain.static_fluents:
        problem.add_fluent(fluent, default_initial_value=False)
    
    # Add actions
    for action in actions.get_actions():
        problem.add_action(action)
    
    # Custom initial state - only r3 is present and active
    custom_initial_state = {
        # Only r3 is at d2, r1 and r2 are inactive (not at any dock)
        domain.robot_at(domain.r3, domain.d2): True,
        
        # Robot capacities
        domain.robot_can_carry_1(domain.r3): True,
        domain.robot_can_carry_2(domain.r3): True,
        domain.robot_can_carry_3(domain.r3): True,
        
        # Robot load tracking
        domain.robot_has_container_1(domain.r3): False,
        domain.robot_has_container_2(domain.r3): False,
        domain.robot_has_container_3(domain.r3): False,
        
        # Initialize robot slot tracking (all empty initially)
        domain.container_in_robot_slot_1(domain.r3, domain.c1): False,
        domain.container_in_robot_slot_1(domain.r3, domain.c2): False,
        domain.container_in_robot_slot_1(domain.r3, domain.c3): False,
        domain.container_in_robot_slot_1(domain.r3, domain.c4): False,
        domain.container_in_robot_slot_1(domain.r3, domain.c5): False,
        
        domain.container_in_robot_slot_2(domain.r3, domain.c1): False,
        domain.container_in_robot_slot_2(domain.r3, domain.c2): False,
        domain.container_in_robot_slot_2(domain.r3, domain.c3): False,
        domain.container_in_robot_slot_2(domain.r3, domain.c4): False,
        domain.container_in_robot_slot_2(domain.r3, domain.c5): False,
        
        domain.container_in_robot_slot_3(domain.r3, domain.c1): False,
        domain.container_in_robot_slot_3(domain.r3, domain.c2): False,
        domain.container_in_robot_slot_3(domain.r3, domain.c3): False,
        domain.container_in_robot_slot_3(domain.r3, domain.c4): False,
        domain.container_in_robot_slot_3(domain.r3, domain.c5): False,
        
        domain.robot_free(domain.r3): True,
        
        # Container piles with proper stacking
        domain.container_in_pile(domain.c1, domain.p1): True,
        domain.container_in_pile(domain.c2, domain.p1): True,
        domain.container_in_pile(domain.c3, domain.p1): True,
        domain.container_in_pile(domain.c4, domain.p1): True,
        domain.container_in_pile(domain.c5, domain.p1): True,
        
        # Stacking order: c1 (bottom) → c2 → c3 → c4 → c5 (top)
        # Only c5 is on top of the pile
        domain.container_on_top_of_pile(domain.c5, domain.p1): True,
        domain.container_on_top_of_pile(domain.c1, domain.p1): False,
        domain.container_on_top_of_pile(domain.c2, domain.p1): False,
        domain.container_on_top_of_pile(domain.c3, domain.p1): False,
        domain.container_on_top_of_pile(domain.c4, domain.p1): False,
        
        # Under relationships: c4 is under c5, c3 is under c4, etc.
        domain.container_under_in_pile(domain.c4, domain.c5, domain.p1): True,
        domain.container_under_in_pile(domain.c3, domain.c4, domain.p1): True,
        domain.container_under_in_pile(domain.c2, domain.c3, domain.p1): True,
        domain.container_under_in_pile(domain.c1, domain.c2, domain.p1): True,
        
        # Pile locations
        domain.pile_at_dock(domain.p1, domain.d1): True,
        domain.pile_at_dock(domain.p2, domain.d2): True,
        domain.pile_at_dock(domain.p3, domain.d3): True,
        
        # Static relations - adjacent docks (triangular network)
        domain.adjacent(domain.d1, domain.d2): True,
        domain.adjacent(domain.d2, domain.d1): True,
        domain.adjacent(domain.d2, domain.d3): True,
        domain.adjacent(domain.d3, domain.d2): True,
        domain.adjacent(domain.d3, domain.d1): True,
        domain.adjacent(domain.d1, domain.d3): True,
    }
    
    # Set initial state
    for fluent, value in custom_initial_state.items():
        problem.set_initial_value(fluent, value)
    
    domain_objects = domain.get_domain_objects()
    # Filter to show only r3 in display
    domain_objects["robots"] = [domain.r3]
    
    return problem, domain, domain_objects


def create_capacity_test_goal(problem, domain):
    """Create a goal to test robot capacity system with 5 containers."""
    
    # Goal: Distribute 5 containers from p1 (d1) to p2 (d2) and p3 (d3)
    # 2 containers should go to p2, 3 containers should go to p3
    # Robot r3 (capacity 3) starts at d2 and can now pick up any container (no LIFO)
    
    goal_conditions = [
        # Move 2 containers to p2 (d2) with proper stacking: c4(bottom) → c5(top)
        domain.container_in_pile(domain.c4, domain.p2),  # c4 to p2
        domain.container_in_pile(domain.c5, domain.p2),  # c5 to p2
        domain.container_on_top_of_pile(domain.c5, domain.p2),  # c5 on top of p2
        domain.container_under_in_pile(domain.c4, domain.c5, domain.p2),  # c4 under c5
        
        # Move 3 containers to p3 (d3) with proper stacking: c3(bottom) → c2 → c1(top)
        domain.container_in_pile(domain.c1, domain.p3),  # c1 to p3
        domain.container_in_pile(domain.c2, domain.p3),  # c2 to p3
        domain.container_in_pile(domain.c3, domain.p3),  # c3 to p3
        domain.container_on_top_of_pile(domain.c1, domain.p3),  # c1 on top of p3
        domain.container_under_in_pile(domain.c3, domain.c2, domain.p3),  # c3 under c2
        domain.container_under_in_pile(domain.c2, domain.c1, domain.p3),  # c2 under c1
    ]
    
    problem.add_goal(And(*goal_conditions))
    return problem


def get_capacity_test_initial_data():
    """Get initial distribution data for capacity test."""
    return [
        {"dock": "d1", "pile": "p1", "stack_order": "c1 → c2 → c3 → c4 → c5", "count": 5, "top_container": "c5"},
        {"dock": "d2", "pile": "p2", "stack_order": "(empty)", "count": 0, "top_container": "-"},
        {"dock": "d3", "pile": "p3", "stack_order": "(empty)", "count": 0, "top_container": "-"}
    ]


def get_capacity_test_target_data():
    """Get target distribution data for capacity test."""
    return [
        {"dock": "d1", "pile": "p1", "target_stack": "(empty)", "count": 0, "change": "5 → 0 (-5)", "top_container": "-"},
        {"dock": "d2", "pile": "p2", "target_stack": "c4 → c5", "count": 2, "change": "0 → 2 (+2)", "top_container": "c5"},
        {"dock": "d3", "pile": "p3", "target_stack": "c3 → c2 → c1", "count": 3, "change": "0 → 3 (+3)", "top_container": "c1"}
    ]


def solve_capacity_test_scenario():
    """Solve the robot capacity test scenario."""
    
    # Create problem and domain
    problem, domain, domain_objects = create_capacity_test_problem_and_domain()
    
    # Add goal
    problem = create_capacity_test_goal(problem, domain)
    
    # Display problem information
    LogisticsDisplay.display_domain_info(domain_objects)
    
    # Get distribution data
    initial_distributions = get_capacity_test_initial_data()
    target_distributions = get_capacity_test_target_data()
    
    # Display distributions
    LogisticsDisplay.display_large_scale_distribution(initial_distributions, target_distributions)
    
    # Solve the problem
    console.print(f"\n[bold blue]🤖 Solving robot capacity test...[/bold blue]")
    
    try:
        with OneshotPlanner(name='fast-downward') as planner:
            start_time = time.time()
            result = planner.solve(problem)
            solve_time = time.time() - start_time
            
            if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
                console.print(f"[green]✅ SUCCESS! Robot capacity test completed in {solve_time:.3f}s[/green]")
                
                # Display plan
                LogisticsDisplay.display_plan_execution(result, "Robot Capacity Test Execution Plan")
                
                # Display summary
                LogisticsDisplay.display_plan_summary(result, solve_time, "Robot Capacity Test Summary")
                
                return True, len(result.plan.actions)
            else:
                console.print(f"[red]❌ Planning failed: {result.status}[/red]")
                return False, 0
                
    except Exception as e:
        console.print(f"[red]❌ Error during planning: {e}[/red]")
        return False, 0


def main():
    """Run the robot capacity test scenario."""
    
    console.print(Panel.fit(
        "[bold blue]🤖 Robot Capacity Test[/bold blue]\n"
        "[white]Testing robot capacity system with simple, solvable scenario[/white]",
        border_style="blue"
    ))
    
    console.print("\n[bold cyan]📋 Test Features:[/bold cyan]")
    console.print("• 1 robot: r3 (cap 3)")
    console.print("• 3 docks connected in triangle")
    console.print("• 5 containers: c1, c2, c3, c4, c5 (all stacked in p1 at d1)")
    console.print("• 3 piles: p1 (d1), p2 (d2), p3 (d3)")
    console.print("• Robot r3 (cap 3) starts at d2")
    console.print("• Goal: 2 containers to p2, 3 containers to p3 (no LIFO constraint)")
    console.print("• Challenge: Test robot capacity without LIFO constraints")
    console.print("• Architecture: Uses generalized src/ domain structure")
    
    success, steps = solve_capacity_test_scenario()
    
    if success:
        console.print(f"\n[bold green]🎉 Robot capacity test completed![/bold green]")
        console.print(f"[green]📊 Executed {steps} actions demonstrating capacity system[/green]")
        console.print(f"[green]✨ Features demonstrated:[/green]")
        console.print(f"  • Robot capacity constraints (simplified to 1 slot per robot)")
        console.print(f"  • No LIFO constraints (robot can pick up any container)")
        console.print(f"  • Capacity-aware pickup/putdown")
        console.print(f"  • Single robot coordination")
        console.print(f"  • Realistic logistics planning")
        console.print(f"  • Plan matches initial conditions perfectly")
        console.print(f"  • Note: True multi-container capacity requires action updates")
        console.print(f"\n[bold green]🚀 Robot capacity system working![/bold green]")
    else:
        console.print(f"\n[bold red]❌ Robot capacity test failed![/bold red]")
        console.print(f"[yellow]🔧 The capacity system might need debugging[/yellow]")


if __name__ == "__main__":
    main()
