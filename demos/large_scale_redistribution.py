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
    """Create the goal for large-scale redistribution."""
    
    # Goal: Redistribute containers to achieve balanced distribution
    # Target: Each dock should have approximately 2 containers (15 total / 8 docks ≈ 2)
    # Distribution: d1(2), d2(2), d3(2), d4(2), d5(2), d6(2), d7(2), d8(1)
    
    goal_conditions = [
        # Dock 1: 2 containers (c1, c2 in p1)
        domain.container_in_pile(domain.c1, domain.p1),
        domain.container_in_pile(domain.c2, domain.p1),
        
        # Dock 2: 2 containers (c3, c4 in p3)
        domain.container_in_pile(domain.c3, domain.p3),
        domain.container_in_pile(domain.c4, domain.p3),
        
        # Dock 3: 2 containers (c5, c6 in p4)
        domain.container_in_pile(domain.c5, domain.p4),
        domain.container_in_pile(domain.c6, domain.p4),
        
        # Dock 4: 2 containers (c7, c8 in p7)
        domain.container_in_pile(domain.c7, domain.p7),
        domain.container_in_pile(domain.c8, domain.p7),
        
        # Dock 5: 2 containers (c9, c10 in p8)
        domain.container_in_pile(domain.c9, domain.p8),
        domain.container_in_pile(domain.c10, domain.p8),
        
        # Dock 6: 2 containers (c11, c12 in p10)
        domain.container_in_pile(domain.c11, domain.p10),
        domain.container_in_pile(domain.c12, domain.p10),
        
        # Dock 7: 2 containers (c13, c14 in p11)
        domain.container_in_pile(domain.c13, domain.p11),
        domain.container_in_pile(domain.c14, domain.p11),
        
        # Dock 8: 1 container (c15 in p12)
        domain.container_in_pile(domain.c15, domain.p12)
    ]
    
    problem.add_goal(And(*goal_conditions))
    return problem


def get_initial_distribution_data():
    """Get initial distribution data for display."""
    return [
        {"dock": "d1", "pile": "p1", "stack_order": "c1 → c2 → c3", "count": 3, "top_container": "c3"},
        {"dock": "d1", "pile": "p2", "stack_order": "c4 → c5", "count": 2, "top_container": "c5"},
        {"dock": "d2", "pile": "p3", "stack_order": "c6 → c7", "count": 2, "top_container": "c7"},
        {"dock": "d3", "pile": "p4", "stack_order": "c8", "count": 1, "top_container": "c8"},
        {"dock": "d3", "pile": "p5", "stack_order": "c9 → c10", "count": 2, "top_container": "c10"},
        {"dock": "d3", "pile": "p6", "stack_order": "c11", "count": 1, "top_container": "c11"},
        {"dock": "d4", "pile": "p7", "stack_order": "c12", "count": 1, "top_container": "c12"},
        {"dock": "d5", "pile": "p8", "stack_order": "c13", "count": 1, "top_container": "c13"},
        {"dock": "d5", "pile": "p9", "stack_order": "c14 → c15", "count": 2, "top_container": "c15"},
        {"dock": "d6", "pile": "p10", "stack_order": "(empty)", "count": 0, "top_container": "-"},
        {"dock": "d7", "pile": "p11", "stack_order": "(empty)", "count": 0, "top_container": "-"},
        {"dock": "d8", "pile": "p12", "stack_order": "(empty)", "count": 0, "top_container": "-"}
    ]


def get_target_distribution_data():
    """Get target distribution data for display."""
    return [
        {"dock": "d1", "pile": "p1", "target_stack": "c1 → c2", "count": 2, "change": "5 → 2 (-3)", "top_container": "c2"},
        {"dock": "d2", "pile": "p3", "target_stack": "c3 → c4", "count": 2, "change": "2 → 2 (0)", "top_container": "c4"},
        {"dock": "d3", "pile": "p4", "target_stack": "c5 → c6", "count": 2, "change": "4 → 2 (-2)", "top_container": "c6"},
        {"dock": "d4", "pile": "p7", "target_stack": "c7 → c8", "count": 2, "change": "1 → 2 (+1)", "top_container": "c8"},
        {"dock": "d5", "pile": "p8", "target_stack": "c9 → c10", "count": 2, "change": "3 → 2 (-1)", "top_container": "c10"},
        {"dock": "d6", "pile": "p10", "target_stack": "c11 → c12", "count": 2, "change": "0 → 2 (+2)", "top_container": "c12"},
        {"dock": "d7", "pile": "p11", "target_stack": "c13 → c14", "count": 2, "change": "0 → 2 (+2)", "top_container": "c14"},
        {"dock": "d8", "pile": "p12", "target_stack": "c15", "count": 1, "change": "0 → 1 (+1)", "top_container": "c15"}
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
    
    try:
        with OneshotPlanner(name='fast-downward') as planner:
            start_time = time.time()
            result = planner.solve(problem)
            solve_time = time.time() - start_time
            
            if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
                console.print(f"[green]✅ SUCCESS! Large-scale redistribution plan found in {solve_time:.3f}s[/green]")
                
                # Display plan
                LogisticsDisplay.display_plan_execution(result, "Large-Scale Redistribution Execution Plan")
                
                # Display summary
                LogisticsDisplay.display_plan_summary(result, solve_time, "Large-Scale Redistribution Summary")
                
                return True, len(result.plan.actions)
            else:
                console.print(f"[red]❌ Planning failed: {result.status}[/red]")
                return False, 0
                
    except Exception as e:
        console.print(f"[red]❌ Error during planning: {e}[/red]")
        return False, 0


def main():
    """Run the large-scale container redistribution scenario."""
    
    console.print(Panel.fit(
        "[bold blue]🏭 Large Scale Container Redistribution[/bold blue]\n"
        "[white]Refactored to use generalized src/ domain structure[/white]",
        border_style="blue"
    ))
    
    console.print("\n[bold cyan]📋 World Features:[/bold cyan]")
    console.print("• 3 robots (r1, r2, r3) for coordinated operations")
    console.print("• 8 docks with complex connectivity (not fully connected)")
    console.print("• 12 piles with unequal distribution per dock")
    console.print("• 15 containers for challenging redistribution")
    console.print("• Operations: move, pickup, putdown")
    console.print("• Goal: Balanced distribution across all docks")
    console.print("• Challenge: Multi-robot coordination in complex network")
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