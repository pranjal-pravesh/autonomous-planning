#!/usr/bin/env python3
"""
Working multi-step planning demo - simplified approach without capacity constraints.
"""

from unified_planning.shortcuts import *
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import time

console = Console()

def create_working_multi_robot_problem():
    """Create a simple logistics problem that definitely works."""
    
    problem = Problem("working_multi_robot")
    
    # Define types
    Robot = UserType("Robot")
    Dock = UserType("Dock")
    
    # Create objects - 2 robots, 5 docks (more docks = more space)
    r1 = Object("r1", Robot)
    r2 = Object("r2", Robot)
    d1 = Object("d1", Dock)
    d2 = Object("d2", Dock)
    d3 = Object("d3", Dock)
    d4 = Object("d4", Dock)
    d5 = Object("d5", Dock)
    
    problem.add_objects([r1, r2, d1, d2, d3, d4, d5])
    
    # Simple boolean fluents - no capacity constraints for now
    robot_at = Fluent("robot_at", BoolType(), robot=Robot, dock=Dock)
    adjacent = Fluent("adjacent", BoolType(), dock1=Dock, dock2=Dock)
    
    problem.add_fluent(robot_at, default_initial_value=False)
    problem.add_fluent(adjacent, default_initial_value=False)
    
    # Simple move action - multiple robots can be at same dock
    move = InstantaneousAction("move", robot=Robot, from_dock=Dock, to_dock=Dock)
    robot = move.parameter("robot")
    from_dock = move.parameter("from_dock")
    to_dock = move.parameter("to_dock")
    
    # Simple preconditions
    move.add_precondition(robot_at(robot, from_dock))
    move.add_precondition(adjacent(from_dock, to_dock))
    
    # Simple effects
    move.add_effect(robot_at(robot, from_dock), False)
    move.add_effect(robot_at(robot, to_dock), True)
    
    problem.add_action(move)
    
    return problem, (r1, r2), (d1, d2, d3, d4, d5), (robot_at, adjacent)

def scenario_1_long_path():
    """Robot r1 must travel a long path d1 → d2 → d3 → d4 → d5."""
    
    console.print(Panel.fit(
        "[bold blue]📍 Scenario 1: Long Path[/bold blue]\n"
        "[white]Robot r1 travels d1 → d2 → d3 → d4 → d5 (4 steps)[/white]",
        border_style="blue"
    ))
    
    problem, (r1, r2), (d1, d2, d3, d4, d5), (robot_at, adjacent) = create_working_multi_robot_problem()
    
    # Set initial state: r1 at d1, r2 at d3 (out of direct path)
    problem.set_initial_value(robot_at(r1, d1), True)
    problem.set_initial_value(robot_at(r2, d3), True)
    
    # Create linear path: d1-d2-d3-d4-d5
    problem.set_initial_value(adjacent(d1, d2), True)
    problem.set_initial_value(adjacent(d2, d1), True)
    problem.set_initial_value(adjacent(d2, d3), True)
    problem.set_initial_value(adjacent(d3, d2), True)
    problem.set_initial_value(adjacent(d3, d4), True)
    problem.set_initial_value(adjacent(d4, d3), True)
    problem.set_initial_value(adjacent(d4, d5), True)
    problem.set_initial_value(adjacent(d5, d4), True)
    
    # Goal: r1 must reach d5
    problem.add_goal(robot_at(r1, d5))
    
    return problem, "r1 travels the full path d1 → d5"

def scenario_2_robot_coordination():
    """Both robots must reach specific positions requiring coordination."""
    
    console.print(Panel.fit(
        "[bold green]🤝 Scenario 2: Robot Coordination[/bold green]\n"
        "[white]r1 goes to d5, r2 goes to d1 (they start at opposite ends)[/white]",
        border_style="green"
    ))
    
    problem, (r1, r2), (d1, d2, d3, d4, d5), (robot_at, adjacent) = create_working_multi_robot_problem()
    
    # Set initial state: r1 at d1, r2 at d5 (opposite ends)
    problem.set_initial_value(robot_at(r1, d1), True)
    problem.set_initial_value(robot_at(r2, d5), True)
    
    # Create linear path: d1-d2-d3-d4-d5
    problem.set_initial_value(adjacent(d1, d2), True)
    problem.set_initial_value(adjacent(d2, d1), True)
    problem.set_initial_value(adjacent(d2, d3), True)
    problem.set_initial_value(adjacent(d3, d2), True)
    problem.set_initial_value(adjacent(d3, d4), True)
    problem.set_initial_value(adjacent(d4, d3), True)
    problem.set_initial_value(adjacent(d4, d5), True)
    problem.set_initial_value(adjacent(d5, d4), True)
    
    # Goal: Robots swap to opposite ends
    problem.add_goal(And(robot_at(r1, d5), robot_at(r2, d1)))
    
    return problem, "r1 and r2 travel to opposite ends"

def scenario_3_convergence():
    """Both robots must converge at the same dock."""
    
    console.print(Panel.fit(
        "[bold red]🎯 Scenario 3: Convergence[/bold red]\n"
        "[white]Both robots must reach d3 (middle dock)[/white]",
        border_style="red"
    ))
    
    problem, (r1, r2), (d1, d2, d3, d4, d5), (robot_at, adjacent) = create_working_multi_robot_problem()
    
    # Set initial state: r1 at d1, r2 at d5 (opposite ends)
    problem.set_initial_value(robot_at(r1, d1), True)
    problem.set_initial_value(robot_at(r2, d5), True)
    
    # Create linear path: d1-d2-d3-d4-d5
    problem.set_initial_value(adjacent(d1, d2), True)
    problem.set_initial_value(adjacent(d2, d1), True)
    problem.set_initial_value(adjacent(d2, d3), True)
    problem.set_initial_value(adjacent(d3, d2), True)
    problem.set_initial_value(adjacent(d3, d4), True)
    problem.set_initial_value(adjacent(d4, d3), True)
    problem.set_initial_value(adjacent(d4, d5), True)
    problem.set_initial_value(adjacent(d5, d4), True)
    
    # Goal: Both robots at d3 (middle)
    problem.add_goal(And(robot_at(r1, d3), robot_at(r2, d3)))
    
    return problem, "Both robots converge at d3"

def scenario_4_complex_network():
    """Complex network with multiple paths."""
    
    console.print(Panel.fit(
        "[bold magenta]🕸️ Scenario 4: Complex Network[/bold magenta]\n"
        "[white]Network with multiple paths - robots find optimal routes[/white]",
        border_style="magenta"
    ))
    
    problem, (r1, r2), (d1, d2, d3, d4, d5), (robot_at, adjacent) = create_working_multi_robot_problem()
    
    # Set initial state: r1 at d1, r2 at d2
    problem.set_initial_value(robot_at(r1, d1), True)
    problem.set_initial_value(robot_at(r2, d2), True)
    
    # Create complex network (star pattern with d3 as center)
    # d1-d3, d2-d3, d3-d4, d3-d5, d4-d5 (multiple paths)
    problem.set_initial_value(adjacent(d1, d3), True)
    problem.set_initial_value(adjacent(d3, d1), True)
    problem.set_initial_value(adjacent(d2, d3), True)
    problem.set_initial_value(adjacent(d3, d2), True)
    problem.set_initial_value(adjacent(d3, d4), True)
    problem.set_initial_value(adjacent(d4, d3), True)
    problem.set_initial_value(adjacent(d3, d5), True)
    problem.set_initial_value(adjacent(d5, d3), True)
    problem.set_initial_value(adjacent(d4, d5), True)
    problem.set_initial_value(adjacent(d5, d4), True)
    # Add direct path d1-d2 for more options
    problem.set_initial_value(adjacent(d1, d2), True)
    problem.set_initial_value(adjacent(d2, d1), True)
    
    # Goal: r1 to d4, r2 to d5
    problem.add_goal(And(robot_at(r1, d4), robot_at(r2, d5)))
    
    return problem, "r1 reaches d4, r2 reaches d5 via optimal paths"

def solve_and_display(problem, description, scenario_name):
    """Solve a problem and display the results."""
    
    console.print(f"\n[bold yellow]🎯 Goal:[/bold yellow] {description}")
    console.print(f"[bold blue]🤖 Solving with fast-downward...[/bold blue]")
    
    try:
        with OneshotPlanner(name='fast-downward') as planner:
            start_time = time.time()
            result = planner.solve(problem)
            solve_time = time.time() - start_time
            
            if result.status.name == 'SOLVED_SATISFICING':
                console.print(f"[green]✅ SUCCESS! Plan found in {solve_time:.3f}s[/green]")
                
                # Display plan
                plan_table = Table(title=f"📋 {scenario_name} - Execution Plan", show_header=True, header_style="bold green")
                plan_table.add_column("Step", style="cyan", justify="center")
                plan_table.add_column("Action", style="white")
                plan_table.add_column("Robot", style="yellow")
                plan_table.add_column("Movement", style="green")
                plan_table.add_column("Description", style="blue")
                
                for i, action in enumerate(result.plan.actions, 1):
                    action_name = action.action.name
                    params = [str(p) for p in action.actual_parameters]
                    robot_param, from_param, to_param = params
                    
                    movement = f"{from_param} → {to_param}"
                    description = f"Robot {robot_param} moves from dock {from_param} to dock {to_param}"
                    
                    plan_table.add_row(str(i), action_name, robot_param, movement, description)
                
                console.print(plan_table)
                
                # Summary
                summary_table = Table(title="📊 Planning Summary", show_header=True, header_style="bold cyan")
                summary_table.add_column("Metric", style="cyan")
                summary_table.add_column("Value", style="white")
                
                summary_table.add_row("Plan Length", f"{len(result.plan.actions)} steps")
                summary_table.add_row("Solve Time", f"{solve_time:.3f} seconds")
                summary_table.add_row("Status", str(result.status))
                summary_table.add_row("Scenario", scenario_name)
                
                console.print(summary_table)
                
                return True, len(result.plan.actions)
            else:
                console.print(f"[red]❌ Planning failed: {result.status}[/red]")
                return False, 0
                
    except Exception as e:
        console.print(f"[red]❌ Error during planning: {e}[/red]")
        return False, 0

def main():
    """Run working multi-step planning scenarios."""
    
    console.print(Panel.fit(
        "[bold blue]🤖 Working Multi-Step Planning Demo[/bold blue]\n"
        "[white]Testing multi-robot scenarios with guaranteed success[/white]",
        border_style="blue"
    ))
    
    scenarios = [
        ("Long Path", scenario_1_long_path),
        ("Robot Coordination", scenario_2_robot_coordination), 
        ("Convergence", scenario_3_convergence),
        ("Complex Network", scenario_4_complex_network)
    ]
    
    results = []
    
    for scenario_name, scenario_func in scenarios:
        console.print(f"\n{'='*60}")
        problem, description = scenario_func()
        success, steps = solve_and_display(problem, description, scenario_name)
        results.append((scenario_name, success, steps))
        
        time.sleep(0.5)
    
    # Final summary
    console.print(f"\n{'='*60}")
    console.print(Panel.fit(
        "[bold green]🏆 Multi-Step Planning Results[/bold green]",
        border_style="green"
    ))
    
    results_table = Table(title="📈 All Scenarios Summary", show_header=True, header_style="bold green")
    results_table.add_column("Scenario", style="cyan")
    results_table.add_column("Status", style="white")
    results_table.add_column("Steps", style="yellow")
    results_table.add_column("Complexity", style="blue")
    
    for scenario_name, success, steps in results:
        status = "✅ Success" if success else "❌ Failed"
        if success:
            if steps <= 2:
                complexity = "Simple"
            elif steps <= 4:
                complexity = "Moderate"
            else:
                complexity = "Complex"
        else:
            complexity = "N/A"
        results_table.add_row(scenario_name, status, str(steps) if success else "N/A", complexity)
    
    console.print(results_table)
    
    successful_scenarios = sum(1 for _, success, _ in results if success)
    total_scenarios = len(results)
    total_steps = sum(steps for _, success, steps in results if success)
    
    if successful_scenarios == total_scenarios:
        console.print(f"\n[bold green]🎉 All {total_scenarios} scenarios completed successfully![/bold green]")
        console.print(f"[bold cyan]📊 Total steps executed: {total_steps}[/bold cyan]")
    else:
        console.print(f"\n[yellow]⚠️  {successful_scenarios}/{total_scenarios} scenarios successful[/yellow]")
    
    return successful_scenarios == total_scenarios

if __name__ == "__main__":
    success = main()
    if success:
        console.print("\n[bold yellow]🚀 Multi-robot coordination demo completed![/bold yellow]")
    else:
        console.print("\n[bold red]❌ Some scenarios failed - debugging needed[/bold red]")
