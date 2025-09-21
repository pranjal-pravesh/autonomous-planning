#!/usr/bin/env python3
"""
Boolean Weight Demo - Simplified weight-based capacity constraints using boolean fluents.
This demo tests weight constraints without numeric complexity.
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


def create_boolean_weight_problem():
    """Create a boolean weight problem that's solvable."""
    
    # Create small-scale domain (we'll customize it)
    domain = LogisticsDomain(scale="small")
    actions = LogisticsActions(domain)
    
    # Create problem
    problem = Problem("boolean_weight_demo")
    
    # Add objects
    domain_objects = domain.get_domain_objects()
    problem.add_objects(domain_objects["all_objects"])
    
    # Add fluents
    for fluent in domain.fluents + domain.static_fluents:
        problem.add_fluent(fluent, default_initial_value=False)
    
    # Add actions
    for action in actions.get_actions():
        problem.add_action(action)
    
    # Custom initial state for boolean weight demo
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
        
        # Robot weight capacities (boolean system)
        domain.robot_can_carry_heavy(domain.r1): True,   # r1 can carry heavy containers
        domain.robot_can_carry_heavy(domain.r2): False,  # r2 cannot carry heavy containers
        
        # Robot current weight status (all start without heavy load)
        domain.robot_has_heavy_load(domain.r1): False,
        domain.robot_has_heavy_load(domain.r2): False,
        
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
        domain.container_in_robot_slot_1(domain.r1, domain.c5): False,
        
        domain.container_in_robot_slot_2(domain.r1, domain.c1): False,
        domain.container_in_robot_slot_2(domain.r1, domain.c2): False,
        domain.container_in_robot_slot_2(domain.r1, domain.c3): False,
        domain.container_in_robot_slot_2(domain.r1, domain.c4): False,
        domain.container_in_robot_slot_2(domain.r1, domain.c5): False,
        
        domain.container_in_robot_slot_1(domain.r2, domain.c1): False,
        domain.container_in_robot_slot_1(domain.r2, domain.c2): False,
        domain.container_in_robot_slot_1(domain.r2, domain.c3): False,
        domain.container_in_robot_slot_1(domain.r2, domain.c4): False,
        domain.container_in_robot_slot_1(domain.r2, domain.c5): False,
        
        domain.container_in_robot_slot_2(domain.r2, domain.c1): False,
        domain.container_in_robot_slot_2(domain.r2, domain.c2): False,
        domain.container_in_robot_slot_2(domain.r2, domain.c3): False,
        domain.container_in_robot_slot_2(domain.r2, domain.c4): False,
        domain.container_in_robot_slot_2(domain.r2, domain.c5): False,
        
        domain.robot_free(domain.r1): True,
        domain.robot_free(domain.r2): True,
        
        # Container weights (light=2t, heavy=4t)
        domain.container_is_light(domain.c1): True,   # c1 is light (2t)
        domain.container_is_light(domain.c2): True,   # c2 is light (2t)
        domain.container_is_light(domain.c3): False,  # c3 is heavy (4t)
        domain.container_is_light(domain.c4): False,  # c4 is heavy (4t)
        domain.container_is_light(domain.c5): True,   # c5 is light (2t)
        
        domain.container_is_heavy(domain.c1): False,  # c1 is not heavy
        domain.container_is_heavy(domain.c2): False,  # c2 is not heavy
        domain.container_is_heavy(domain.c3): True,   # c3 is heavy (4t)
        domain.container_is_heavy(domain.c4): True,   # c4 is heavy (4t)
        domain.container_is_heavy(domain.c5): False,  # c5 is not heavy
        
        # Container piles with proper stacking
        # Pile 1 (d1): c1(light) at bottom, c3(heavy) on top
        domain.container_in_pile(domain.c1, domain.p1): True,
        domain.container_in_pile(domain.c3, domain.p1): True,
        domain.container_on_top_of_pile(domain.c3, domain.p1): True,
        domain.container_on_top_of_pile(domain.c1, domain.p1): False,
        domain.container_under_in_pile(domain.c1, domain.c3, domain.p1): True,
        
        # Pile 2 (d2): c2(light) at bottom, c4(heavy) on top
        domain.container_in_pile(domain.c2, domain.p2): True,
        domain.container_in_pile(domain.c4, domain.p2): True,
        domain.container_on_top_of_pile(domain.c4, domain.p2): True,
        domain.container_on_top_of_pile(domain.c2, domain.p2): False,
        domain.container_under_in_pile(domain.c2, domain.c4, domain.p2): True,
        
        # Pile 3 (d3): c5(light) only
        domain.container_in_pile(domain.c5, domain.p3): True,
        domain.container_on_top_of_pile(domain.c5, domain.p3): True,
        
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


def create_boolean_weight_goal(problem, domain):
    """Create a boolean weight-based goal."""
    
    # Goal: Move c3 and c4 to p3
    # Challenge: r2 cannot carry heavy containers (c3, c4)
    # Only r1 can carry heavy containers
    
    goal_conditions = [
        # Move c3 and c4 to p3
        domain.container_in_pile(domain.c3, domain.p3),
        domain.container_in_pile(domain.c4, domain.p3),
        
        # Simple stacking: c3 at bottom, c4 on top
        domain.container_on_top_of_pile(domain.c4, domain.p3),
        domain.container_under_in_pile(domain.c3, domain.c4, domain.p3),
    ]
    
    problem.add_goal(And(*goal_conditions))
    return problem


def solve_boolean_weight_scenario():
    """Solve the boolean weight scenario."""
    
    console.print(Panel("⚖️ Boolean Weight Demo\nTesting simplified weight-based capacity constraints", 
                        title="Boolean Weight Demo", 
                        title_align="left", 
                        border_style="blue"))
    
    console.print("\n[bold cyan]📋 Demo Features:[/bold cyan]")
    console.print("• 2 robots with different weight capacities:")
    console.print("  - r1: Can carry heavy containers (4t)")
    console.print("  - r2: Cannot carry heavy containers (only light 2t)")
    console.print("• 5 containers: 3 light (2t each), 2 heavy (4t each)")
    console.print("• Initial: p1=c1(2t)→c3(4t), p2=c2(2t)→c4(4t), p3=c5(2t)")
    console.print("• Goal: Move c3 and c4 to p3")
    console.print("• Challenge: Only r1 can carry heavy containers!")
    console.print("• Architecture: Uses generalized src/ domain structure")
    
    # Create problem and domain
    problem, domain, domain_objects = create_boolean_weight_problem()
    
    # Add goal
    problem = create_boolean_weight_goal(problem, domain)
    
    # Display problem information
    LogisticsDisplay.display_domain_info(domain_objects)
    
    # Solve the problem
    console.print(f"\n[bold blue]🤖 Solving boolean weight demo...[/bold blue]")
    
    try:
        with OneshotPlanner(name='fast-downward') as planner:
            start_time = time.time()
            result = planner.solve(problem)
            solve_time = time.time() - start_time
            
            if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
                console.print(f"[bold green]✅ SUCCESS! Boolean weight demo completed in {solve_time:.3f}s[/bold green]")
                
                # Display execution plan
                if result.plan:
                    console.print("\n[bold cyan]📋 Boolean Weight Demo Execution Plan[/bold cyan]")
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
                            if container in ["c1", "c2", "c5"]:
                                weight_impact = "Light container (2t)"
                            else:  # c3, c4
                                weight_impact = "Heavy container (4t)"
                        elif action_name == "putdown":
                            robot, container, pile, dock = params
                            details = f"{robot} puts {container} on {pile} at {dock}"
                            # Determine weight based on container
                            if container in ["c1", "c2", "c5"]:
                                weight_impact = "Light container (2t)"
                            else:  # c3, c4
                                weight_impact = "Heavy container (4t)"
                        else:
                            details = f"{action_name}({', '.join(params)})"
                            weight_impact = "Unknown"
                        
                        table.add_row(str(i), action_name, params[0] if params else "-", details, weight_impact)
                    
                    console.print(table)
                    
                    # Summary
                    summary_table = Table(show_header=True, header_style="bold cyan", title="📊 Boolean Weight Demo Summary")
                    summary_table.add_column("Metric", style="cyan")
                    summary_table.add_column("Value", style="white")
                    
                    summary_table.add_row("Total Actions", str(len(result.plan.actions)))
                    summary_table.add_row("Solve Time", f"{solve_time:.3f} seconds")
                    summary_table.add_row("Status", "✅ SUCCESS")
                    
                    console.print(summary_table)
                    
                    console.print("\n[bold green]🎉 Boolean weight demo completed![/bold green]")
                    console.print(f"[green]📊 Executed {len(result.plan.actions)} actions demonstrating weight constraints[/green]")
                    console.print("[green]✨ Features demonstrated:[/green]")
                    console.print("[green]  • Boolean weight-based capacity constraints[/green]")
                    console.print("[green]  • Robot weight limit enforcement[/green]")
                    console.print("[green]  • Intelligent load planning[/green]")
                    console.print("[green]  • Weight-aware logistics planning[/green]")
                    console.print("\n[bold green]🚀 Boolean weight system working![/bold green]")
                    
                    return True, len(result.plan.actions)
                    
            else:
                console.print(f"[bold red]❌ Failed: {result.status}[/bold red]")
                return False, 0
                
    except Exception as e:
        console.print(f"[bold red]❌ Error during solving: {str(e)}[/bold red]")
        return False, 0


def main():
    """Main function to run the boolean weight demo."""
    success, steps = solve_boolean_weight_scenario()
    
    if not success:
        console.print("\n[bold red]❌ Boolean weight demo failed![/bold red]")
        console.print("[red]🔧 The weight constraints might still be too complex[/red]")
    
    return success


if __name__ == "__main__":
    main()
