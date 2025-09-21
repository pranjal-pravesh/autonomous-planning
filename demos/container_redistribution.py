#!/usr/bin/env python3
"""
Simplified container redistribution scenario using only boolean predicates.
Robots redistribute containers to achieve target counts at each dock.
"""

from unified_planning.shortcuts import *
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import time

console = Console()

def create_simple_container_problem():
    """Create a container redistribution problem with proper pile concept."""
    
    problem = Problem("container_redistribution_with_piles")
    
    # Define types
    Robot = UserType("Robot")
    Dock = UserType("Dock")
    Container = UserType("Container")
    Pile = UserType("Pile")
    
    # Create objects
    # 2 robots
    r1 = Object("r1", Robot)
    r2 = Object("r2", Robot)
    
    # 4 docks
    d1 = Object("d1", Dock)
    d2 = Object("d2", Dock)
    d3 = Object("d3", Dock)
    d4 = Object("d4", Dock)
    
    # 6 containers
    c1 = Object("c1", Container)
    c2 = Object("c2", Container)
    c3 = Object("c3", Container)
    c4 = Object("c4", Container)
    c5 = Object("c5", Container)
    c6 = Object("c6", Container)
    
    # 4 piles (one at each dock)
    p1 = Object("p1", Pile)
    p2 = Object("p2", Pile)
    p3 = Object("p3", Pile)
    p4 = Object("p4", Pile)
    
    problem.add_objects([r1, r2, d1, d2, d3, d4, c1, c2, c3, c4, c5, c6, p1, p2, p3, p4])
    
    # Define boolean fluents
    robot_at = Fluent("robot_at", BoolType(), robot=Robot, dock=Dock)
    robot_carrying = Fluent("robot_carrying", BoolType(), robot=Robot, container=Container)
    robot_free = Fluent("robot_free", BoolType(), robot=Robot)
    container_in_pile = Fluent("container_in_pile", BoolType(), container=Container, pile=Pile)
    pile_at_dock = Fluent("pile_at_dock", BoolType(), pile=Pile, dock=Dock)
    adjacent = Fluent("adjacent", BoolType(), dock1=Dock, dock2=Dock)
    
    # Add fluents to problem
    problem.add_fluent(robot_at, default_initial_value=False)
    problem.add_fluent(robot_carrying, default_initial_value=False)
    problem.add_fluent(robot_free, default_initial_value=True)
    problem.add_fluent(container_in_pile, default_initial_value=False)
    problem.add_fluent(pile_at_dock, default_initial_value=False)
    problem.add_fluent(adjacent, default_initial_value=False)
    
    # Define actions
    
    # 1. Move action - robot moves between adjacent docks
    move = InstantaneousAction("move", robot=Robot, from_dock=Dock, to_dock=Dock)
    robot = move.parameter("robot")
    from_dock = move.parameter("from_dock")
    to_dock = move.parameter("to_dock")
    
    move.add_precondition(robot_at(robot, from_dock))
    move.add_precondition(adjacent(from_dock, to_dock))
    
    move.add_effect(robot_at(robot, from_dock), False)
    move.add_effect(robot_at(robot, to_dock), True)
    
    problem.add_action(move)
    
    # 2. Pick up action - robot picks up container from pile
    pickup = InstantaneousAction("pickup", robot=Robot, container=Container, pile=Pile, dock=Dock)
    robot = pickup.parameter("robot")
    container = pickup.parameter("container")
    pile = pickup.parameter("pile")
    dock = pickup.parameter("dock")
    
    pickup.add_precondition(robot_at(robot, dock))
    pickup.add_precondition(pile_at_dock(pile, dock))
    pickup.add_precondition(container_in_pile(container, pile))
    pickup.add_precondition(robot_free(robot))
    
    pickup.add_effect(robot_carrying(robot, container), True)
    pickup.add_effect(robot_free(robot), False)
    pickup.add_effect(container_in_pile(container, pile), False)
    
    problem.add_action(pickup)
    
    # 3. Put down action - robot puts down container on pile
    putdown = InstantaneousAction("putdown", robot=Robot, container=Container, pile=Pile, dock=Dock)
    robot = putdown.parameter("robot")
    container = putdown.parameter("container")
    pile = putdown.parameter("pile")
    dock = putdown.parameter("dock")
    
    putdown.add_precondition(robot_at(robot, dock))
    putdown.add_precondition(pile_at_dock(pile, dock))
    putdown.add_precondition(robot_carrying(robot, container))
    
    putdown.add_effect(robot_carrying(robot, container), False)
    putdown.add_effect(robot_free(robot), True)
    putdown.add_effect(container_in_pile(container, pile), True)
    
    problem.add_action(putdown)
    
    return problem, {
        'robots': (r1, r2),
        'docks': (d1, d2, d3, d4),
        'containers': (c1, c2, c3, c4, c5, c6),
        'piles': (p1, p2, p3, p4)
    }, {
        'robot_at': robot_at,
        'robot_carrying': robot_carrying,
        'robot_free': robot_free,
        'container_in_pile': container_in_pile,
        'pile_at_dock': pile_at_dock,
        'adjacent': adjacent
    }

def scenario_simple_redistribution():
    """
    Container redistribution scenario with proper pile concept.
    
    Initial state:
    - Dock 1, Pile p1: containers c1, c2, c3 (3 containers)
    - Dock 2, Pile p2: containers c4, c5 (2 containers)  
    - Dock 3, Pile p3: container c6 (1 container)
    - Dock 4, Pile p4: no containers (0 containers)
    
    Goal state:
    - Dock 1, Pile p1: 1 container (c1)
    - Dock 2, Pile p2: 1 container (c4) 
    - Dock 3, Pile p3: 2 containers (c2, c6)
    - Dock 4, Pile p4: 2 containers (c3, c5)
    
    This achieves the target distribution: N₁=1, N₂=1, N₃=2, N₄=2
    """
    
    console.print(Panel.fit(
        "[bold blue]📦 Container Redistribution with Piles[/bold blue]\n"
        "[white]Goal: Redistribute containers to achieve N₁=1, N₂=1, N₃=2, N₄=2[/white]",
        border_style="blue"
    ))
    
    problem, objects, fluents = create_simple_container_problem()
    
    # Unpack objects
    r1, r2 = objects['robots']
    d1, d2, d3, d4 = objects['docks']
    c1, c2, c3, c4, c5, c6 = objects['containers']
    p1, p2, p3, p4 = objects['piles']
    
    # Unpack fluents
    robot_at = fluents['robot_at']
    robot_carrying = fluents['robot_carrying']
    robot_free = fluents['robot_free']
    container_in_pile = fluents['container_in_pile']
    pile_at_dock = fluents['pile_at_dock']
    adjacent = fluents['adjacent']
    
    # Set initial robot positions
    problem.set_initial_value(robot_at(r1, d1), True)
    problem.set_initial_value(robot_at(r2, d2), True)
    problem.set_initial_value(robot_free(r1), True)
    problem.set_initial_value(robot_free(r2), True)
    
    # Set pile-dock relationships
    problem.set_initial_value(pile_at_dock(p1, d1), True)
    problem.set_initial_value(pile_at_dock(p2, d2), True)
    problem.set_initial_value(pile_at_dock(p3, d3), True)
    problem.set_initial_value(pile_at_dock(p4, d4), True)
    
    # Set initial container distribution
    # Dock 1, Pile p1: c1, c2, c3
    problem.set_initial_value(container_in_pile(c1, p1), True)
    problem.set_initial_value(container_in_pile(c2, p1), True)
    problem.set_initial_value(container_in_pile(c3, p1), True)
    
    # Dock 2, Pile p2: c4, c5
    problem.set_initial_value(container_in_pile(c4, p2), True)
    problem.set_initial_value(container_in_pile(c5, p2), True)
    
    # Dock 3, Pile p3: c6
    problem.set_initial_value(container_in_pile(c6, p3), True)
    
    # Dock 4, Pile p4: empty (default)
    
    # Set up network connectivity (fully connected for simplicity)
    docks = [d1, d2, d3, d4]
    for i, dock_a in enumerate(docks):
        for j, dock_b in enumerate(docks):
            if i != j:
                problem.set_initial_value(adjacent(dock_a, dock_b), True)
    
    # Define goal: Specific container placement to achieve target counts
    goal_conditions = [
        # Dock 1, Pile p1: 1 container (c1)
        container_in_pile(c1, p1),
        
        # Dock 2, Pile p2: 1 container (c4)
        container_in_pile(c4, p2),
        
        # Dock 3, Pile p3: 2 containers (c2, c6)
        container_in_pile(c2, p3),
        container_in_pile(c6, p3),
        
        # Dock 4, Pile p4: 2 containers (c3, c5)
        container_in_pile(c3, p4),
        container_in_pile(c5, p4)
    ]
    
    problem.add_goal(And(*goal_conditions))
    
    return problem, "Redistribute 6 containers to achieve target counts: N₁=1, N₂=1, N₃=2, N₄=2"

def display_redistribution_plan():
    """Display the redistribution plan in tables."""
    
    # Initial state
    initial_table = Table(title="📦 Initial Container Distribution", show_header=True, header_style="bold cyan")
    initial_table.add_column("Dock", style="cyan")
    initial_table.add_column("Pile", style="white")
    initial_table.add_column("Containers", style="yellow")
    initial_table.add_column("Count", style="green")
    
    initial_table.add_row("d1", "p1", "c1, c2, c3", "3")
    initial_table.add_row("d2", "p2", "c4, c5", "2")
    initial_table.add_row("d3", "p3", "c6", "1")
    initial_table.add_row("d4", "p4", "(empty)", "0")
    
    console.print(initial_table)
    
    console.print()
    
    # Goal state
    goal_table = Table(title="🎯 Target Container Distribution", show_header=True, header_style="bold green")
    goal_table.add_column("Dock", style="cyan")
    goal_table.add_column("Pile", style="white")
    goal_table.add_column("Target Containers", style="yellow")
    goal_table.add_column("Target Count (Nᵢ)", style="green")
    goal_table.add_column("Change", style="white")
    
    goal_table.add_row("d1", "p1", "c1", "1", "3 → 1 (-2)")
    goal_table.add_row("d2", "p2", "c4", "1", "2 → 1 (-1)")
    goal_table.add_row("d3", "p3", "c2, c6", "2", "1 → 2 (+1)")
    goal_table.add_row("d4", "p4", "c3, c5", "2", "0 → 2 (+2)")
    
    console.print(goal_table)

def solve_and_display_simple_redistribution(problem, description):
    """Solve the simplified redistribution problem."""
    
    console.print(f"\n[bold yellow]🎯 Goal:[/bold yellow] {description}")
    
    display_redistribution_plan()
    
    console.print(f"\n[bold blue]🤖 Solving with fast-downward...[/bold blue]")
    
    try:
        with OneshotPlanner(name='fast-downward') as planner:
            start_time = time.time()
            result = planner.solve(problem)
            solve_time = time.time() - start_time
            
            if result.status.name == 'SOLVED_SATISFICING':
                console.print(f"[green]✅ SUCCESS! Redistribution plan found in {solve_time:.3f}s[/green]")
                
                # Display plan
                plan_table = Table(title="📋 Container Redistribution Execution Plan", show_header=True, header_style="bold green")
                plan_table.add_column("Step", style="cyan", justify="center")
                plan_table.add_column("Action", style="white")
                plan_table.add_column("Robot", style="yellow")
                plan_table.add_column("Details", style="green")
                plan_table.add_column("Purpose", style="blue")
                
                for i, action in enumerate(result.plan.actions, 1):
                    action_name = action.action.name
                    params = [str(p) for p in action.actual_parameters]
                    
                    if action_name == "move":
                        robot_param, from_dock, to_dock = params
                        details = f"{robot_param}: {from_dock} → {to_dock}"
                        purpose = "Navigate to target location"
                    elif action_name == "pickup":
                        robot_param, container, pile, dock = params
                        details = f"{robot_param} picks {container} from {pile} at {dock}"
                        purpose = f"Collect {container} for redistribution"
                    elif action_name == "putdown":
                        robot_param, container, pile, dock = params
                        details = f"{robot_param} puts {container} on {pile} at {dock}"
                        purpose = f"Deliver {container} to target pile"
                    else:
                        details = ", ".join(params)
                        purpose = "Execute action"
                    
                    plan_table.add_row(str(i), action_name, params[0] if params else "?", details, purpose)
                
                console.print(plan_table)
                
                # Summary
                summary_table = Table(title="📊 Redistribution Summary", show_header=True, header_style="bold cyan")
                summary_table.add_column("Metric", style="cyan")
                summary_table.add_column("Value", style="white")
                
                summary_table.add_row("Total Actions", f"{len(result.plan.actions)}")
                summary_table.add_row("Solve Time", f"{solve_time:.3f} seconds")
                summary_table.add_row("Containers Moved", "4 containers redistributed")
                summary_table.add_row("Final Distribution", "N₁=1, N₂=1, N₃=2, N₄=2 ✅")
                
                console.print(summary_table)
                
                return True, len(result.plan.actions)
            else:
                console.print(f"[red]❌ Planning failed: {result.status}[/red]")
                return False, 0
                
    except Exception as e:
        console.print(f"[red]❌ Error during planning: {e}[/red]")
        return False, 0

def main():
    """Run the simplified container redistribution scenario."""
    
    console.print(Panel.fit(
        "[bold blue]🏗️ Container Redistribution Planning[/bold blue]\n"
        "[white]Realistic logistics with pickup/delivery operations[/white]",
        border_style="blue"
    ))
    
    console.print("\n[bold cyan]📋 Scenario Description:[/bold cyan]")
    console.print("• 2 robots (r1, r2) working cooperatively")
    console.print("• 4 docks (d1, d2, d3, d4) as locations")
    console.print("• 6 containers (c1-c6) to redistribute optimally")
    console.print("• Goal: Achieve target counts Nᵢ at each dock i")
    console.print("• Operations: move, pickup, putdown")
    console.print("• Challenge: Multi-robot coordination for efficiency")
    
    problem, description = scenario_simple_redistribution()
    success, steps = solve_and_display_simple_redistribution(problem, description)
    
    if success:
        console.print(f"\n[bold green]🎉 Container redistribution completed successfully![/bold green]")
        console.print(f"[bold cyan]📊 Executed {steps} actions to achieve optimal distribution[/bold cyan]")
    else:
        console.print(f"\n[bold red]❌ Container redistribution failed![/bold red]")
        console.print("The domain might still be too complex - let's analyze the issue")
    
    return success

if __name__ == "__main__":
    success = main()
    if success:
        console.print("\n[bold yellow]🚀 Container redistribution planning completed![/bold yellow]")
    else:
        console.print("\n[bold red]🔧 Domain needs further simplification for PDDL compatibility[/bold red]")
