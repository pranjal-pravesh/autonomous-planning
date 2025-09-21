"""
Display utilities for logistics planning scenarios.
Provides rich console output for distributions, plans, and domain information.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import Dict, List, Tuple, Any
from unified_planning.model import Problem, Fluent
from unified_planning.model.object import Object

console = Console()


class LogisticsDisplay:
    """Display utilities for logistics planning scenarios."""
    
    @staticmethod
    def display_domain_info(domain_objects: Dict[str, List[Object]], title: str = "Logistics Domain"):
        """Display basic domain information."""
        console.print(Panel.fit(
            f"[bold blue]🏭 {title}[/bold blue]\n"
            "[white]Domain objects and structure[/white]",
            border_style="blue"
        ))
        
        # Objects summary
        objects_table = Table(title="📦 Domain Objects", show_header=True, header_style="bold cyan")
        objects_table.add_column("Type", style="cyan")
        objects_table.add_column("Count", style="white")
        objects_table.add_column("Objects", style="yellow")
        
        for obj_type, objects in domain_objects.items():
            if obj_type != "all_objects":
                objects_table.add_row(
                    obj_type.title(),
                    str(len(objects)),
                    ", ".join([obj.name for obj in objects])
                )
        
        console.print(objects_table)
    
    @staticmethod
    def display_initial_distribution(initial_state: Dict[str, Any], title: str = "Initial Distribution"):
        """Display initial container distribution."""
        console.print(Panel.fit(
            f"[bold cyan]📦 {title}[/bold cyan]\n"
            "[white]Starting state with container placement[/white]",
            border_style="cyan"
        ))
        
        # Initial distribution table
        initial_table = Table(title="🏭 Initial State", show_header=True, header_style="bold cyan")
        initial_table.add_column("Dock", style="cyan")
        initial_table.add_column("Pile", style="white")
        initial_table.add_column("Containers", style="green")
        initial_table.add_column("Count", style="yellow")
        initial_table.add_column("Robot", style="red")
        
        for dock_info in initial_state.get("dock_distributions", []):
            initial_table.add_row(
                dock_info["dock"],
                dock_info["pile"],
                dock_info["containers"],
                str(dock_info["count"]),
                dock_info.get("robot", "-")
            )
        
        console.print(initial_table)
    
    @staticmethod
    def display_target_distribution(target_state: Dict[str, Any], title: str = "Target Distribution"):
        """Display target container distribution."""
        console.print(Panel.fit(
            f"[bold green]🎯 {title}[/bold green]\n"
            "[white]Goal state for redistribution[/white]",
            border_style="green"
        ))
        
        # Target distribution table
        target_table = Table(title="🎯 Target State", show_header=True, header_style="bold green")
        target_table.add_column("Dock", style="cyan")
        target_table.add_column("Target Pile", style="white")
        target_table.add_column("Target Containers", style="green")
        target_table.add_column("Count", style="yellow")
        target_table.add_column("Change", style="red")
        target_table.add_column("Reason", style="blue")
        
        for dock_info in target_state.get("dock_distributions", []):
            target_table.add_row(
                dock_info["dock"],
                dock_info["pile"],
                dock_info["containers"],
                str(dock_info["count"]),
                dock_info["change"],
                dock_info.get("reason", "")
            )
        
        console.print(target_table)
    
    @staticmethod
    def display_distribution_summary(initial_state: Dict[str, Any], target_state: Dict[str, Any]):
        """Display distribution summary comparing initial and target states."""
        summary_table = Table(title="📊 Distribution Summary", show_header=True, header_style="bold magenta")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Initial", style="white")
        summary_table.add_column("Target", style="green")
        summary_table.add_column("Change", style="red")
        
        # Calculate totals
        initial_total = sum(dock["count"] for dock in initial_state.get("dock_distributions", []))
        target_total = sum(dock["count"] for dock in target_state.get("dock_distributions", []))
        
        summary_table.add_row("Total Containers", str(initial_total), str(target_total), f"{target_total - initial_total:+d}")
        
        # Add specific metrics
        for metric in initial_state.get("summary_metrics", []):
            summary_table.add_row(
                metric["name"],
                str(metric["initial"]),
                str(metric["target"]),
                metric["change"]
            )
        
        console.print(summary_table)
    
    @staticmethod
    def display_network_connectivity(connections: List[Tuple[str, str]], title: str = "Network Connectivity"):
        """Display network connectivity information."""
        network_table = Table(title=f"🕸️ {title}", show_header=True, header_style="bold magenta")
        network_table.add_column("Dock", style="cyan")
        network_table.add_column("Connected To", style="white")
        network_table.add_column("Piles", style="yellow")
        
        # Group connections by dock
        dock_connections = {}
        for dock_a, dock_b in connections:
            if dock_a not in dock_connections:
                dock_connections[dock_a] = []
            dock_connections[dock_a].append(dock_b)
        
        for dock, connected_docks in dock_connections.items():
            network_table.add_row(
                dock,
                ", ".join(connected_docks),
                "Multiple" if len(connected_docks) > 2 else "Standard"
            )
        
        console.print(network_table)
    
    @staticmethod
    def display_plan_execution(plan_result, title: str = "Plan Execution"):
        """Display plan execution results."""
        if not plan_result or not plan_result.plan:
            console.print(f"[red]❌ {title}: No plan found[/red]")
            return
        
        plan_table = Table(title=f"📋 {title}", show_header=True, header_style="bold green")
        plan_table.add_column("Step", style="cyan", justify="center")
        plan_table.add_column("Action", style="white")
        plan_table.add_column("Robot", style="yellow")
        plan_table.add_column("Details", style="green")
        plan_table.add_column("Purpose", style="blue")
        
        for i, action in enumerate(plan_result.plan.actions, 1):
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
    
    @staticmethod
    def display_plan_summary(plan_result, solve_time: float, description: str = "Planning Summary"):
        """Display plan summary statistics."""
        summary_table = Table(title=f"📊 {description}", show_header=True, header_style="bold cyan")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="white")
        
        plan_length = len(plan_result.plan.actions) if plan_result and plan_result.plan else 0
        
        summary_table.add_row("Total Actions", str(plan_length))
        summary_table.add_row("Solve Time", f"{solve_time:.3f} seconds")
        summary_table.add_row("Status", "✅ SUCCESS" if plan_result and plan_result.status.name == 'SOLVED_SATISFICING' else "❌ FAILED")
        
        console.print(summary_table)
    
    @staticmethod
    def display_large_scale_distribution(initial_distributions: List[Dict], target_distributions: List[Dict]):
        """Display large-scale distribution with detailed pile structure."""
        
        # Initial state with detailed pile structure
        initial_table = Table(title="📦 Initial Container Distribution (Bottom → Top)", show_header=True, header_style="bold cyan")
        initial_table.add_column("Dock", style="cyan")
        initial_table.add_column("Pile", style="white")
        initial_table.add_column("Stack Order", style="yellow")
        initial_table.add_column("Count", style="green")
        initial_table.add_column("Top Container", style="red")
        
        for dist in initial_distributions:
            initial_table.add_row(
                dist["dock"],
                dist["pile"],
                dist["stack_order"],
                str(dist["count"]),
                dist["top_container"]
            )
        
        console.print(initial_table)
        
        # Summary by dock
        summary_table = Table(title="📊 Dock Summary", show_header=True, header_style="bold magenta")
        summary_table.add_column("Dock", style="cyan")
        summary_table.add_column("Total Containers", style="green")
        summary_table.add_column("Piles Used", style="white")
        summary_table.add_column("Pile Distribution", style="yellow")
        
        # Group by dock
        dock_summary = {}
        for dist in initial_distributions:
            dock = dist["dock"]
            if dock not in dock_summary:
                dock_summary[dock] = {"total": 0, "piles": [], "pile_info": [], "occupied_piles": 0}
            dock_summary[dock]["total"] += dist["count"]
            dock_summary[dock]["piles"].append(dist["pile"])
            dock_summary[dock]["pile_info"].append(f"{dist['pile']}({dist['count']})")
            if dist["count"] > 0:  # Only count piles with containers
                dock_summary[dock]["occupied_piles"] += 1
        
        for dock, info in dock_summary.items():
            summary_table.add_row(
                dock,
                str(info["total"]),
                f"{info['occupied_piles']}/{len(info['piles'])}",
                ", ".join(info["pile_info"])
            )
        
        console.print(summary_table)
        
        # Target state
        goal_table = Table(title="🎯 Target Container Distribution (Bottom → Top)", show_header=True, header_style="bold green")
        goal_table.add_column("Dock", style="cyan")
        goal_table.add_column("Target Pile", style="white")
        goal_table.add_column("Target Stack", style="yellow")
        goal_table.add_column("Count", style="green")
        goal_table.add_column("Change", style="white")
        goal_table.add_column("Top Container", style="red")
        
        for dist in target_distributions:
            goal_table.add_row(
                dist["dock"],
                dist["pile"],
                dist["target_stack"],
                str(dist["count"]),
                dist["change"],
                dist["top_container"]
            )
        
        console.print(goal_table)
