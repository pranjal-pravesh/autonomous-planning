#!/usr/bin/env python3
"""
Tricky Weight Challenge (Refactored)
- Domain remains general in src/
- This demo constructs all objects and initial state locally
- Expected plan length: 19 actions (same as original)
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


def build_problem_refactored():
    # Create domain WITHOUT auto objects; we'll define state here.
    domain = LogisticsDomain(scale="small", auto_objects=False)
    problem = Problem("tricky_weight_challenge_refactored")

    # Create objects locally
    Robot = domain.Robot
    Dock = domain.Dock
    Container = domain.Container
    Pile = domain.Pile

    r1 = Object("r1", Robot)

    d1 = Object("d1", Dock)
    d2 = Object("d2", Dock)
    d3 = Object("d3", Dock)

    c1 = Object("c1", Container)
    c2 = Object("c2", Container)
    c3 = Object("c3", Container)
    c4 = Object("c4", Container)
    c5 = Object("c5", Container)

    p1 = Object("p1", Pile)
    p2 = Object("p2", Pile)
    p3 = Object("p3", Pile)

    # Register all objects with the problem AND assign to domain for action rules
    all_objects = [r1, d1, d2, d3, c1, c2, c3, c4, c5, p1, p2, p3]
    problem.add_objects(all_objects)
    
    # Assign objects to domain so actions can access them
    domain.assign_objects({
        "robots": [r1],
        "docks": [d1, d2, d3],
        "containers": [c1, c2, c3, c4, c5],
        "piles": [p1, p2, p3],
        "all_objects": all_objects
    })

    # Add fluents (all domain fluents and static fluents)
    for fluent in domain.fluents + domain.static_fluents:
        problem.add_fluent(fluent, default_initial_value=False)

    # Now that domain has objects, build actions and add them
    actions = LogisticsActions(domain)
    for action in actions.get_actions():
        problem.add_action(action)

    # Initial state (identical to original tricky_weight_challenge)
    I = {
        # Robot locations
        domain.robot_at(r1, d1): True,

        # Robot capacities (2 slots for r1)
        domain.robot_can_carry_1(r1): True,
        domain.robot_can_carry_2(r1): True,
        domain.robot_can_carry_3(r1): False,

        # Weight capacity and current weight
        domain.robot_capacity_6(r1): True,
        domain.robot_weight_0(r1): True,

        # Robot load tracking
        domain.robot_has_container_1(r1): False,
        domain.robot_has_container_2(r1): False,
        domain.robot_has_container_3(r1): False,

        # Initialize robot slot tracking (empty)
        domain.container_in_robot_slot_1(r1, c1): False,
        domain.container_in_robot_slot_1(r1, c2): False,
        domain.container_in_robot_slot_1(r1, c3): False,
        domain.container_in_robot_slot_1(r1, c4): False,
        domain.container_in_robot_slot_1(r1, c5): False,

        domain.container_in_robot_slot_2(r1, c1): False,
        domain.container_in_robot_slot_2(r1, c2): False,
        domain.container_in_robot_slot_2(r1, c3): False,
        domain.container_in_robot_slot_2(r1, c4): False,
        domain.container_in_robot_slot_2(r1, c5): False,

        domain.robot_free(r1): True,

        # Container weights
        domain.container_weight_2(c1): True,
        domain.container_weight_4(c2): True,
        domain.container_weight_4(c3): True,
        domain.container_weight_4(c4): True,
        domain.container_weight_4(c5): True,

        # Piles and stacking
        domain.container_in_pile(c1, p1): True,
        domain.container_in_pile(c2, p1): True,
        domain.container_on_top_of_pile(c2, p1): True,
        domain.container_on_top_of_pile(c1, p1): False,
        domain.container_under_in_pile(c1, c2, p1): True,

        domain.container_in_pile(c3, p2): True,
        domain.container_in_pile(c4, p2): True,
        domain.container_in_pile(c5, p2): True,
        domain.container_on_top_of_pile(c5, p2): True,
        domain.container_on_top_of_pile(c4, p2): False,
        domain.container_on_top_of_pile(c3, p2): False,
        domain.container_under_in_pile(c3, c4, p2): True,
        domain.container_under_in_pile(c4, c5, p2): True,

        # Empty p3
        domain.container_in_pile(c1, p3): False,
        domain.container_in_pile(c2, p3): False,
        domain.container_in_pile(c3, p3): False,
        domain.container_in_pile(c4, p3): False,
        domain.container_in_pile(c5, p3): False,

        # Pile locations
        domain.pile_at_dock(p1, d1): True,
        domain.pile_at_dock(p2, d2): True,
        domain.pile_at_dock(p3, d3): True,

        # Adjacency
        domain.adjacent(d1, d2): True,
        domain.adjacent(d2, d1): True,
        domain.adjacent(d2, d3): True,
        domain.adjacent(d3, d2): True,
        domain.adjacent(d3, d1): True,
        domain.adjacent(d1, d3): True,
    }

    for f, v in I.items():
        problem.set_initial_value(f, v)

    # Goal conditions (identical to original)
    goal = And(
        domain.container_in_pile(c4, p3),
        domain.container_in_pile(c5, p3),
        domain.container_in_pile(c1, p3),
        domain.container_in_pile(c2, p3),
        domain.container_in_pile(c3, p2),
        domain.container_on_top_of_pile(c2, p3),
        domain.container_under_in_pile(c1, c2, p3),
        domain.container_under_in_pile(c5, c1, p3),
        domain.container_under_in_pile(c4, c5, p3),
        domain.container_on_top_of_pile(c3, p2),
    )
    problem.add_goal(goal)

    # For display utilities
    domain_objects = {
        "robots": [r1],
        "docks": [d1, d2, d3],
        "containers": [c1, c2, c3, c4, c5],
        "piles": [p1, p2, p3],
        "all_objects": [r1, d1, d2, d3, c1, c2, c3, c4, c5, p1, p2, p3]
    }

    return problem, domain, domain_objects


def solve_refactored():
    console.print(Panel("⚖️ Tricky Weight Challenge (Refactored)\nDomain is independent; demo builds world and state locally", title="Refactored Tricky Weight", title_align="left", border_style="blue"))

    problem, domain, domain_objects = build_problem_refactored()

    LogisticsDisplay.display_domain_info(domain_objects)

    console.print(f"\n[bold blue]🤖 Solving refactored tricky weight challenge...[/bold blue]")

    with OneshotPlanner(name='fast-downward') as planner:
        start = time.time()
        result = planner.solve(problem)
        elapsed = time.time() - start

    if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
        console.print(f"[bold green]✅ SUCCESS! Completed in {elapsed:.3f}s[/bold green]")

        if result.plan:
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Step", style="dim", width=6, justify="center")
            table.add_column("Action", style="cyan", width=12)
            table.add_column("Params", style="white")

            for i, action in enumerate(result.plan.actions, 1):
                table.add_row(str(i), action.action.name, ", ".join(str(p) for p in action.actual_parameters))

            console.print(table)

            if len(result.plan.actions) == 19:
                console.print("[bold green]🎯 Plan length matches expected 19 steps[/bold green]")
            else:
                console.print(f"[bold yellow]ℹ️ Plan length = {len(result.plan.actions)} (expected 19). This can vary with planner heuristics but should generally match if model is identical.[/bold yellow]")

        return True, len(result.plan.actions) if result.plan else 0

    console.print(f"[bold red]❌ Failed: {result.status}[/bold red]")
    return False, 0


def main():
    solve_refactored()


if __name__ == "__main__":
    main()


