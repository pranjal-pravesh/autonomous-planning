"""
Planning solver with rich console output for the logistics domain.
Provides beautiful visualization of the planning process and results.
"""

from unified_planning.shortcuts import *
from unified_planning.engines import PlanGenerationResult
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from typing import Dict, List, Any, Optional
import time


class LogisticsSolver:
    """Planning solver with rich console output for the logistics domain."""
    
    def __init__(self):
        self.console = Console()
        self.available_planners = ["pyperplan", "fast-downward"]
    
    def solve_problem(self, problem: Problem, planner_name: str = "pyperplan", heuristic: str = "default") -> Optional[PlanGenerationResult]:
        """
        Solve a planning problem using the specified planner and heuristic.
        
        Args:
            problem: The planning problem to solve
            planner_name: Name of the planner to use
            heuristic: Heuristic to use for Fast Downward
            
        Returns:
            PlanGenerationResult if successful, None otherwise
        """
        self.console.print(f"\n[bold blue]🤖 Solving with {planner_name} planner...[/bold blue]")
        if heuristic != "default":
            self.console.print(f"[bold blue]🎯 Using heuristic: {heuristic}[/bold blue]")
        
        try:
            # Use fast-downward instead of pyperplan for equality support
            planner_name = 'fast-downward' if planner_name == 'pyperplan' else planner_name
            
            # Configure Fast Downward with specific heuristics for logistics
            if planner_name == 'fast-downward' and heuristic != "default":
                # Try different heuristics that work well for logistics problems
                heuristics_config = {
                    "h_ff": "--search 'astar(ff())'",
                    "h_add": "--search 'astar(add())'", 
                    "h_max": "--search 'astar(max())'",
                    "h_lmcut": "--search 'astar(lmcut())'",
                    "h_cea": "--search 'astar(cea())'",
                    "h_cg": "--search 'astar(cg())'",
                    "h_goalcount": "--search 'astar(goalcount())'",
                    "gbfs_ff": "--search 'eager_greedy([ff()])'",
                    "gbfs_add": "--search 'eager_greedy([add()])'",
                    "gbfs_cea": "--search 'eager_greedy([cea()])'"
                }
                
                if heuristic in heuristics_config:
                    # Use the specific heuristic configuration
                    with OneshotPlanner(name=planner_name, params=heuristics_config[heuristic]) as planner:
                        start_time = time.time()
                        result = planner.solve(problem)
                        solve_time = time.time() - start_time
                        return self._handle_result(result, solve_time, heuristic)
                else:
                    self.console.print(f"[yellow]⚠️ Unknown heuristic '{heuristic}', using default[/yellow]")
            
            # Default planner configuration
            with OneshotPlanner(name=planner_name) as planner:
                start_time = time.time()
                result = planner.solve(problem)
                solve_time = time.time() - start_time
                return self._handle_result(result, solve_time, "default")
                    
        except Exception as e:
            self.console.print(f"[red]❌ Error with {planner_name}: {str(e)}[/red]")
            return None
    
    def _handle_result(self, result: PlanGenerationResult, solve_time: float, heuristic: str) -> Optional[PlanGenerationResult]:
        """Handle the planning result and display appropriate messages."""
        if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
            self.console.print(f"[green]✅ Plan found in {solve_time:.2f} seconds![/green]")
            if heuristic != "default":
                self.console.print(f"[green]🎯 Heuristic '{heuristic}' succeeded![/green]")
            return result
        elif result.status == PlanGenerationResultStatus.SOLVED_OPTIMALLY:
            self.console.print(f"[green]✅ Optimal plan found in {solve_time:.2f} seconds![/green]")
            if heuristic != "default":
                self.console.print(f"[green]🎯 Heuristic '{heuristic}' found optimal solution![/green]")
            return result
        else:
            self.console.print(f"[red]❌ Planning failed: {result.status}[/red]")
            if heuristic != "default":
                self.console.print(f"[red]🎯 Heuristic '{heuristic}' failed[/red]")
            return None
    
    def display_problem_info(self, problem: Problem) -> None:
        """Display comprehensive problem information."""
        # Problem header
        self.console.print(Panel.fit(
            f"[bold blue]📋 Planning Problem: {problem.name}[/bold blue]",
            border_style="blue"
        ))
        
        # Objects table
        objects_table = Table(title="🏗️ Domain Objects", show_header=True, header_style="bold magenta")
        objects_table.add_column("Type", style="cyan")
        objects_table.add_column("Objects", style="white")
        
        # Group objects by type
        objects_by_type = {}
        for obj in problem.all_objects:
            obj_type = str(obj.type)
            if obj_type not in objects_by_type:
                objects_by_type[obj_type] = []
            objects_by_type[obj_type].append(str(obj))
        
        for obj_type, objects in objects_by_type.items():
            objects_table.add_row(obj_type, ", ".join(objects))
        
        self.console.print(objects_table)
        
        # Fluents table
        fluents_table = Table(title="🔧 State Variables (Fluents)", show_header=True, header_style="bold magenta")
        fluents_table.add_column("Fluent", style="cyan")
        fluents_table.add_column("Type", style="white")
        fluents_table.add_column("Parameters", style="yellow")
        
        for fluent in problem.fluents:
            params = ", ".join([f"{p.name}: {p.type}" for p in fluent.signature])
            fluents_table.add_row(fluent.name, str(fluent.type), params)
        
        self.console.print(fluents_table)
        
        # Actions table
        actions_table = Table(title="⚡ Available Actions", show_header=True, header_style="bold magenta")
        actions_table.add_column("Action", style="cyan")
        actions_table.add_column("Parameters", style="white")
        
        for action in problem.actions:
            params = ", ".join([f"{p.name}: {p.type}" for p in action.parameters])
            actions_table.add_row(action.name, params)
        
        self.console.print(actions_table)
    
    def display_initial_state(self, problem: Problem) -> None:
        """Display the initial state in a readable format."""
        self.console.print(Panel.fit(
            "[bold green]🌱 Initial State[/bold green]",
            border_style="green"
        ))
        
        # Robot state
        robot_table = Table(title="🤖 Robot State", show_header=True, header_style="bold cyan")
        robot_table.add_column("Robot", style="cyan")
        robot_table.add_column("Location", style="white")
        robot_table.add_column("Cargo", style="yellow")
        
        for obj in problem.all_objects:
            if str(obj.type) == "Robot":
                loc = problem.initial_value(problem.fluent("loc")(obj))
                cargo = problem.initial_value(problem.fluent("cargo")(obj))
                robot_table.add_row(str(obj), str(loc), str(cargo))
        
        self.console.print(robot_table)
        
        # Dock state
        dock_table = Table(title="🏗️ Dock State", show_header=True, header_style="bold cyan")
        dock_table.add_column("Dock", style="cyan")
        dock_table.add_column("Occupied", style="white")
        
        for obj in problem.all_objects:
            if str(obj.type) == "Dock":
                occupied = problem.initial_value(problem.fluent("occupied")(obj))
                dock_table.add_row(str(obj), "✅ Yes" if occupied else "❌ No")
        
        self.console.print(dock_table)
        
        # Container and pile state
        container_table = Table(title="📦 Container & Pile State", show_header=True, header_style="bold cyan")
        container_table.add_column("Container", style="cyan")
        container_table.add_column("Position", style="white")
        container_table.add_column("Pile", style="yellow")
        
        for obj in problem.all_objects:
            if str(obj.type) == "Container":
                pos = problem.initial_value(problem.fluent("pos")(obj))
                pile = problem.initial_value(problem.fluent("pile")(obj))
                container_table.add_row(str(obj), str(pos), str(pile))
        
        self.console.print(container_table)
        
        # Pile tops
        pile_table = Table(title="🗂️ Pile Tops", show_header=True, header_style="bold cyan")
        pile_table.add_column("Pile", style="cyan")
        pile_table.add_column("Top Container", style="white")
        
        for obj in problem.all_objects:
            if str(obj.type) == "Pile":
                top = problem.initial_value(problem.fluent("top")(obj))
                pile_table.add_row(str(obj), str(top))
        
        self.console.print(pile_table)
    
    def display_goals(self, problem: Problem) -> None:
        """Display the problem goals."""
        if not problem.goals:
            self.console.print("[yellow]⚠️ No goals specified[/yellow]")
            return
        
        self.console.print(Panel.fit(
            "[bold red]🎯 Goals[/bold red]",
            border_style="red"
        ))
        
        goals_table = Table(title="Goal Conditions", show_header=True, header_style="bold red")
        goals_table.add_column("Goal", style="white")
        
        for i, goal in enumerate(problem.goals, 1):
            goals_table.add_row(f"{i}. {goal}")
        
        self.console.print(goals_table)
    
    def display_plan(self, result: PlanGenerationResult) -> None:
        """Display the found plan in a beautiful format."""
        if not result.plan:
            self.console.print("[red]❌ No plan to display[/red]")
            return
        
        self.console.print(Panel.fit(
            f"[bold green]📋 Plan Found ({len(result.plan.actions)} steps)[/bold green]",
            border_style="green"
        ))
        
        plan_table = Table(title="Execution Plan", show_header=True, header_style="bold green")
        plan_table.add_column("Step", style="cyan", justify="center")
        plan_table.add_column("Action", style="white")
        plan_table.add_column("Parameters", style="yellow")
        
        for i, action in enumerate(result.plan.actions, 1):
            action_name = action.action.name
            params = ", ".join([str(param) for param in action.actual_parameters])
            plan_table.add_row(str(i), action_name, params)
        
        self.console.print(plan_table)
        
        # Plan summary
        self.console.print(f"\n[bold green]📊 Plan Summary:[/bold green]")
        self.console.print(f"   • Total steps: {len(result.plan.actions)}")
        self.console.print(f"   • Plan cost: {result.plan.cost if hasattr(result.plan, 'cost') else 'N/A'}")
        self.console.print(f"   • Status: {result.status}")
    
    def display_planning_summary(self, problem: Problem, result: Optional[PlanGenerationResult], solve_time: float) -> None:
        """Display a comprehensive planning summary."""
        summary_table = Table(title="📊 Planning Summary", show_header=True, header_style="bold blue")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="white")
        
        summary_table.add_row("Problem", problem.name)
        summary_table.add_row("Objects", str(len(problem.all_objects)))
        summary_table.add_row("Fluents", str(len(problem.fluents)))
        summary_table.add_row("Actions", str(len(problem.actions)))
        summary_table.add_row("Goals", str(len(problem.goals)))
        summary_table.add_row("Solve Time", f"{solve_time:.2f}s")
        
        if result:
            summary_table.add_row("Status", "✅ Solved")
            summary_table.add_row("Plan Length", str(len(result.plan.actions)))
        else:
            summary_table.add_row("Status", "❌ Failed")
            summary_table.add_row("Plan Length", "N/A")
        
        self.console.print(summary_table)
    
    def solve_and_display(self, problem: Problem, planner_name: str = "pyperplan") -> Optional[PlanGenerationResult]:
        """
        Solve a problem and display all information in a beautiful format.
        
        Args:
            problem: The planning problem to solve
            planner_name: Name of the planner to use
            
        Returns:
            PlanGenerationResult if successful, None otherwise
        """
        # Display problem information
        self.display_problem_info(problem)
        self.console.print()
        
        # Display initial state
        self.display_initial_state(problem)
        self.console.print()
        
        # Display goals
        self.display_goals(problem)
        self.console.print()
        
        # Solve the problem
        start_time = time.time()
        result = self.solve_problem(problem, planner_name)
        solve_time = time.time() - start_time
        
        # Display results
        if result:
            self.display_plan(result)
            self.console.print()
        
        # Display summary
        self.display_planning_summary(problem, result, solve_time)
        
        return result
