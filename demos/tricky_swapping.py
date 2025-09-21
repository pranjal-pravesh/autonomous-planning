#!/usr/bin/env python3
"""
Tricky Container Swapping - Test LIFO behavior with multi-capacity robots.
This demo tests if the planner can figure out the optimal strategy for swapping
containers while preserving/reversing stacking order based on robot capacity usage.
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


def create_tricky_swapping_problem():
    """Create the tricky swapping problem with 2 docks, 2 piles, 2 robots."""
    
    # Create small-scale domain (we'll customize it)
    domain = LogisticsDomain(scale="small")
    actions = LogisticsActions(domain)
    
    # Create problem
    problem = Problem("tricky_container_swapping")
    
    # Add objects
    domain_objects = domain.get_domain_objects()
    problem.add_objects(domain_objects["all_objects"])
    
    # Add fluents
    for fluent in domain.fluents + domain.static_fluents:
        problem.add_fluent(fluent, default_initial_value=False)
    
    # Add actions
    for action in actions.get_actions():
        problem.add_action(action)
    
    # Custom initial state for tricky swapping
    custom_initial_state = {
        # Robot locations - r1 at d1, r2 at d2
        domain.robot_at(domain.r1, domain.d1): True,
        domain.robot_at(domain.r2, domain.d2): True,
        
        # Robot capacities - both robots can carry 2 containers
        domain.robot_can_carry_1(domain.r1): True,
        domain.robot_can_carry_2(domain.r1): True,
        domain.robot_can_carry_3(domain.r1): False,  # r1 capacity 2
        
        domain.robot_can_carry_1(domain.r2): True,
        domain.robot_can_carry_2(domain.r2): True,
        domain.robot_can_carry_3(domain.r2): False,  # r2 capacity 2
        
        # Robot load tracking (all start empty)
        domain.robot_has_container_1(domain.r1): False,
        domain.robot_has_container_2(domain.r1): False,
        domain.robot_has_container_3(domain.r1): False,
        
        domain.robot_has_container_1(domain.r2): False,
        domain.robot_has_container_2(domain.r2): False,
        domain.robot_has_container_3(domain.r2): False,
        
        # Initialize robot slot tracking (all empty initially)
        domain.container_in_robot_slot_1(domain.r1, domain.c1): False,
        domain.container_in_robot_slot_1(domain.r1, domain.c2): False,
        domain.container_in_robot_slot_1(domain.r1, domain.c3): False,
        domain.container_in_robot_slot_1(domain.r1, domain.c4): False,
        
        domain.container_in_robot_slot_2(domain.r1, domain.c1): False,
        domain.container_in_robot_slot_2(domain.r1, domain.c2): False,
        domain.container_in_robot_slot_2(domain.r1, domain.c3): False,
        domain.container_in_robot_slot_2(domain.r1, domain.c4): False,
        
        domain.container_in_robot_slot_1(domain.r2, domain.c1): False,
        domain.container_in_robot_slot_1(domain.r2, domain.c2): False,
        domain.container_in_robot_slot_1(domain.r2, domain.c3): False,
        domain.container_in_robot_slot_1(domain.r2, domain.c4): False,
        
        domain.container_in_robot_slot_2(domain.r2, domain.c1): False,
        domain.container_in_robot_slot_2(domain.r2, domain.c2): False,
        domain.container_in_robot_slot_2(domain.r2, domain.c3): False,
        domain.container_in_robot_slot_2(domain.r2, domain.c4): False,
        
        domain.robot_free(domain.r1): True,
        domain.robot_free(domain.r2): True,
        
        # Container piles with proper stacking
        # Pile 1 (d1): c1(bottom) → c2(top)
        domain.container_in_pile(domain.c1, domain.p1): True,
        domain.container_in_pile(domain.c2, domain.p1): True,
        domain.container_on_top_of_pile(domain.c2, domain.p1): True,
        domain.container_on_top_of_pile(domain.c1, domain.p1): False,
        domain.container_under_in_pile(domain.c1, domain.c2, domain.p1): True,
        
        # Pile 2 (d2): c3(bottom) → c4(top)
        domain.container_in_pile(domain.c3, domain.p2): True,
        domain.container_in_pile(domain.c4, domain.p2): True,
        domain.container_on_top_of_pile(domain.c4, domain.p2): True,
        domain.container_on_top_of_pile(domain.c3, domain.p2): False,
        domain.container_under_in_pile(domain.c3, domain.c4, domain.p2): True,
        
        # Pile locations
        domain.pile_at_dock(domain.p1, domain.d1): True,
        domain.pile_at_dock(domain.p2, domain.d2): True,
        
        # Static relations - adjacent docks
        domain.adjacent(domain.d1, domain.d2): True,
        domain.adjacent(domain.d2, domain.d1): True,
    }
    
    # Set initial state
    for fluent, value in custom_initial_state.items():
        problem.set_initial_value(fluent, value)
    
    return problem, domain, domain_objects


def create_tricky_swapping_goal(problem, domain):
    """Create the tricky swapping goal."""
    
    # Goal: Swap the piles with specific stacking orders
    # Pile 1 (d1): should have c3(bottom) → c4(top) 
    # Pile 2 (d2): should have c2(bottom) → c1(top) (REVERSED from original c1→c2)
    
    goal_conditions = [
        # Pile 1 (d1) gets c3 and c4
        domain.container_in_pile(domain.c3, domain.p1),
        domain.container_in_pile(domain.c4, domain.p1),
        domain.container_on_top_of_pile(domain.c4, domain.p1),  # c4 on top
        domain.container_under_in_pile(domain.c3, domain.c4, domain.p1),  # c3 under c4
        
        # Pile 2 (d2) gets c2 and c1 (REVERSED order)
        domain.container_in_pile(domain.c2, domain.p2),
        domain.container_in_pile(domain.c1, domain.p2),
        domain.container_on_top_of_pile(domain.c1, domain.p2),  # c1 on top (was bottom)
        domain.container_under_in_pile(domain.c2, domain.c1, domain.p2),  # c2 under c1 (was top)
    ]
    
    problem.add_goal(And(*goal_conditions))
    return problem


def get_tricky_swapping_initial_data():
    """Get initial distribution data for tricky swapping."""
    return [
        {"dock": "d1", "pile": "p1", "stack_order": "c1 → c2", "count": 2, "top_container": "c2"},
        {"dock": "d2", "pile": "p2", "stack_order": "c3 → c4", "count": 2, "top_container": "c4"}
    ]


def get_tricky_swapping_target_data():
    """Get target distribution data for tricky swapping."""
    return [
        {"dock": "d1", "pile": "p1", "target_stack": "c3 → c4", "count": 2, "change": "c1,c2 → c3,c4", "top_container": "c4"},
        {"dock": "d2", "pile": "p2", "target_stack": "c2 → c1", "count": 2, "change": "c3,c4 → c2,c1", "top_container": "c1"}
    ]


def solve_tricky_swapping_scenario():
    """Solve the tricky swapping scenario."""
    
    console.print(Panel("🔄 Tricky Container Swapping\nTesting LIFO behavior with multi-capacity robots", 
                        title="Tricky Container Swapping", 
                        title_align="left", 
                        border_style="blue"))
    
    console.print("\n[bold cyan]📋 Test Features:[/bold cyan]")
    console.print("• 2 robots: r1 (cap 2), r2 (cap 2)")
    console.print("• 2 docks connected directly")
    console.print("• 4 containers: c1, c2, c3, c4")
    console.print("• 2 piles: p1 (d1), p2 (d2)")
    console.print("• Initial: p1=c1→c2, p2=c3→c4")
    console.print("• Goal: p1=c3→c4, p2=c2→c1 (REVERSED)")
    console.print("• Challenge: Test LIFO behavior differences")
    console.print("• Architecture: Uses generalized src/ domain structure")
    
    # Create problem and domain
    problem, domain, domain_objects = create_tricky_swapping_problem()
    
    # Add goal
    problem = create_tricky_swapping_goal(problem, domain)
    
    # Display problem information
    LogisticsDisplay.display_domain_info(domain_objects)
    
    # Get distribution data
    initial_distributions = get_tricky_swapping_initial_data()
    target_distributions = get_tricky_swapping_target_data()
    
    # Display distributions
    LogisticsDisplay.display_large_scale_distribution(initial_distributions, target_distributions)
    
    # Solve the problem
    console.print(f"\n[bold blue]🤖 Solving tricky swapping...[/bold blue]")
    
    try:
        with OneshotPlanner(name='fast-downward') as planner:
            start_time = time.time()
            result = planner.solve(problem)
            solve_time = time.time() - start_time
            
            if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
                console.print(f"[bold green]✅ SUCCESS! Tricky swapping completed in {solve_time:.3f}s[/bold green]")
                
                # Display execution plan
                if result.plan:
                    console.print("\n[bold cyan]📋 Tricky Swapping Execution Plan[/bold cyan]")
                    from rich.table import Table
                    
                    table = Table(show_header=True, header_style="bold cyan")
                    table.add_column("Step", style="dim", width=6, justify="center")
                    table.add_column("Action", style="cyan", width=9)
                    table.add_column("Robot", style="yellow", width=7)
                    table.add_column("Details", style="white", width=35)
                    table.add_column("Purpose", style="green", width=30)
                    
                    for i, action in enumerate(result.plan.actions, 1):
                        action_name = action.action.name
                        params = [str(p) for p in action.actual_parameters]
                        
                        if action_name == "move":
                            robot, from_dock, to_dock = params
                            details = f"{robot}: {from_dock} → {to_dock}"
                            purpose = "Navigate to target location"
                        elif action_name == "pickup":
                            robot, container, pile, dock = params
                            details = f"{robot} picks {container} from {pile} at {dock}"
                            purpose = f"Collect {container} for swapping"
                        elif action_name == "putdown":
                            robot, container, pile, dock = params
                            details = f"{robot} puts {container} on {pile} at {dock}"
                            purpose = f"Deliver {container} to target pile"
                        else:
                            details = f"{action_name}({', '.join(params)})"
                            purpose = "Execute action"
                        
                        table.add_row(str(i), action_name, params[0] if params else "-", details, purpose)
                    
                    console.print(table)
                    
                    # Summary
                    summary_table = Table(show_header=True, header_style="bold cyan", title="📊 Tricky Swapping Summary")
                    summary_table.add_column("Metric", style="cyan")
                    summary_table.add_column("Value", style="white")
                    
                    summary_table.add_row("Total Actions", str(len(result.plan.actions)))
                    summary_table.add_row("Solve Time", f"{solve_time:.3f} seconds")
                    summary_table.add_row("Status", "✅ SUCCESS")
                    
                    console.print(summary_table)
                    
                    console.print("\n[bold green]🎉 Tricky swapping completed![/bold green]")
                    console.print(f"[green]📊 Executed {len(result.plan.actions)} actions demonstrating LIFO behavior[/green]")
                    console.print("[green]✨ Features demonstrated:[/green]")
                    console.print("[green]  • Multi-capacity robot coordination[/green]")
                    console.print("[green]  • LIFO order preservation vs reversal[/green]")
                    console.print("[green]  • Intelligent stacking strategy[/green]")
                    console.print("[green]  • Complex container redistribution[/green]")
                    console.print("[green]  • True LIFO robot behavior[/green]")
                    console.print("\n[bold green]🚀 LIFO system working intelligently![/bold green]")
                    
                    return True, len(result.plan.actions)
                    
            else:
                console.print(f"[bold red]❌ Failed: {result.status}[/bold red]")
                return False, 0
                
    except Exception as e:
        console.print(f"[bold red]❌ Error during solving: {str(e)}[/bold red]")
        return False, 0


def main():
    """Main function to run the tricky swapping test."""
    success, steps = solve_tricky_swapping_scenario()
    
    if not success:
        console.print("\n[bold red]❌ Tricky swapping failed![/bold red]")
        console.print("[red]🔧 The LIFO constraints might be too complex[/red]")
    
    return success


if __name__ == "__main__":
    main()
