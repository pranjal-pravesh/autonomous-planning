#!/usr/bin/env python3
"""
Working demo of Example 2.3 from Automated Planning textbook.
"""

from unified_planning.shortcuts import *
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def main():
    """Create and solve a simple logistics planning problem."""
    
    console.print(Panel.fit(
        "[bold blue]🤖 Automated Planning - Example 2.3[/bold blue]\n"
        "[white]Working Demo with Correct Unified Planning Syntax[/white]",
        border_style="blue"
    ))
    
    # Create problem
    problem = Problem("logistics_demo")
    
    # Define types
    Robot = UserType("Robot")
    Dock = UserType("Dock")
    
    # Create objects
    r1 = Object("r1", Robot)
    d1 = Object("d1", Dock)
    d2 = Object("d2", Dock)
    d3 = Object("d3", Dock)
    
    problem.add_objects([r1, d1, d2, d3])
    
    # Create fluents - use boolean fluents for PDDL compatibility
    robot_at = Fluent("robot_at", BoolType(), robot=Robot, dock=Dock)
    dock_occupied = Fluent("dock_occupied", BoolType(), dock=Dock)
    adjacent = Fluent("adjacent", BoolType(), dock1=Dock, dock2=Dock)
    
    problem.add_fluent(robot_at)
    problem.add_fluent(dock_occupied, default_initial_value=False)
    problem.add_fluent(adjacent, default_initial_value=False)
    
    # Create move action with correct syntax
    move = InstantaneousAction("move", robot=Robot, from_dock=Dock, to_dock=Dock)
    robot = move.parameter("robot")
    from_dock = move.parameter("from_dock")
    to_dock = move.parameter("to_dock")
    
    # Add preconditions - use boolean fluents
    move.add_precondition(robot_at(robot, from_dock))
    move.add_precondition(adjacent(from_dock, to_dock))
    move.add_precondition(Not(dock_occupied(to_dock)))
    
    # Add effects
    move.add_effect(robot_at(robot, from_dock), False)
    move.add_effect(robot_at(robot, to_dock), True)
    move.add_effect(dock_occupied(from_dock), False)
    move.add_effect(dock_occupied(to_dock), True)
    
    problem.add_action(move)
    
    # Set initial state (from Example 2.3)
    problem.set_initial_value(robot_at(r1, d1), True)
    problem.set_initial_value(robot_at(r1, d2), False)
    problem.set_initial_value(robot_at(r1, d3), False)
    problem.set_initial_value(dock_occupied(d1), True)
    problem.set_initial_value(dock_occupied(d2), False)
    problem.set_initial_value(dock_occupied(d3), False)
    
    # Set adjacency (triangular network from Figure 2.3)
    problem.set_initial_value(adjacent(d1, d2), True)
    problem.set_initial_value(adjacent(d2, d1), True)
    problem.set_initial_value(adjacent(d2, d3), True)
    problem.set_initial_value(adjacent(d3, d2), True)
    problem.set_initial_value(adjacent(d1, d3), True)
    problem.set_initial_value(adjacent(d3, d1), True)
    
    # Set goal: move robot r1 to dock d3
    problem.add_goal(robot_at(r1, d3))
    
    # Display problem setup
    console.print("\n[bold green]🌱 Problem Setup:[/bold green]")
    console.print(f"• Robot r1 starts at dock d1")
    console.print(f"• Goal: Move r1 to dock d3")
    console.print(f"• Docks are connected in triangular network")
    
    console.print("\n[bold blue]🤖 Solving with fast-downward...[/bold blue]")
    
    # Solve the problem
    try:
        with OneshotPlanner(name='fast-downward') as planner:
            result = planner.solve(problem)
            
            if result.status.name == 'SOLVED_SATISFICING':
                console.print("[green]✅ SUCCESS! Plan found![/green]")
                
                # Display plan
                plan_table = Table(title="📋 Execution Plan", show_header=True, header_style="bold green")
                plan_table.add_column("Step", style="cyan", justify="center")
                plan_table.add_column("Action", style="white")
                plan_table.add_column("Parameters", style="yellow")
                plan_table.add_column("Result", style="green")
                
                for i, action in enumerate(result.plan.actions, 1):
                    action_name = action.action.name
                    params = [str(p) for p in action.actual_parameters]
                    robot_param, from_param, to_param = params
                    
                    result_text = f"Robot {robot_param} moves from dock {from_param} to dock {to_param}"
                    plan_table.add_row(str(i), action_name, f"{robot_param}, {from_param} → {to_param}", result_text)
                
                console.print(plan_table)
                
                # Summary
                console.print(f"\n[bold green]📊 Planning Results:[/bold green]")
                console.print(f"   • Plan length: {len(result.plan.actions)} steps")
                console.print(f"   • Planning status: {result.status}")
                console.print(f"   • Final robot location: dock d3")
                
                console.print("\n[bold yellow]🎉 AUTOMATED PLANNING IS WORKING![/bold yellow]")
                console.print("\n[bold cyan]💡 This demonstrates:[/bold cyan]")
                console.print("   ✅ State-variable modeling (Chapter 2 concepts)")
                console.print("   ✅ Forward state-space search algorithms")
                console.print("   ✅ STRIPS planning with preconditions & effects")
                console.print("   ✅ Unified Planning library integration")
                console.print("   ✅ Beautiful rich console visualization")
                
                return True
            else:
                console.print(f"[red]❌ Planning failed: {result.status}[/red]")
                return False
                
    except Exception as e:
        console.print(f"[red]❌ Error during planning: {e}[/red]")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        console.print("\n[bold green]🚀 Demo completed successfully![/bold green]")
        console.print("\n[bold blue]📁 Project Structure:[/bold blue]")
        console.print("   • /src/ - Core domain, actions, problem definitions")
        console.print("   • /examples/ - Example scenarios")
        console.print("   • /docs/ - Theory and implementation guides")
        console.print("   • main.py - Full CLI interface")
        console.print("   • demo.py - This working demonstration")
        console.print("   • README.md - Complete documentation")
        
        console.print("\n[bold green]✨ Ready for Extension:[/bold green]")
        console.print("   • Multiple robots and containers")
        console.print("   • Load/unload actions for container handling")
        console.print("   • Complex multi-step goals")
        console.print("   • Different planning algorithms (A*, GBFS)")
        console.print("   • Heuristic comparisons (h_add, h_max, h_ff)")
    else:
        console.print("\n[bold red]❌ Demo failed - check unified planning setup[/bold red]")