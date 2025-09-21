#!/usr/bin/env python3
"""
Tricky Weight Challenge - Complex weight-based capacity constraints.
This demo forces the planner to work within strict weight and capacity limits,
creating a scenario where intelligent planning is essential.
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


def create_tricky_weight_problem():
    """Create the tricky weight challenge problem."""
    
    # Create small-scale domain (we'll customize it)
    domain = LogisticsDomain(scale="small")
    actions = LogisticsActions(domain)
    
    # Create problem
    problem = Problem("tricky_weight_challenge")
    
    # Add objects
    domain_objects = domain.get_domain_objects()
    problem.add_objects(domain_objects["all_objects"])
    
    # Add fluents
    for fluent in domain.fluents + domain.static_fluents:
        problem.add_fluent(fluent, default_initial_value=False)
    
    # Add actions
    for action in actions.get_actions():
        problem.add_action(action)
    
    # Custom initial state for tricky weight challenge
    custom_initial_state = {
        # Robot locations - only r1 at d1
        domain.robot_at(domain.r1, domain.d1): True,
        domain.robot_at(domain.r2, domain.d2): False,  # r2 not used
        domain.robot_at(domain.r3, domain.d3): False,  # r3 not used
        
        # Robot capacities - r1 has 2 slots and can carry heavy containers
        domain.robot_can_carry_1(domain.r1): True,
        domain.robot_can_carry_2(domain.r1): True,
        domain.robot_can_carry_3(domain.r1): False,  # r1 capacity 2 slots
        
        # Robot weight capacity (boolean weight levels)
        domain.robot_capacity_6(domain.r1): True,   # r1 can carry up to 6t
        
        # Robot current weight level (starts with 0t)
        domain.robot_weight_0(domain.r1): True,
        
        # Robot load tracking (starts empty)
        domain.robot_has_container_1(domain.r1): False,
        domain.robot_has_container_2(domain.r1): False,
        domain.robot_has_container_3(domain.r1): False,
        
        # Initialize robot slot tracking (all empty initially)
        domain.container_in_robot_slot_1(domain.r1, domain.c1): False,
        domain.container_in_robot_slot_1(domain.r1, domain.c2): False,
        domain.container_in_robot_slot_1(domain.r1, domain.c3): False,
        domain.container_in_robot_slot_1(domain.r1, domain.c4): False,
        domain.container_in_robot_slot_1(domain.r1, domain.c5): False,
        
        domain.container_in_robot_slot_2(domain.r1, domain.c1): False,
        domain.container_in_robot_slot_2(domain.r1, domain.c2): False,
        domain.container_in_robot_slot_2(domain.r1, domain.c3): False,
        domain.container_in_robot_slot_2(domain.r1, domain.c4): False,
        domain.container_in_robot_slot_2(domain.r1, domain.c5): False,
        
        domain.robot_free(domain.r1): True,
        
        # Container weights (boolean weight levels)
        domain.container_weight_2(domain.c1): True,   # c1 weighs 2t
        domain.container_weight_4(domain.c2): True,   # c2 weighs 4t
        domain.container_weight_4(domain.c3): True,   # c3 weighs 4t
        domain.container_weight_4(domain.c4): True,   # c4 weighs 4t
        domain.container_weight_4(domain.c5): True,   # c5 weighs 4t
        
        # Container piles with proper stacking
        # Pile 1 (d1): c1(2t) at bottom, c2(4t) on top
        domain.container_in_pile(domain.c1, domain.p1): True,
        domain.container_in_pile(domain.c2, domain.p1): True,
        domain.container_on_top_of_pile(domain.c2, domain.p1): True,
        domain.container_on_top_of_pile(domain.c1, domain.p1): False,
        domain.container_under_in_pile(domain.c1, domain.c2, domain.p1): True,
        
        # Pile 2 (d2): c3(4t) at bottom, c4(4t) in middle, c5(4t) on top
        domain.container_in_pile(domain.c3, domain.p2): True,
        domain.container_in_pile(domain.c4, domain.p2): True,
        domain.container_in_pile(domain.c5, domain.p2): True,
        domain.container_on_top_of_pile(domain.c5, domain.p2): True,
        domain.container_on_top_of_pile(domain.c4, domain.p2): False,
        domain.container_on_top_of_pile(domain.c3, domain.p2): False,
        domain.container_under_in_pile(domain.c3, domain.c4, domain.p2): True,
        domain.container_under_in_pile(domain.c4, domain.c5, domain.p2): True,
        
        # Pile 3 (d3): empty initially
        domain.container_in_pile(domain.c1, domain.p3): False,
        domain.container_in_pile(domain.c2, domain.p3): False,
        domain.container_in_pile(domain.c3, domain.p3): False,
        domain.container_in_pile(domain.c4, domain.p3): False,
        domain.container_in_pile(domain.c5, domain.p3): False,
        
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
    
    return problem, domain, domain_objects


def create_tricky_weight_goal(problem, domain):
    """Create the tricky weight challenge goal."""
    
    # Challenge: 
    # - Final state: c4-c5-c1-c2 on pile 3, c3 on pile 2 (as original)
    # - Robot capacity: 6t weight, 2 slots
    # - Problem: Robot cannot carry 2 heavy containers (4t + 4t = 8t > 6t capacity)
    # - Solution: Must make multiple trips or use intelligent planning
    
    goal_conditions = [
        # Final distribution: c4-c5-c1-c2 on pile 3
        domain.container_in_pile(domain.c4, domain.p3),
        domain.container_in_pile(domain.c5, domain.p3),
        domain.container_in_pile(domain.c1, domain.p3),
        domain.container_in_pile(domain.c2, domain.p3),
        
        # c3 remains on pile 2 (as original)
        domain.container_in_pile(domain.c3, domain.p2),
        
        # Specific stacking order for pile 3: c4 at bottom, c5, c1, c2 on top
        domain.container_on_top_of_pile(domain.c2, domain.p3),  # c2 on top
        domain.container_under_in_pile(domain.c1, domain.c2, domain.p3),  # c1 under c2
        domain.container_under_in_pile(domain.c5, domain.c1, domain.p3),  # c5 under c1
        domain.container_under_in_pile(domain.c4, domain.c5, domain.p3),  # c4 under c5 (bottom)
        
        # c3 should be the only container on pile 2
        domain.container_on_top_of_pile(domain.c3, domain.p2),
    ]
    
    problem.add_goal(And(*goal_conditions))
    return problem


def get_tricky_weight_initial_data():
    """Get initial distribution data for tricky weight challenge."""
    return [
        {"dock": "d1", "pile": "p1", "stack_order": "c1(2t) → c2(4t)", "count": 2, "top_container": "c2"},
        {"dock": "d2", "pile": "p2", "stack_order": "c3(4t) → c4(4t) → c5(4t)", "count": 3, "top_container": "c5"},
        {"dock": "d3", "pile": "p3", "stack_order": "(empty)", "count": 0, "top_container": "-"}
    ]


def get_tricky_weight_target_data():
    """Get target distribution data for tricky weight challenge."""
    return [
        {"dock": "d1", "pile": "p1", "target_stack": "(empty)", "count": 0, "change": "2 → 0", "top_container": "-"},
        {"dock": "d2", "pile": "p2", "target_stack": "c3(4t)", "count": 1, "change": "3 → 1", "top_container": "c3"},
        {"dock": "d3", "pile": "p3", "target_stack": "c4(4t) → c5(4t) → c1(2t) → c2(4t)", "count": 4, "change": "0 → 4", "top_container": "c2"}
    ]


def solve_tricky_weight_scenario():
    """Solve the tricky weight challenge scenario."""
    
    console.print(Panel("⚖️ Tricky Weight Challenge\nComplex weight-based capacity constraints with intelligent planning", 
                        title="Tricky Weight Challenge", 
                        title_align="left", 
                        border_style="blue"))
    
    console.print("\n[bold cyan]📋 Challenge Features:[/bold cyan]")
    console.print("• 1 robot with strict constraints:")
    console.print("  - r1: 6t weight capacity, 2 slots")
    console.print("• 5 containers with numerical weights:")
    console.print("  - c1: 2t, c2: 4t, c3: 4t, c4: 4t, c5: 4t")
    console.print("• Initial: p1=c1(2t)→c2(4t), p2=c3(4t)→c4(4t)→c5(4t), p3=empty")
    console.print("• Goal: c4-c5-c1-c2 on p3, c3 on p2 (as original)")
    console.print("• Challenge: Robot cannot carry 2 heavy containers (8t > 6t)!")
    console.print("• Solution: Must use intelligent multi-trip planning")
    console.print("• Architecture: Uses generalized src/ domain structure")
    console.print("• Weight System: Boolean weight levels (2t, 4t, 6t) for planner compatibility")
    
    # Create problem and domain
    problem, domain, domain_objects = create_tricky_weight_problem()
    
    # Add goal
    problem = create_tricky_weight_goal(problem, domain)
    
    # Display problem information
    LogisticsDisplay.display_domain_info(domain_objects)
    
    # Get distribution data
    initial_distributions = get_tricky_weight_initial_data()
    target_distributions = get_tricky_weight_target_data()
    
    # Display distributions
    LogisticsDisplay.display_large_scale_distribution(initial_distributions, target_distributions)
    
    # Solve the problem
    console.print(f"\n[bold blue]🤖 Solving tricky weight challenge...[/bold blue]")
    
    try:
        with OneshotPlanner(name='fast-downward') as planner:
            start_time = time.time()
            result = planner.solve(problem)
            solve_time = time.time() - start_time
            
            if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
                console.print(f"[bold green]✅ SUCCESS! Tricky weight challenge completed in {solve_time:.3f}s[/bold green]")
                
                # Display execution plan
                if result.plan:
                    console.print("\n[bold cyan]📋 Tricky Weight Challenge Execution Plan[/bold cyan]")
                    from rich.table import Table
                    
                    table = Table(show_header=True, header_style="bold cyan")
                    table.add_column("Step", style="dim", width=6, justify="center")
                    table.add_column("Action", style="cyan", width=9)
                    table.add_column("Robot", style="yellow", width=7)
                    table.add_column("Details", style="white", width=40)
                    table.add_column("Weight Impact", style="magenta", width=20)
                    
                    for i, action in enumerate(result.plan.actions, 1):
                        action_name = action.action.name
                        params = [str(p) for p in action.actual_parameters]
                        
                        if action_name == "move":
                            robot, from_dock, to_dock = params
                            details = f"{robot}: {from_dock} → {to_dock}"
                            weight_impact = "No weight change"
                        elif action_name == "pickup":
                            robot, container, pile, dock = params
                            details = f"{robot} picks {container} from {pile} at {dock}"
                            # Determine weight based on container
                            if container == "c1":
                                weight_impact = "+2t"
                            else:  # c2, c3, c4, c5
                                weight_impact = "+4t"
                        elif action_name == "putdown":
                            robot, container, pile, dock = params
                            details = f"{robot} puts {container} on {pile} at {dock}"
                            # Determine weight based on container
                            if container == "c1":
                                weight_impact = "-2t"
                            else:  # c2, c3, c4, c5
                                weight_impact = "-4t"
                        else:
                            details = f"{action_name}({', '.join(params)})"
                            weight_impact = "Unknown"
                        
                        table.add_row(str(i), action_name, params[0] if params else "-", details, weight_impact)
                    
                    console.print(table)
                    
                    # Summary
                    summary_table = Table(show_header=True, header_style="bold cyan", title="📊 Tricky Weight Challenge Summary")
                    summary_table.add_column("Metric", style="cyan")
                    summary_table.add_column("Value", style="white")
                    
                    summary_table.add_row("Total Actions", str(len(result.plan.actions)))
                    summary_table.add_row("Solve Time", f"{solve_time:.3f} seconds")
                    summary_table.add_row("Status", "✅ SUCCESS")
                    
                    console.print(summary_table)
                    
                    console.print("\n[bold green]🎉 Tricky weight challenge completed![/bold green]")
                    console.print(f"[green]📊 Executed {len(result.plan.actions)} actions demonstrating intelligent weight planning[/green]")
                    console.print("[green]✨ Features demonstrated:[/green]")
                    console.print("[green]  • Complex weight-based capacity constraints[/green]")
                    console.print("[green]  • Multi-trip planning under weight limits[/green]")
                    console.print("[green]  • Intelligent load balancing[/green]")
                    console.print("[green]  • Realistic logistics planning[/green]")
                    console.print("[green]  • Advanced constraint satisfaction[/green]")
                    console.print("\n[bold green]🚀 Tricky weight system working intelligently![/bold green]")
                    
                    return True, len(result.plan.actions)
                    
            else:
                console.print(f"[bold red]❌ Failed: {result.status}[/bold red]")
                return False, 0
                
    except Exception as e:
        console.print(f"[bold red]❌ Error during solving: {str(e)}[/bold red]")
        return False, 0


def main():
    """Main function to run the tricky weight challenge."""
    success, steps = solve_tricky_weight_scenario()
    
    if not success:
        console.print("\n[bold red]❌ Tricky weight challenge failed![/bold red]")
        console.print("[red]🔧 The weight constraints might be too complex[/red]")
    
    return success


if __name__ == "__main__":
    main()
