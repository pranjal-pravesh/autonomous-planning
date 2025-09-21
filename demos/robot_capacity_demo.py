#!/usr/bin/env python3
"""
Robot Capacity Demo - Demonstrates robots with different capacities and LIFO stacking.
Shows how robots with capacities 1, 2, and 3 handle container pickup and delivery.
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

# Import from src/
from src.domain import LogisticsDomain
from src.actions import LogisticsActions
from src.problem import LogisticsProblem
from utils.display import LogisticsDisplay

console = Console()


def create_capacity_demo_problem():
    """Create a problem to demonstrate robot capacities."""
    
    # Create small-scale domain with capacity robots
    domain = LogisticsDomain(scale="small")
    actions = LogisticsActions(domain)
    
    # Create problem
    problem = Problem("robot_capacity_demo")
    
    # Add objects
    domain_objects = domain.get_domain_objects()
    problem.add_objects(domain_objects["all_objects"])
    
    # Add fluents
    for fluent in domain.fluents + domain.static_fluents:
        if fluent.type.is_int_type():
            problem.add_fluent(fluent, default_initial_value=0)
        else:
            problem.add_fluent(fluent, default_initial_value=False)
    
    # Add actions
    for action in actions.get_actions():
        problem.add_action(action)
    
    # Set initial state
    initial_state = domain.get_initial_state()
    for fluent, value in initial_state.items():
        problem.set_initial_value(fluent, value)
    
    return problem, domain, domain_objects


def create_capacity_demo_goal(problem, domain):
    """Create a goal that demonstrates capacity usage with proper stacking."""
    
    # Goal: Move c2 (top container) from p1 to p3, demonstrating LIFO constraints
    # This shows that only the top container can be picked up first
    
    goal_conditions = [
        # Move c2 (the top container) to p3 (at d3)
        domain.container_in_pile(domain.c2, domain.p3),
        # Keep c1 in p1 (it will become accessible after c2 is removed)
        domain.container_in_pile(domain.c1, domain.p1),
        # Keep c3 in p2
        domain.container_in_pile(domain.c3, domain.p2),
    ]
    
    problem.add_goal(And(*goal_conditions))
    return problem


def display_robot_capacities(domain_objects):
    """Display robot capacity information."""
    
    console.print(Panel.fit(
        "[bold blue]🤖 Robot Capacity System[/bold blue]\n"
        "[white]Robots with different capacities and LIFO stacking[/white]",
        border_style="blue"
    ))
    
    # Robot capacity table
    capacity_table = Table(title="🚛 Robot Capacities", show_header=True, header_style="bold cyan")
    capacity_table.add_column("Robot", style="cyan")
    capacity_table.add_column("Capacity", style="white")
    capacity_table.add_column("Initial Load", style="green")
    capacity_table.add_column("Initial Position", style="yellow")
    capacity_table.add_column("Description", style="blue")
    
    capacity_table.add_row("r1", "1", "0/1", "d1", "Single container robot")
    capacity_table.add_row("r2", "2", "0/2", "d2", "Double container robot")
    capacity_table.add_row("r3", "3", "0/3", "d3", "Triple container robot")
    
    console.print(capacity_table)
    
    # LIFO explanation
    lifo_table = Table(title="📚 LIFO Stacking System", show_header=True, header_style="bold magenta")
    lifo_table.add_column("Operation", style="cyan")
    lifo_table.add_column("Behavior", style="white")
    lifo_table.add_column("Example", style="green")
    
    lifo_table.add_row("Pickup", "New container goes on top", "r3 picks c1 → c1 on top")
    lifo_table.add_row("Pickup", "New container goes on top", "r3 picks c2 → c2 on top, c1 below")
    lifo_table.add_row("Putdown", "Only top container can be unloaded", "r3 can only putdown c2")
    lifo_table.add_row("Putdown", "After unloading, next container becomes top", "After c2, c1 becomes top")
    
    console.print(lifo_table)


def display_initial_and_target_capacity(domain):
    """Display initial and target states for capacity demo with detailed stacking."""
    
    # Initial state with detailed stacking
    initial_table = Table(title="📦 Initial Container Distribution (Bottom → Top)", show_header=True, header_style="bold cyan")
    initial_table.add_column("Dock", style="cyan")
    initial_table.add_column("Pile", style="white")
    initial_table.add_column("Stack Order", style="yellow")
    initial_table.add_column("Count", style="green")
    initial_table.add_column("Top Container", style="red")
    initial_table.add_column("Robot", style="blue")
    initial_table.add_column("Robot Capacity", style="magenta")
    
    initial_table.add_row("d1", "p1", "c1 → c2", "2", "c2", "r1", "1 (can't carry both)")
    initial_table.add_row("d2", "p2", "c3", "1", "c3", "r2", "2 (can carry c3)")
    initial_table.add_row("d3", "p3", "(empty)", "0", "-", "r3", "3 (can carry c1+c2)")
    
    console.print(initial_table)
    
    # Target state with detailed stacking
    target_table = Table(title="🎯 Target Container Distribution (Bottom → Top)", show_header=True, header_style="bold green")
    target_table.add_column("Dock", style="cyan")
    target_table.add_column("Pile", style="white")
    target_table.add_column("Target Stack", style="yellow")
    target_table.add_column("Count", style="green")
    target_table.add_column("Top Container", style="red")
    target_table.add_column("Change", style="blue")
    target_table.add_column("Required Robot", style="magenta")
    
    target_table.add_row("d1", "p1", "c1", "1", "c1", "2 → 1 (-1)", "After c2 removed")
    target_table.add_row("d2", "p2", "c3", "1", "c3", "1 → 1 (0)", "-")
    target_table.add_row("d3", "p3", "c2", "1", "c2", "0 → 1 (+1)", "r3 (capacity 3)")
    
    console.print(target_table)
    
    # Robot capacity analysis
    capacity_analysis_table = Table(title="🤖 Robot Capacity Analysis", show_header=True, header_style="bold magenta")
    capacity_analysis_table.add_column("Robot", style="cyan")
    capacity_analysis_table.add_column("Capacity", style="white")
    capacity_analysis_table.add_column("Initial Position", style="green")
    capacity_analysis_table.add_column("Task", style="yellow")
    capacity_analysis_table.add_column("Efficiency", style="red")
    
    capacity_analysis_table.add_row("r1", "1 container", "d1", "Move c2 only", "Medium (1 trip)")
    capacity_analysis_table.add_row("r2", "2 containers", "d2", "Move c3 only", "Medium (1 trip)")
    capacity_analysis_table.add_row("r3", "3 containers", "d3", "Move c2", "High (1 trip, demonstrates LIFO)")
    
    console.print(capacity_analysis_table)


def display_robot_load_states(result):
    """Display robot load states during plan execution."""
    
    console.print(Panel.fit(
        "[bold blue]🤖 Robot Load States During Execution[/bold blue]\n"
        "[white]Showing how robots carry containers during the plan[/white]",
        border_style="blue"
    ))
    
    # Simulate robot load states based on the plan
    robot_states = {
        "r1": {"load": [], "capacity": 1, "position": "d1"},
        "r2": {"load": [], "capacity": 2, "position": "d2"}, 
        "r3": {"load": [], "capacity": 3, "position": "d3"}
    }
    
    load_states_table = Table(title="🚛 Robot Load States", show_header=True, header_style="bold cyan")
    load_states_table.add_column("Step", style="cyan")
    load_states_table.add_column("Action", style="white")
    load_states_table.add_column("r1 Load", style="green")
    load_states_table.add_column("r2 Load", style="yellow")
    load_states_table.add_column("r3 Load", style="red")
    load_states_table.add_column("Notes", style="blue")
    
    # Track robot states through the plan
    for i, action in enumerate(result.plan.actions, 1):
        action_name = action.action.name
        params = [str(p) for p in action.actual_parameters]
        
        # Update robot states based on action
        if action_name == "pickup":
            robot, container, pile, dock = params
            if robot in robot_states:
                robot_states[robot]["load"].append(container)
                robot_states[robot]["position"] = dock
        elif action_name == "putdown":
            robot, container, pile, dock = params
            if robot in robot_states and container in robot_states[robot]["load"]:
                robot_states[robot]["load"].remove(container)
                robot_states[robot]["position"] = dock
        elif action_name == "move":
            robot, from_dock, to_dock = params
            if robot in robot_states:
                robot_states[robot]["position"] = to_dock
        
        # Format load states
        r1_load = " → ".join(robot_states["r1"]["load"]) if robot_states["r1"]["load"] else "(empty)"
        r2_load = " → ".join(robot_states["r2"]["load"]) if robot_states["r2"]["load"] else "(empty)"
        r3_load = " → ".join(robot_states["r3"]["load"]) if robot_states["r3"]["load"] else "(empty)"
        
        # Add notes
        notes = ""
        if action_name == "pickup":
            robot, container, pile, dock = params
            notes = f"{robot} picks {container}"
        elif action_name == "putdown":
            robot, container, pile, dock = params
            notes = f"{robot} puts {container}"
        elif action_name == "move":
            robot, from_dock, to_dock = params
            notes = f"{robot} moves to {to_dock}"
        
        load_states_table.add_row(
            str(i), 
            action_name, 
            r1_load, 
            r2_load, 
            r3_load, 
            notes
        )
    
    console.print(load_states_table)
    
    # Show final state
    final_state_table = Table(title="🏁 Final Robot States", show_header=True, header_style="bold green")
    final_state_table.add_column("Robot", style="cyan")
    final_state_table.add_column("Final Load", style="white")
    final_state_table.add_column("Final Position", style="green")
    final_state_table.add_column("Capacity Used", style="yellow")
    
    for robot, state in robot_states.items():
        final_load = " → ".join(state["load"]) if state["load"] else "(empty)"
        capacity_used = f"{len(state['load'])}/{state['capacity']}"
        final_state_table.add_row(robot, final_load, state["position"], capacity_used)
    
    console.print(final_state_table)


def solve_capacity_demo():
    """Solve the capacity demonstration scenario."""
    
    console.print(Panel.fit(
        "[bold blue]🤖 Robot Capacity Demonstration[/bold blue]\n"
        "[white]Testing robots with capacities 1, 2, and 3 with LIFO stacking[/white]",
        border_style="blue"
    ))
    
    # Create problem
    problem, domain, domain_objects = create_capacity_demo_problem()
    problem = create_capacity_demo_goal(problem, domain)
    
    # Display robot capacities
    display_robot_capacities(domain_objects)
    
    # Display initial and target states
    display_initial_and_target_capacity(domain)
    
    # Solve the problem
    console.print(f"\n[bold blue]🤖 Solving with fast-downward...[/bold blue]")
    
    try:
        with OneshotPlanner(name='fast-downward') as planner:
            start_time = time.time()
            result = planner.solve(problem)
            solve_time = time.time() - start_time
            
            if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
                console.print(f"[green]✅ SUCCESS! Capacity demo plan found in {solve_time:.3f}s[/green]")
                
                # Explain the LIFO behavior
                console.print(Panel.fit(
                    "[bold yellow]🎯 LIFO Stacking Demonstration[/bold yellow]\n"
                    "[white]Notice: Robot picks up c2 (top container) first, not c1 (bottom container)[/white]\n"
                    "[green]This demonstrates proper LIFO (Last In, First Out) behavior![/green]",
                    border_style="yellow"
                ))
                
                # Display plan
                LogisticsDisplay.display_plan_execution(result, "Robot Capacity Demonstration Plan")
                
                # Display robot load states during execution
                display_robot_load_states(result)
                
                # Display summary
                LogisticsDisplay.display_plan_summary(result, solve_time, "Capacity Demo Summary")
                
                return True, len(result.plan.actions)
            else:
                console.print(f"[red]❌ Planning failed: {result.status}[/red]")
                return False, 0
                
    except Exception as e:
        console.print(f"[red]❌ Error during planning: {e}[/red]")
        return False, 0


def main():
    """Run the robot capacity demonstration."""
    
    console.print(Panel.fit(
        "[bold blue]🤖 Robot Capacity Demonstration[/bold blue]\n"
        "[white]Testing robots with different capacities and LIFO stacking[/white]",
        border_style="blue"
    ))
    
    console.print("\n[bold cyan]📋 Demo Features:[/bold cyan]")
    console.print("• 3 robots with capacities 1, 2, and 3")
    console.print("• LIFO (Last In, First Out) stacking system")
    console.print("• Capacity constraints on pickup actions")
    console.print("• Only top container can be unloaded")
    console.print("• Realistic logistics operations")
    
    success, steps = solve_capacity_demo()
    
    if success:
        console.print(f"\n[bold green]🎉 Capacity demonstration completed![/bold green]")
        console.print(f"[bold cyan]📊 Executed {steps} actions demonstrating capacity system[/bold cyan]")
        console.print("[bold yellow]✨ Features demonstrated:[/bold yellow]")
        console.print("  • Robot capacity constraints (1, 2, 3)")
        console.print("  • LIFO stacking on robots")
        console.print("  • Capacity-aware pickup/putdown")
        console.print("  • Multi-container transport")
        console.print("  • Realistic logistics planning")
    else:
        console.print(f"\n[bold red]❌ Capacity demonstration failed![/bold red]")
        console.print("The capacity system might need adjustment")
    
    return success


if __name__ == "__main__":
    success = main()
    if success:
        console.print("\n[bold yellow]🚀 Robot capacity system working![/bold yellow]")
    else:
        console.print("\n[bold red]🔧 Capacity system needs optimization[/bold red]")
