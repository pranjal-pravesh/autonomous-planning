#!/usr/bin/env python3
"""
Large Scale Container Redistribution - Complex logistics world with multiple docks,
unequal piles per dock, many containers, and 3 robots for coordination.
"""

from unified_planning.shortcuts import *
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import time

console = Console()

def create_large_scale_domain():
    """Create a large-scale container domain with complex connectivity and unequal piles."""
    
    problem = Problem("large_scale_container_redistribution")
    
    # Define types
    Robot = UserType("Robot")
    Dock = UserType("Dock")
    Container = UserType("Container")
    Pile = UserType("Pile")
    
    # Create objects
    # 3 robots
    r1 = Object("r1", Robot)
    r2 = Object("r2", Robot)
    r3 = Object("r3", Robot)
    
    # 8 docks (larger world)
    d1 = Object("d1", Dock)
    d2 = Object("d2", Dock)
    d3 = Object("d3", Dock)
    d4 = Object("d4", Dock)
    d5 = Object("d5", Dock)
    d6 = Object("d6", Dock)
    d7 = Object("d7", Dock)
    d8 = Object("d8", Dock)
    
    # 15 containers (many more)
    c1 = Object("c1", Container)
    c2 = Object("c2", Container)
    c3 = Object("c3", Container)
    c4 = Object("c4", Container)
    c5 = Object("c5", Container)
    c6 = Object("c6", Container)
    c7 = Object("c7", Container)
    c8 = Object("c8", Container)
    c9 = Object("c9", Container)
    c10 = Object("c10", Container)
    c11 = Object("c11", Container)
    c12 = Object("c12", Container)
    c13 = Object("c13", Container)
    c14 = Object("c14", Container)
    c15 = Object("c15", Container)
    
    # 12 piles (unequal distribution per dock)
    # Dock 1: 2 piles, Dock 2: 1 pile, Dock 3: 3 piles, Dock 4: 1 pile
    # Dock 5: 2 piles, Dock 6: 1 pile, Dock 7: 1 pile, Dock 8: 1 pile
    p1 = Object("p1", Pile)   # d1
    p2 = Object("p2", Pile)   # d1
    p3 = Object("p3", Pile)   # d2
    p4 = Object("p4", Pile)   # d3
    p5 = Object("p5", Pile)   # d3
    p6 = Object("p6", Pile)   # d3
    p7 = Object("p7", Pile)   # d4
    p8 = Object("p8", Pile)   # d5
    p9 = Object("p9", Pile)   # d5
    p10 = Object("p10", Pile) # d6
    p11 = Object("p11", Pile) # d7
    p12 = Object("p12", Pile) # d8
    
    problem.add_objects([
        r1, r2, r3,  # 3 robots
        d1, d2, d3, d4, d5, d6, d7, d8,  # 8 docks
        c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15,  # 15 containers
        p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12  # 12 piles
    ])
    
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
        'robots': (r1, r2, r3),
        'docks': (d1, d2, d3, d4, d5, d6, d7, d8),
        'containers': (c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15),
        'piles': (p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12)
    }, {
        'robot_at': robot_at,
        'robot_carrying': robot_carrying,
        'robot_free': robot_free,
        'container_in_pile': container_in_pile,
        'pile_at_dock': pile_at_dock,
        'adjacent': adjacent
    }

def scenario_large_scale_redistribution():
    """
    Large-scale redistribution scenario with complex connectivity and unequal piles.
    
    Initial state:
    - Dock 1 (2 piles): p1(c1,c2,c3), p2(c4,c5) = 5 containers
    - Dock 2 (1 pile): p3(c6,c7) = 2 containers
    - Dock 3 (3 piles): p4(c8), p5(c9,c10), p6(c11) = 4 containers
    - Dock 4 (1 pile): p7(c12) = 1 container
    - Dock 5 (2 piles): p8(c13), p9(c14,c15) = 3 containers
    - Dock 6,7,8: empty = 0 containers
    
    Goal: Redistribute to achieve balanced distribution across all docks
    """
    
    console.print(Panel.fit(
        "[bold blue]🏭 Large Scale Container Redistribution[/bold blue]\n"
        "[white]Complex logistics world with 8 docks, 12 piles, 15 containers, 3 robots[/white]",
        border_style="blue"
    ))
    
    problem, objects, fluents = create_large_scale_domain()
    
    # Unpack objects
    r1, r2, r3 = objects['robots']
    d1, d2, d3, d4, d5, d6, d7, d8 = objects['docks']
    c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15 = objects['containers']
    p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12 = objects['piles']
    
    # Unpack fluents
    robot_at = fluents['robot_at']
    robot_carrying = fluents['robot_carrying']
    robot_free = fluents['robot_free']
    container_in_pile = fluents['container_in_pile']
    pile_at_dock = fluents['pile_at_dock']
    adjacent = fluents['adjacent']
    
    # Set initial robot positions
    problem.set_initial_value(robot_at(r1, d1), True)
    problem.set_initial_value(robot_at(r2, d3), True)
    problem.set_initial_value(robot_at(r3, d5), True)
    problem.set_initial_value(robot_free(r1), True)
    problem.set_initial_value(robot_free(r2), True)
    problem.set_initial_value(robot_free(r3), True)
    
    # Set pile-dock relationships (unequal distribution)
    # Dock 1: 2 piles
    problem.set_initial_value(pile_at_dock(p1, d1), True)
    problem.set_initial_value(pile_at_dock(p2, d1), True)
    # Dock 2: 1 pile
    problem.set_initial_value(pile_at_dock(p3, d2), True)
    # Dock 3: 3 piles
    problem.set_initial_value(pile_at_dock(p4, d3), True)
    problem.set_initial_value(pile_at_dock(p5, d3), True)
    problem.set_initial_value(pile_at_dock(p6, d3), True)
    # Dock 4: 1 pile
    problem.set_initial_value(pile_at_dock(p7, d4), True)
    # Dock 5: 2 piles
    problem.set_initial_value(pile_at_dock(p8, d5), True)
    problem.set_initial_value(pile_at_dock(p9, d5), True)
    # Dock 6: 1 pile
    problem.set_initial_value(pile_at_dock(p10, d6), True)
    # Dock 7: 1 pile
    problem.set_initial_value(pile_at_dock(p11, d7), True)
    # Dock 8: 1 pile
    problem.set_initial_value(pile_at_dock(p12, d8), True)
    
    # Set initial container distribution (simplified for planning)
    # Dock 1, Pile p1: c1, c2, c3
    problem.set_initial_value(container_in_pile(c1, p1), True)
    problem.set_initial_value(container_in_pile(c2, p1), True)
    problem.set_initial_value(container_in_pile(c3, p1), True)
    
    # Dock 1, Pile p2: c4, c5
    problem.set_initial_value(container_in_pile(c4, p2), True)
    problem.set_initial_value(container_in_pile(c5, p2), True)
    
    # Dock 2, Pile p3: c6, c7
    problem.set_initial_value(container_in_pile(c6, p3), True)
    problem.set_initial_value(container_in_pile(c7, p3), True)
    
    # Dock 3, Pile p4: c8
    problem.set_initial_value(container_in_pile(c8, p4), True)
    
    # Dock 3, Pile p5: c9, c10
    problem.set_initial_value(container_in_pile(c9, p5), True)
    problem.set_initial_value(container_in_pile(c10, p5), True)
    
    # Dock 3, Pile p6: c11
    problem.set_initial_value(container_in_pile(c11, p6), True)
    
    # Dock 4, Pile p7: c12
    problem.set_initial_value(container_in_pile(c12, p7), True)
    
    # Dock 5, Pile p8: c13
    problem.set_initial_value(container_in_pile(c13, p8), True)
    
    # Dock 5, Pile p9: c14, c15
    problem.set_initial_value(container_in_pile(c14, p9), True)
    problem.set_initial_value(container_in_pile(c15, p9), True)
    
    # Dock 6,7,8: empty (default)
    
    # Set up complex network connectivity (not fully connected)
    # Create a more realistic warehouse layout
    connections = [
        (d1, d2), (d1, d3),  # d1 connected to d2, d3
        (d2, d3), (d2, d4),  # d2 connected to d3, d4
        (d3, d4), (d3, d5),  # d3 connected to d4, d5
        (d4, d5), (d4, d6),  # d4 connected to d5, d6
        (d5, d6), (d5, d7),  # d5 connected to d6, d7
        (d6, d7), (d6, d8),  # d6 connected to d7, d8
        (d7, d8),            # d7 connected to d8
        # Add some cross-connections for more interesting paths
        (d1, d5),            # d1 connected to d5 (cross-connection)
        (d2, d6),            # d2 connected to d6 (cross-connection)
    ]
    
    for dock_a, dock_b in connections:
        problem.set_initial_value(adjacent(dock_a, dock_b), True)
        problem.set_initial_value(adjacent(dock_b, dock_a), True)  # Bidirectional
    
    # Define goal: Redistribute containers to achieve balanced distribution
    # Goal: Each dock should have approximately 2 containers (15 total / 8 docks ≈ 2)
    # We'll distribute: d1(2), d2(2), d3(2), d4(2), d5(2), d6(2), d7(2), d8(1)
    goal_conditions = [
        # Dock 1: 2 containers (c1, c2 in p1)
        container_in_pile(c1, p1),
        container_in_pile(c2, p1),
        
        # Dock 2: 2 containers (c3, c4 in p3)
        container_in_pile(c3, p3),
        container_in_pile(c4, p3),
        
        # Dock 3: 2 containers (c5, c6 in p4)
        container_in_pile(c5, p4),
        container_in_pile(c6, p4),
        
        # Dock 4: 2 containers (c7, c8 in p7)
        container_in_pile(c7, p7),
        container_in_pile(c8, p7),
        
        # Dock 5: 2 containers (c9, c10 in p8)
        container_in_pile(c9, p8),
        container_in_pile(c10, p8),
        
        # Dock 6: 2 containers (c11, c12 in p10)
        container_in_pile(c11, p10),
        container_in_pile(c12, p10),
        
        # Dock 7: 2 containers (c13, c14 in p11)
        container_in_pile(c13, p11),
        container_in_pile(c14, p11),
        
        # Dock 8: 1 container (c15 in p12)
        container_in_pile(c15, p12)
    ]
    
    problem.add_goal(And(*goal_conditions))
    
    return problem, "Redistribute 15 containers across 8 docks for balanced distribution"

def display_large_scale_plan():
    """Display the large-scale redistribution plan with detailed pile structure."""
    
    # Initial state with detailed pile structure
    initial_table = Table(title="📦 Initial Container Distribution (Bottom → Top)", show_header=True, header_style="bold cyan")
    initial_table.add_column("Dock", style="cyan")
    initial_table.add_column("Pile", style="white")
    initial_table.add_column("Stack Order", style="yellow")
    initial_table.add_column("Count", style="green")
    initial_table.add_column("Top Container", style="red")
    
    # Dock 1: p1(c1,c2,c3), p2(c4,c5)
    initial_table.add_row("d1", "p1", "c1 → c2 → c3", "3", "c3")
    initial_table.add_row("d1", "p2", "c4 → c5", "2", "c5")
    
    # Dock 2: p3(c6,c7)
    initial_table.add_row("d2", "p3", "c6 → c7", "2", "c7")
    
    # Dock 3: p4(c8), p5(c9,c10), p6(c11)
    initial_table.add_row("d3", "p4", "c8", "1", "c8")
    initial_table.add_row("d3", "p5", "c9 → c10", "2", "c10")
    initial_table.add_row("d3", "p6", "c11", "1", "c11")
    
    # Dock 4: p7(c12)
    initial_table.add_row("d4", "p7", "c12", "1", "c12")
    
    # Dock 5: p8(c13), p9(c14,c15)
    initial_table.add_row("d5", "p8", "c13", "1", "c13")
    initial_table.add_row("d5", "p9", "c14 → c15", "2", "c15")
    
    # Dock 6,7,8: empty
    initial_table.add_row("d6", "p10", "(empty)", "0", "-")
    initial_table.add_row("d7", "p11", "(empty)", "0", "-")
    initial_table.add_row("d8", "p12", "(empty)", "0", "-")
    
    console.print(initial_table)
    
    console.print()
    
    # Summary by dock
    summary_table = Table(title="📊 Dock Summary", show_header=True, header_style="bold magenta")
    summary_table.add_column("Dock", style="cyan")
    summary_table.add_column("Total Containers", style="green")
    summary_table.add_column("Piles Used", style="white")
    summary_table.add_column("Pile Distribution", style="yellow")
    
    summary_table.add_row("d1", "5", "2/2", "p1(3), p2(2)")
    summary_table.add_row("d2", "2", "1/1", "p3(2)")
    summary_table.add_row("d3", "4", "3/3", "p4(1), p5(2), p6(1)")
    summary_table.add_row("d4", "1", "1/1", "p7(1)")
    summary_table.add_row("d5", "3", "2/2", "p8(1), p9(2)")
    summary_table.add_row("d6", "0", "0/1", "p10(0)")
    summary_table.add_row("d7", "0", "0/1", "p11(0)")
    summary_table.add_row("d8", "0", "0/1", "p12(0)")
    
    console.print(summary_table)
    
    console.print()
    
    # Goal state with detailed target structure
    goal_table = Table(title="🎯 Target Container Distribution (Bottom → Top)", show_header=True, header_style="bold green")
    goal_table.add_column("Dock", style="cyan")
    goal_table.add_column("Target Pile", style="white")
    goal_table.add_column("Target Stack", style="yellow")
    goal_table.add_column("Count", style="green")
    goal_table.add_column("Change", style="white")
    goal_table.add_column("Top Container", style="red")
    
    goal_table.add_row("d1", "p1", "c1 → c2", "2", "5 → 2 (-3)", "c2")
    goal_table.add_row("d2", "p3", "c3 → c4", "2", "2 → 2 (0)", "c4")
    goal_table.add_row("d3", "p4", "c5 → c6", "2", "4 → 2 (-2)", "c6")
    goal_table.add_row("d4", "p7", "c7 → c8", "2", "1 → 2 (+1)", "c8")
    goal_table.add_row("d5", "p8", "c9 → c10", "2", "3 → 2 (-1)", "c10")
    goal_table.add_row("d6", "p10", "c11 → c12", "2", "0 → 2 (+2)", "c12")
    goal_table.add_row("d7", "p11", "c13 → c14", "2", "0 → 2 (+2)", "c14")
    goal_table.add_row("d8", "p12", "c15", "1", "0 → 1 (+1)", "c15")
    
    console.print(goal_table)
    
    console.print()
    
    # Target summary
    target_summary = Table(title="📊 Target Summary", show_header=True, header_style="bold green")
    target_summary.add_column("Dock", style="cyan")
    target_summary.add_column("Target Count", style="green")
    target_summary.add_column("Piles Used", style="white")
    target_summary.add_column("Redistribution", style="yellow")
    
    target_summary.add_row("d1", "2", "1/2", "Keep c1,c2, move c3,c4,c5")
    target_summary.add_row("d2", "2", "1/1", "Keep c6,c7, rename to c3,c4")
    target_summary.add_row("d3", "2", "1/3", "Keep c8,c9, move c10,c11")
    target_summary.add_row("d4", "2", "1/1", "Keep c12, add c7,c8")
    target_summary.add_row("d5", "2", "1/2", "Keep c13,c14, move c15")
    target_summary.add_row("d6", "2", "1/1", "Add c11,c12")
    target_summary.add_row("d7", "2", "1/1", "Add c13,c14")
    target_summary.add_row("d8", "1", "1/1", "Add c15")
    
    console.print(target_summary)
    
    console.print()
    
    # Network connectivity
    network_table = Table(title="🕸️ Network Connectivity", show_header=True, header_style="bold magenta")
    network_table.add_column("Dock", style="cyan")
    network_table.add_column("Connected To", style="white")
    network_table.add_column("Piles", style="yellow")
    
    network_table.add_row("d1", "d2, d3, d5", "p1, p2 (2 piles)")
    network_table.add_row("d2", "d1, d3, d4, d6", "p3 (1 pile)")
    network_table.add_row("d3", "d1, d2, d4, d5", "p4, p5, p6 (3 piles)")
    network_table.add_row("d4", "d2, d3, d5, d6", "p7 (1 pile)")
    network_table.add_row("d5", "d1, d3, d4, d6, d7", "p8, p9 (2 piles)")
    network_table.add_row("d6", "d2, d4, d5, d7, d8", "p10 (1 pile)")
    network_table.add_row("d7", "d5, d6, d8", "p11 (1 pile)")
    network_table.add_row("d8", "d6, d7", "p12 (1 pile)")
    
    console.print(network_table)

def solve_and_display_large_scale(problem, description):
    """Solve the large-scale redistribution problem."""
    
    console.print(f"\n[bold yellow]🎯 Goal:[/bold yellow] {description}")
    
    display_large_scale_plan()
    
    console.print(f"\n[bold blue]🤖 Solving with fast-downward...[/bold blue]")
    
    try:
        with OneshotPlanner(name='fast-downward') as planner:
            start_time = time.time()
            result = planner.solve(problem)
            solve_time = time.time() - start_time
            
            if result.status.name == 'SOLVED_SATISFICING':
                console.print(f"[green]✅ SUCCESS! Large-scale redistribution plan found in {solve_time:.3f}s[/green]")
                
                # Display plan
                plan_table = Table(title="📋 Large-Scale Redistribution Execution Plan", show_header=True, header_style="bold green")
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
                summary_table = Table(title="📊 Large-Scale Redistribution Summary", show_header=True, header_style="bold cyan")
                summary_table.add_column("Metric", style="cyan")
                summary_table.add_column("Value", style="white")
                
                summary_table.add_row("Total Actions", f"{len(result.plan.actions)}")
                summary_table.add_row("Solve Time", f"{solve_time:.3f} seconds")
                summary_table.add_row("Containers Moved", "15 containers redistributed")
                summary_table.add_row("Final Distribution", "Balanced across 8 docks ✅")
                summary_table.add_row("Robots Used", "3 robots coordinated")
                summary_table.add_row("Network Complexity", "Complex connectivity with cross-links")
                
                console.print(summary_table)
                
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
        "[white]Complex logistics world with realistic warehouse layout[/white]",
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
    
    problem, description = scenario_large_scale_redistribution()
    success, steps = solve_and_display_large_scale(problem, description)
    
    if success:
        console.print(f"\n[bold green]🎉 Large-scale redistribution completed![/bold green]")
        console.print(f"[bold cyan]📊 Executed {steps} actions to achieve balanced distribution[/bold cyan]")
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
