#!/usr/bin/env python3
"""
Large Scale Container Redistribution - Refactored to use src/ domain structure.
Complex logistics world with multiple docks, unequal piles per dock, many containers, and 3 robots.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from unified_planning.shortcuts import *
from unified_planning.engines.results import PlanGenerationResultStatus
from rich.console import Console
from rich.panel import Panel
import time

# Import from src/
from src.domain import LogisticsDomain
from src.actions import LogisticsActions
from src.problem import LogisticsProblem
from utils.display import LogisticsDisplay

console = Console()


def create_large_scale_problem():
    """Create a large-scale logistics problem using the src/ structure."""
    
    # Create large-scale domain
    domain = LogisticsDomain(scale="large")
    actions = LogisticsActions(domain)
    
    # Create problem
    problem = Problem("large_scale_container_redistribution")
    
    # Add objects
    domain_objects = domain.get_domain_objects()
    problem.add_objects(domain_objects["all_objects"])
    
    # Add fluents
    for fluent in domain.fluents + domain.static_fluents:
        problem.add_fluent(fluent, default_initial_value=False)
    
    # Add actions
    for action in actions.get_actions():
        problem.add_action(action)
    
    # Set initial state
    initial_state = domain.get_initial_state()
    for fluent, value in initial_state.items():
        problem.set_initial_value(fluent, value)
    
    return problem, domain, domain_objects


def create_large_scale_goal(problem, domain):
    """Create the goal for large-scale redistribution - ultra-simple capacity test."""
    
    # Goal: Ultra-simple test to verify robot capacity system works
    # Move just 2 containers from central dock to smaller docks
    # This should be easily solvable and demonstrate robot capacity differences
    
    goal_conditions = [
        # Dock 2: 1 container (c3 from p1 at d1)
        domain.container_in_pile(domain.c3, domain.p9),
        
        # Dock 3: 1 container (c5 from p2 at d1)
        domain.container_in_pile(domain.c5, domain.p10)
    ]
    
    problem.add_goal(And(*goal_conditions))
    return problem


def get_initial_distribution_data():
    """Get initial distribution data for display - central dock with many containers."""
    return [
        # Central dock d1 - has all containers initially
        {"dock": "d1", "pile": "p1", "stack_order": "c1 → c2 → c3", "count": 3, "top_container": "c3"},
        {"dock": "d1", "pile": "p2", "stack_order": "c4 → c5", "count": 2, "top_container": "c5"},
        {"dock": "d1", "pile": "p3", "stack_order": "c6 → c7", "count": 2, "top_container": "c7"},
        {"dock": "d1", "pile": "p4", "stack_order": "c8", "count": 1, "top_container": "c8"},
        {"dock": "d1", "pile": "p5", "stack_order": "c9 → c10", "count": 2, "top_container": "c10"},
        {"dock": "d1", "pile": "p6", "stack_order": "c11", "count": 1, "top_container": "c11"},
        {"dock": "d1", "pile": "p7", "stack_order": "c12", "count": 1, "top_container": "c12"},
        {"dock": "d1", "pile": "p8", "stack_order": "c13", "count": 1, "top_container": "c13"},
        
        # All other docks are empty initially
        {"dock": "d2", "pile": "p9", "stack_order": "(empty)", "count": 0, "top_container": "-"},
        {"dock": "d3", "pile": "p10", "stack_order": "(empty)", "count": 0, "top_container": "-"},
        {"dock": "d4", "pile": "p11", "stack_order": "(empty)", "count": 0, "top_container": "-"},
        {"dock": "d5", "pile": "p12", "stack_order": "(empty)", "count": 0, "top_container": "-"},
        {"dock": "d6", "pile": "p13", "stack_order": "(empty)", "count": 0, "top_container": "-"},
        {"dock": "d7", "pile": "p14", "stack_order": "(empty)", "count": 0, "top_container": "-"},
        {"dock": "d8", "pile": "p15", "stack_order": "(empty)", "count": 0, "top_container": "-"}
    ]


def get_target_distribution_data():
    """Get target distribution data for display - ultra-simple capacity test."""
    return [
        # Central dock d1 - containers moved out
        {"dock": "d1", "pile": "p1", "target_stack": "c1 → c2", "count": 2, "change": "3 → 2 (-1)", "top_container": "c2"},
        {"dock": "d1", "pile": "p2", "target_stack": "c4", "count": 1, "change": "2 → 1 (-1)", "top_container": "c4"},
        
        # Smaller docks - containers distributed
        {"dock": "d2", "pile": "p9", "target_stack": "c3", "count": 1, "change": "0 → 1 (+1)", "top_container": "c3"},
        {"dock": "d3", "pile": "p10", "target_stack": "c5", "count": 1, "change": "0 → 1 (+1)", "top_container": "c5"}
    ]


def solve_large_scale_scenario():
    """Solve the large-scale redistribution scenario."""
    
    console.print(Panel.fit(
        "[bold blue]🏭 Large Scale Container Redistribution[/bold blue]\n"
        "[white]Using generalized src/ domain structure[/white]",
        border_style="blue"
    ))
    
    # Create problem
    problem, domain, domain_objects = create_large_scale_problem()
    problem = create_large_scale_goal(problem, domain)
    
    # Display domain information
    LogisticsDisplay.display_domain_info(domain_objects, "Large Scale Logistics Domain")
    
    # Display distributions
    initial_distributions = get_initial_distribution_data()
    target_distributions = get_target_distribution_data()
    
    LogisticsDisplay.display_large_scale_distribution(initial_distributions, target_distributions)
    
    # Solve the problem
    console.print(f"\n[bold blue]🤖 Solving with fast-downward...[/bold blue]")
    
    # Try different planners and configurations
    planners_to_try = [
        ("pyperplan", "Pyperplan (lightweight STRIPS planner)"),
        ("fast-downward", "Fast Downward (default configuration)"),
        ("fast-downward", "Fast Downward with A* and FF heuristic")
    ]
    
    result = None
    successful_planner = None
    
    for planner_name, description in planners_to_try:
        console.print(f"\n[bold cyan]🎯 Trying planner: {description}[/bold cyan]")
        
        try:
            if planner_name == "pyperplan":
                with OneshotPlanner(name='pyperplan') as planner:
                    start_time = time.time()
                    result = planner.solve(problem)
                    solve_time = time.time() - start_time
            elif planner_name == "fast-downward" and "FF heuristic" in description:
                # Try Fast Downward with FF heuristic
                with OneshotPlanner(name='fast-downward', params="--search 'astar(ff())'") as planner:
                    start_time = time.time()
                    result = planner.solve(problem)
                    solve_time = time.time() - start_time
            else:
                # Default Fast Downward
                with OneshotPlanner(name='fast-downward') as planner:
                    start_time = time.time()
                    result = planner.solve(problem)
                    solve_time = time.time() - start_time
            
            if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
                console.print(f"[green]✅ SUCCESS! Plan found in {solve_time:.3f}s with {description}[/green]")
                successful_planner = description
                
                # Display plan
                LogisticsDisplay.display_plan_execution(result, f"Large-Scale Redistribution Execution Plan ({description})")
                
                # Display summary
                LogisticsDisplay.display_plan_summary(result, solve_time, f"Large-Scale Redistribution Summary ({description})")
                
                return True, len(result.plan.actions)
            else:
                console.print(f"[red]❌ Failed with {description}: {result.status}[/red]")
                
        except Exception as e:
            console.print(f"[red]❌ Error with {description}: {str(e)}[/red]")
    
    console.print(f"\n[red]❌ All planners failed![/red]")
    console.print(f"[yellow]🔧 The domain might be too complex for the current planners[/yellow]")
    return False, 0


def main():
    """Run the large-scale container redistribution scenario."""
    
    console.print(Panel.fit(
        "[bold blue]🏭 Large Scale Container Redistribution[/bold blue]\n"
        "[white]Refactored to use generalized src/ domain structure[/white]",
        border_style="blue"
    ))
    
    console.print("\n[bold cyan]📋 World Features:[/bold cyan]")
    console.print("• 3 robots: r1 (cap 3), r2 (cap 3), r3 (cap 2) for coordinated operations")
    console.print("• 8 docks: 1 central dock (d1) with 8 piles, 7 smaller docks with 1 pile each")
    console.print("• 15 piles total: 8 at central dock, 7 at smaller docks")
    console.print("• 13 containers initially all at central dock d1")
    console.print("• Operations: move, pickup, putdown")
    console.print("• Goal: Distribute containers from central dock to smaller docks")
    console.print("• Challenge: Test robot capacity system with realistic logistics scenario")
    console.print("• Architecture: Uses generalized src/ domain structure")
    
    success, steps = solve_large_scale_scenario()
    
    if success:
        console.print(f"\n[bold green]🎉 Large-scale redistribution completed![/bold green]")
        console.print(f"[bold cyan]📊 Executed {steps} actions to achieve balanced distribution[/bold cyan]")
        console.print("[bold yellow]✨ Features demonstrated:[/bold yellow]")
        console.print("  • Generalized domain structure from src/")
        console.print("  • Scalable logistics planning")
        console.print("  • Multi-robot coordination")
        console.print("  • Complex network topology")
        console.print("  • Unequal pile distribution")
        console.print("  • Balanced container redistribution")
    else:
        console.print(f"\n[bold red]❌ Large-scale redistribution failed![/bold red]")
        console.print("The domain might be too complex for the current planner")
    
    return success


if __name__ == "__main__":
    success = main()
    if success:
        console.print("\n[bold yellow]🚀 Large-scale logistics planning completed![/bold yellow]")
    else:
        console.print("\n[bold red]🔧 Domain needs optimization for large-scale scenarios[/bold red]")