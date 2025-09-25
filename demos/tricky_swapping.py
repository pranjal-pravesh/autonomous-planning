#!/usr/bin/env python3
"""
Tricky Container Swapping (Refactored)
- Domain remains general in src/
- This demo constructs all objects and initial state locally
- All containers: 2t weight
- All robots: 4t capacity, 2 slots
- Tests LIFO behavior with multi-capacity robots
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from unified_planning.shortcuts import *
from unified_planning.engines.results import PlanGenerationResultStatus
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import time

from src.domain import LogisticsDomain
from src.actions import LogisticsActions
from utils.display import LogisticsDisplay

console = Console()


def build_tricky_swapping_problem():
    """Create the tricky swapping problem with refactored domain."""
    
    # Create domain WITHOUT auto objects; we'll define state here
    domain = LogisticsDomain(scale="small", auto_objects=False)
    problem = Problem("tricky_container_swapping_refactored")

    # Create objects locally
    Robot = domain.Robot
    Dock = domain.Dock
    Container = domain.Container
    Pile = domain.Pile

    r1 = Object("r1", Robot)
    r2 = Object("r2", Robot)

    d1 = Object("d1", Dock)
    d2 = Object("d2", Dock)

    c1 = Object("c1", Container)
    c2 = Object("c2", Container)
    c3 = Object("c3", Container)
    c4 = Object("c4", Container)

    p1 = Object("p1", Pile)
    p2 = Object("p2", Pile)

    # Register all objects with the problem
    all_objects = [r1, r2, d1, d2, c1, c2, c3, c4, p1, p2]
    problem.add_objects(all_objects)
    
    # Assign objects to domain so actions can access them
    domain.assign_objects({
        "robots": [r1, r2],
        "docks": [d1, d2],
        "containers": [c1, c2, c3, c4],
        "piles": [p1, p2],
        "all_objects": all_objects
    })

    # Add fluents (all domain fluents and static fluents)
    for fluent in domain.fluents + domain.static_fluents:
        problem.add_fluent(fluent, default_initial_value=False)

    # Now that domain has objects, build actions and add them
    actions = LogisticsActions(domain)
    for action in actions.get_actions():
        problem.add_action(action)

    # Initial state - all containers 2t, robots 4t capacity, 2 slots
    I = {
        # Robot locations - r1 at d1, r2 at d2
        domain.robot_at(r1, d1): True,
        domain.robot_at(r2, d2): True,
        
        # Robot capacities - both robots can carry 2 containers (2 slots)
        domain.robot_can_carry_1(r1): True,
        domain.robot_can_carry_2(r1): True,
        domain.robot_can_carry_3(r1): False,  # r1 capacity 2 slots
        
        domain.robot_can_carry_1(r2): True,
        domain.robot_can_carry_2(r2): True,
        domain.robot_can_carry_3(r2): False,  # r2 capacity 2 slots
        
        # Robot weight capacity - both robots can carry up to 6t total (4t requirement fits)
        domain.robot_capacity_5(r1): False,
        domain.robot_capacity_6(r1): True,
        domain.robot_capacity_8(r1): False,
        domain.robot_capacity_10(r1): False,
        
        domain.robot_capacity_5(r2): False,
        domain.robot_capacity_6(r2): True,
        domain.robot_capacity_8(r2): False,
        domain.robot_capacity_10(r2): False,
        
        # Robot current weight - both start empty (0t)
        domain.robot_weight_0(r1): True,
        domain.robot_weight_2(r1): False,
        domain.robot_weight_4(r1): False,
        domain.robot_weight_6(r1): False,
        domain.robot_weight_8(r1): False,
        domain.robot_weight_10(r1): False,
        
        domain.robot_weight_0(r2): True,
        domain.robot_weight_2(r2): False,
        domain.robot_weight_4(r2): False,
        domain.robot_weight_6(r2): False,
        domain.robot_weight_8(r2): False,
        domain.robot_weight_10(r2): False,
        
        # Robot load tracking (all start empty)
        domain.robot_has_container_1(r1): False,
        domain.robot_has_container_2(r1): False,
        domain.robot_has_container_3(r1): False,
        
        domain.robot_has_container_1(r2): False,
        domain.robot_has_container_2(r2): False,
        domain.robot_has_container_3(r2): False,
        
        # Robot free status
        domain.robot_free(r1): True,
        domain.robot_free(r2): True,
        
        # Container weights - ALL containers are 2t
        domain.container_weight_2(c1): True,
        domain.container_weight_2(c2): True,
        domain.container_weight_2(c3): True,
        domain.container_weight_2(c4): True,
        
        # Container piles with proper stacking
        # Pile 1 (d1): c1(bottom) → c2(top)
        domain.container_in_pile(c1, p1): True,
        domain.container_in_pile(c2, p1): True,
        domain.container_on_top_of_pile(c2, p1): True,
        domain.container_on_top_of_pile(c1, p1): False,
        domain.container_under_in_pile(c1, c2, p1): True,
        
        # Pile 2 (d2): c3(bottom) → c4(top)
        domain.container_in_pile(c3, p2): True,
        domain.container_in_pile(c4, p2): True,
        domain.container_on_top_of_pile(c4, p2): True,
        domain.container_on_top_of_pile(c3, p2): False,
        domain.container_under_in_pile(c3, c4, p2): True,
        
        # Pile locations
        domain.pile_at_dock(p1, d1): True,
        domain.pile_at_dock(p2, d2): True,
        
        # Static relations - adjacent docks
        domain.adjacent(d1, d2): True,
        domain.adjacent(d2, d1): True,
    }

    for f, v in I.items():
        problem.set_initial_value(f, v)

    # Goal: Swap the piles with specific stacking orders
    # Pile 1 (d1): should have c3(bottom) → c4(top) 
    # Pile 2 (d2): should have c2(bottom) → c1(top) (REVERSED from original c1→c2)
    goal = And(
        # Pile 1 (d1) gets c3 and c4
        domain.container_in_pile(c3, p1),
        domain.container_in_pile(c4, p1),
        domain.container_on_top_of_pile(c4, p1),  # c4 on top
        domain.container_under_in_pile(c3, c4, p1),  # c3 under c4
        
        # Pile 2 (d2) gets c2 and c1 (REVERSED order)
        domain.container_in_pile(c2, p2),
        domain.container_in_pile(c1, p2),
        domain.container_on_top_of_pile(c1, p2),  # c1 on top (was bottom)
        domain.container_under_in_pile(c2, c1, p2),  # c2 under c1 (was top)
    )
    problem.add_goal(goal)

    # For display utilities
    domain_objects = {
        "robots": [r1, r2],
        "docks": [d1, d2],
        "containers": [c1, c2, c3, c4],
        "piles": [p1, p2],
        "all_objects": all_objects
    }

    return problem, domain, domain_objects


def solve_tricky_swapping_refactored():
    """Solve the tricky swapping scenario with refactored domain."""
    
    # Suppress engine credits in output
    from unified_planning import shortcuts as up_shortcuts
    up_shortcuts.get_environment().credits_stream = None

    console.print(Panel("Tricky Container Swapping (Refactored)\nDomain is independent; demo builds world and state locally", 
                        title="Refactored Tricky Swapping", 
                        title_align="left", 
                        border_style="blue"))
    
    console.print("\n[bold cyan]Test Features:[/bold cyan]")
    console.print("- 2 robots: r1, r2 (both 6t capacity, 2 slots)")
    console.print("- 2 docks connected directly")
    console.print("- 4 containers: c1, c2, c3, c4 (all 2t weight)")
    console.print("- 2 piles: p1 (d1), p2 (d2)")
    console.print("- Initial: p1=c1→c2, p2=c3→c4")
    console.print("- Goal: p1=c3→c4, p2=c2→c1 (REVERSED)")
    console.print("- Challenge: Test LIFO behavior with weight constraints")
    console.print("- Architecture: Uses clean, independent domain structure")
    
    problem, domain, domain_objects = build_tricky_swapping_problem()
    
    LogisticsDisplay.display_domain_info(domain_objects)
    
    console.print(f"\n[bold blue]Solving tricky swapping with refactored domain...[/bold blue]")
    
    try:
        with OneshotPlanner(name='fast-downward') as planner:
            start_time = time.time()
            result = planner.solve(problem)
            solve_time = time.time() - start_time
            
            if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
                console.print(f"[bold green]SUCCESS! Tricky swapping completed in {solve_time:.3f}s[/bold green]")
                
                # Display execution plan
                if result.plan:
                    console.print("\n[bold cyan]Tricky Swapping Execution Plan[/bold cyan]")
                    
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
                    summary_table = Table(show_header=True, header_style="bold cyan", title="Tricky Swapping Summary")
                    summary_table.add_column("Metric", style="cyan")
                    summary_table.add_column("Value", style="white")
                    
                    summary_table.add_row("Total Actions", str(len(result.plan.actions)))
                    summary_table.add_row("Solve Time", f"{solve_time:.3f} seconds")
                    summary_table.add_row("Status", "✅ SUCCESS")
                    summary_table.add_row("Architecture", "Refactored (Clean Domain)")
                    
                    console.print(summary_table)
                    
                    console.print("\n[bold green]Tricky swapping completed with refactored domain![/bold green]")
                    console.print(f"[green]Executed {len(result.plan.actions)} actions demonstrating LIFO behavior[/green]")
                    console.print("[green]Features demonstrated:[/green]")
                    console.print("[green]  - Multi-capacity robot coordination (6t capacity, 2 slots)[/green]")
                    console.print("[green]  - Weight-aware planning (all containers 2t)[/green]")
                    console.print("[green]  - LIFO order preservation vs reversal[/green]")
                    console.print("[green]  - Intelligent stacking strategy[/green]")
                    console.print("[green]  - Complex container redistribution[/green]")
                    console.print("[green]  - Clean, independent domain architecture[/green]")
                    
                    return True, len(result.plan.actions)
                    
            else:
                console.print(f"[bold red]❌ Failed: {result.status}[/bold red]")
                return False, 0
                
    except Exception as e:
        console.print(f"[bold red]❌ Error during solving: {str(e)}[/bold red]")
        return False, 0


def main():
    """Main function to run the refactored tricky swapping test."""
    success, steps = solve_tricky_swapping_refactored()
    
    if not success:
        console.print("\n[bold red]❌ Tricky swapping failed![/bold red]")
        console.print("[red]🔧 The LIFO constraints might be too complex[/red]")
    
    return success


if __name__ == "__main__":
    main()
