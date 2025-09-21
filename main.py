#!/usr/bin/env python3
"""
Main script for the Automated Planning Example 2.3 simulation.
Provides a command-line interface to run different planning scenarios.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from typing import Optional
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.problem import ExampleProblems
from src.solver import LogisticsSolver

app = typer.Typer(help="Automated Planning - Example 2.3 Logistics Domain Simulation")
console = Console()


@app.command()
def run(
    problem: str = typer.Option(
        "move_robot", 
        "--problem", "-p",
        help="Problem to solve: move_robot, move_container, complex_goal, swap_containers"
    ),
    planner: str = typer.Option(
        "pyperplan",
        "--planner", "-pl",
        help="Planner to use: pyperplan, fast-downward"
    ),
    list_problems: bool = typer.Option(
        False,
        "--list", "-l",
        help="List all available problems"
    )
):
    """Run the logistics domain simulation with specified problem and planner."""
    
    if list_problems:
        console.print(Panel.fit(
            "[bold blue]📋 Available Problems[/bold blue]",
            border_style="blue"
        ))
        
        problems_info = {
            "move_robot": "Move robot r1 to dock d3",
            "move_container": "Move container c1 to pile p2", 
            "complex_goal": "Move r1 to d3 AND move c1 to p2",
            "swap_containers": "Swap positions of c1 and c3"
        }
        
        for prob_name, description in problems_info.items():
            console.print(f"  • [cyan]{prob_name}[/cyan]: {description}")
        return
    
    # Create solver and example problems
    solver = LogisticsSolver()
    examples = ExampleProblems()
    
    # Get all available problems
    all_problems = examples.get_all_problems()
    
    if problem not in all_problems:
        console.print(f"[red]❌ Unknown problem: {problem}[/red]")
        console.print(f"Available problems: {', '.join(all_problems.keys())}")
        console.print("Use --list to see all available problems")
        raise typer.Exit(1)
    
    # Get the selected problem
    selected_problem = all_problems[problem]
    
    # Display welcome message
    console.print(Panel.fit(
        "[bold blue]🤖 Automated Planning - Example 2.3[/bold blue]\n"
        "[white]Logistics Domain Simulation[/white]",
        border_style="blue"
    ))
    
    # Solve and display
    result = solver.solve_and_display(selected_problem, planner)
    
    if result:
        console.print("\n[bold green]🎉 Planning completed successfully![/bold green]")
    else:
        console.print("\n[bold red]❌ Planning failed![/bold red]")
        raise typer.Exit(1)


@app.command()
def interactive():
    """Run an interactive session to explore different problems."""
    console.print(Panel.fit(
        "[bold blue]🤖 Interactive Planning Session[/bold blue]\n"
        "[white]Explore the logistics domain interactively[/white]",
        border_style="blue"
    ))
    
    solver = LogisticsSolver()
    examples = ExampleProblems()
    all_problems = examples.get_all_problems()
    
    while True:
        console.print("\n[bold cyan]Available Problems:[/bold cyan]")
        for i, (name, _) in enumerate(all_problems.items(), 1):
            console.print(f"  {i}. {name}")
        console.print("  0. Exit")
        
        try:
            choice = typer.prompt("Select a problem (number)", type=int)
            
            if choice == 0:
                console.print("[yellow]👋 Goodbye![/yellow]")
                break
            elif 1 <= choice <= len(all_problems):
                problem_name = list(all_problems.keys())[choice - 1]
                problem = all_problems[problem_name]
                
                console.print(f"\n[bold green]Solving: {problem_name}[/bold green]")
                result = solver.solve_and_display(problem)
                
                if result:
                    console.print("\n[green]✅ Problem solved![/green]")
                else:
                    console.print("\n[red]❌ Problem failed![/red]")
            else:
                console.print("[red]❌ Invalid choice![/red]")
                
        except (ValueError, KeyboardInterrupt):
            console.print("\n[yellow]👋 Goodbye![/yellow]")
            break


@app.command()
def demo():
    """Run a demonstration of all example problems."""
    console.print(Panel.fit(
        "[bold blue]🎬 Planning Demonstration[/bold blue]\n"
        "[white]Running all example problems[/white]",
        border_style="blue"
    ))
    
    solver = LogisticsSolver()
    examples = ExampleProblems()
    all_problems = examples.get_all_problems()
    
    for i, (name, problem) in enumerate(all_problems.items(), 1):
        console.print(f"\n[bold cyan]--- Problem {i}/{len(all_problems)}: {name} ---[/bold cyan]")
        result = solver.solve_and_display(problem)
        
        if result:
            console.print(f"[green]✅ {name} solved successfully![/green]")
        else:
            console.print(f"[red]❌ {name} failed![/red]")
        
        if i < len(all_problems):
            input("\nPress Enter to continue to next problem...")


@app.command()
def demos():
    """Run advanced planning demonstrations."""
    console.print(Panel.fit(
        "[bold blue]🎬 Advanced Planning Demos[/bold blue]\n"
        "[white]Run advanced logistics scenarios[/white]",
        border_style="blue"
    ))
    
    import subprocess
    import sys
    
    demos_info = {
        "multi_robot": "Multi-robot coordination scenarios",
        "container_redistribution": "Simple container redistribution using src/ structure",
        "large_scale": "Large-scale redistribution using src/ structure (8 docks, 12 piles, 15 containers, 3 robots)"
    }
    
    console.print("\n[bold cyan]Available Demos:[/bold cyan]")
    for i, (name, description) in enumerate(demos_info.items(), 1):
        console.print(f"  {i}. [cyan]{name}[/cyan]: {description}")
    console.print("  0. Exit")
    
    try:
        choice = typer.prompt("Select a demo (number)", type=int)
        
        if choice == 0:
            console.print("[yellow]👋 Goodbye![/yellow]")
            return
        elif choice == 1:
            console.print("\n[bold green]Running multi-robot coordination demo...[/bold green]")
            subprocess.run([sys.executable, "demos/multi_robot_coordination.py"])
        elif choice == 2:
            console.print("\n[bold green]Running container redistribution demo...[/bold green]")
            subprocess.run([sys.executable, "demos/container_redistribution.py"])
        elif choice == 3:
            console.print("\n[bold green]Running large-scale redistribution demo...[/bold green]")
            subprocess.run([sys.executable, "demos/large_scale_redistribution.py"])
        else:
            console.print("[red]❌ Invalid choice![/red]")
            
    except (ValueError, KeyboardInterrupt):
        console.print("\n[yellow]👋 Goodbye![/yellow]")


if __name__ == "__main__":
    app()
