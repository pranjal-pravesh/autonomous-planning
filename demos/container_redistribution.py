#!/usr/bin/env python3
"""
Container Redistribution Demo - Refactored to use src/ domain structure.
Simple logistics scenario with 2 robots, 4 docks, 4 piles, and 6 containers.
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


def create_simple_redistribution_problem():
    """Create a simple container redistribution problem using the src/ structure."""
    
    # Create small-scale domain (we'll extend it for this demo)
    domain = LogisticsDomain(scale="small")
    actions = LogisticsActions(domain)
    
    # Create problem
    problem = Problem("simple_container_redistribution")
    
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


def create_simple_redistribution_goal(problem, domain):
    """Create the goal for simple redistribution."""
    
    # Goal: Redistribute containers to achieve better organization
    # Simple goal that works with the 3-container, 3-dock domain
    
    simple_goal_conditions = [
        # Move c1 from p1 to p2 (dock 2)
        domain.container_in_pile(domain.c1, domain.p2),
        # Keep c2 in p1 (dock 1) 
        domain.container_in_pile(domain.c2, domain.p1),
        # Keep c3 in p2 (dock 2) - now p2 will have both c1 and c3
        domain.container_in_pile(domain.c3, domain.p2),
    ]
    
    problem.add_goal(And(*simple_goal_conditions))
    return problem


def get_simple_initial_distribution_data():
    """Get initial distribution data for display."""
    return [
        {"dock": "d1", "pile": "p1", "containers": "c1, c2", "count": 2, "robot": "r1"},
        {"dock": "d2", "pile": "p2", "containers": "c3", "count": 1, "robot": "r2"},
        {"dock": "d2", "pile": "p3", "containers": "(empty)", "count": 0, "robot": "-"},
    ]


def get_simple_target_distribution_data():
    """Get target distribution data for display."""
    return [
        {"dock": "d1", "pile": "p1", "containers": "c2", "count": 1, "change": "2 → 1 (-1)", "reason": "Keep one container"},
        {"dock": "d2", "pile": "p2", "containers": "c1, c3", "count": 2, "change": "1 → 2 (+1)", "reason": "Consolidate containers"},
        {"dock": "d2", "pile": "p3", "containers": "(empty)", "count": 0, "change": "0 → 0 (0)", "reason": "Keep empty"},
    ]


def solve_simple_redistribution_scenario():
    """Solve the simple redistribution scenario."""
    
    console.print(Panel.fit(
        "[bold blue]📦 Simple Container Redistribution[/bold blue]\n"
        "[white]Using generalized src/ domain structure[/white]",
        border_style="blue"
    ))
    
    # Create problem
    problem, domain, domain_objects = create_simple_redistribution_problem()
    problem = create_simple_redistribution_goal(problem, domain)
    
    # Display domain information
    LogisticsDisplay.display_domain_info(domain_objects, "Simple Logistics Domain")
    
    # Display distributions
    initial_state = {
        "dock_distributions": get_simple_initial_distribution_data()
    }
    target_state = {
        "dock_distributions": get_simple_target_distribution_data()
    }
    
    LogisticsDisplay.display_initial_distribution(initial_state, "Initial Container Distribution")
    LogisticsDisplay.display_target_distribution(target_state, "Target Container Distribution")
    LogisticsDisplay.display_distribution_summary(initial_state, target_state)
    
    # Solve the problem
    console.print(f"\n[bold blue]🤖 Solving with fast-downward...[/bold blue]")
    
    try:
        with OneshotPlanner(name='fast-downward') as planner:
            start_time = time.time()
            result = planner.solve(problem)
            solve_time = time.time() - start_time
            
            if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
                console.print(f"[green]✅ SUCCESS! Simple redistribution plan found in {solve_time:.3f}s[/green]")
                
                # Display plan
                LogisticsDisplay.display_plan_execution(result, "Simple Redistribution Execution Plan")
                
                # Display summary
                LogisticsDisplay.display_plan_summary(result, solve_time, "Simple Redistribution Summary")
                
                return True, len(result.plan.actions)
            else:
                console.print(f"[red]❌ Planning failed: {result.status}[/red]")
                return False, 0
                
    except Exception as e:
        console.print(f"[red]❌ Error during planning: {e}[/red]")
        return False, 0


def main():
    """Run the simple container redistribution scenario."""
    
    console.print(Panel.fit(
        "[bold blue]📦 Simple Container Redistribution[/bold blue]\n"
        "[white]Refactored to use generalized src/ domain structure[/white]",
        border_style="blue"
    ))
    
    console.print("\n[bold cyan]📋 World Features:[/bold cyan]")
    console.print("• 2 robots (r1, r2) for coordinated operations")
    console.print("• 3 docks with triangular connectivity")
    console.print("• 3 piles with containers")
    console.print("• 3 containers for redistribution")
    console.print("• Operations: move, pickup, putdown")
    console.print("• Goal: Redistribute containers for better organization")
    console.print("• Architecture: Uses generalized src/ domain structure")
    
    success, steps = solve_simple_redistribution_scenario()
    
    if success:
        console.print(f"\n[bold green]🎉 Simple redistribution completed![/bold green]")
        console.print(f"[bold cyan]📊 Executed {steps} actions to achieve target distribution[/bold cyan]")
        console.print("[bold yellow]✨ Features demonstrated:[/bold yellow]")
        console.print("  • Generalized domain structure from src/")
        console.print("  • Simple logistics planning")
        console.print("  • Multi-robot coordination")
        console.print("  • Container redistribution")
        console.print("  • Clean separation of concerns")
    else:
        console.print(f"\n[bold red]❌ Simple redistribution failed![/bold red]")
        console.print("The domain might need adjustment")
    
    return success


if __name__ == "__main__":
    success = main()
    if success:
        console.print("\n[bold yellow]🚀 Simple logistics planning completed![/bold yellow]")
    else:
        console.print("\n[bold red]🔧 Domain needs optimization[/bold red]")