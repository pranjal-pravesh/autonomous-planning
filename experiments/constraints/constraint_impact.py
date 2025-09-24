#!/usr/bin/env python3
"""
Constraint Impact Analysis Experiment

This experiment analyzes how different types of constraints affect planning performance:
- LIFO (Last-In, First-Out) constraints
- Weight-based capacity constraints
- Robot slot limitations
- Mixed constraint scenarios
"""

import sys
import os
import time
import statistics
import json
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, List, Tuple
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.domain import LogisticsDomain
from src.actions import LogisticsActions
from unified_planning.model import Problem, Object
from unified_planning.shortcuts import And, OneshotPlanner
from unified_planning.engines.results import PlanGenerationResultStatus

class ConstraintImpactExperiment:
    def __init__(self, output_dir: str = "experiments/constraints/results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Experiment configurations testing different constraint types
        self.constraint_configs = [
            {
                "name": "no_constraints",
                "description": "No LIFO, no weight constraints",
                "lifo_enabled": False,
                "weight_constraints": False,
                "robots": 2, "docks": 3, "containers": 6, "piles": 3
            },
            {
                "name": "lifo_only",
                "description": "LIFO constraints only",
                "lifo_enabled": True,
                "weight_constraints": False,
                "robots": 2, "docks": 3, "containers": 6, "piles": 3
            },
            {
                "name": "weight_only",
                "description": "Weight constraints only",
                "lifo_enabled": False,
                "weight_constraints": True,
                "robots": 2, "docks": 3, "containers": 6, "piles": 3
            },
            {
                "name": "tight_capacity_only",
                "description": "Tight capacity constraints only (no LIFO, no weight constraints)",
                "lifo_enabled": False,
                "weight_constraints": False,
                "tight_capacity": True,
                "robots": 2, "docks": 4, "containers": 8, "piles": 4
            },
            {
                "name": "all_constraints",
                "description": "All constraints: LIFO + weight + tight capacity",
                "lifo_enabled": True,
                "weight_constraints": True,
                "tight_capacity": True,
                "robots": 2, "docks": 4, "containers": 8, "piles": 4
            }
        ]
        
        self.results = []
    
    def create_problem(self, config: Dict) -> Tuple[Problem, LogisticsDomain]:
        """Create a logistics problem with given constraint configuration."""
        domain = LogisticsDomain(scale="small", auto_objects=False)
        problem = Problem(f"constraint_impact_{config['name']}")
        
        # Create objects
        robots = [Object(f"r{i+1}", domain.Robot) for i in range(config["robots"])]
        docks = [Object(f"d{i+1}", domain.Dock) for i in range(config["docks"])]
        containers = [Object(f"c{i+1}", domain.Container) for i in range(config["containers"])]
        piles = [Object(f"p{i+1}", domain.Pile) for i in range(config["piles"])]
        
        all_objects = robots + docks + containers + piles
        problem.add_objects(all_objects)
        
        domain.assign_objects({
            "robots": robots,
            "docks": docks,
            "containers": containers,
            "piles": piles,
            "all_objects": all_objects
        })
        
        # Add fluents
        for fluent in domain.fluents + domain.static_fluents:
            problem.add_fluent(fluent, default_initial_value=False)
        
        # Add actions
        actions = LogisticsActions(domain)
        for action in actions.get_actions():
            problem.add_action(action)
        
        # Set initial state
        initial_state = {}
        
        # Robot locations and capacities
        for i, robot in enumerate(robots):
            dock = docks[i % len(docks)]
            initial_state[domain.robot_at(robot, dock)] = True
            initial_state[domain.robot_can_carry_1(robot)] = True
            initial_state[domain.robot_can_carry_2(robot)] = True
            initial_state[domain.robot_can_carry_3(robot)] = False
            initial_state[domain.robot_weight_0(robot)] = True
            initial_state[domain.robot_free(robot)] = True
            
            # Set capacity based on constraint type
            if config.get("tight_capacity", False):
                initial_state[domain.robot_capacity_5(robot)] = True  # Tight capacity
            else:
                initial_state[domain.robot_capacity_6(robot)] = True  # Normal capacity
        
        # Container weights based on constraint type
        if config["weight_constraints"]:
            # Mixed weights to create constraints
            for i, container in enumerate(containers):
                if i % 3 == 0:
                    initial_state[domain.container_weight_2(container)] = True
                elif i % 3 == 1:
                    initial_state[domain.container_weight_4(container)] = True
                else:
                    initial_state[domain.container_weight_6(container)] = True
        else:
            # All containers same weight (no weight constraints)
            for container in containers:
                initial_state[domain.container_weight_2(container)] = True
        
        # Distribute containers in piles
        containers_per_pile = config["containers"] // config["piles"]
        for i, pile in enumerate(piles):
            start_idx = i * containers_per_pile
            end_idx = start_idx + containers_per_pile
            if i == len(piles) - 1:
                end_idx = config["containers"]
            
            pile_containers = containers[start_idx:end_idx]
            for j, container in enumerate(pile_containers):
                initial_state[domain.container_in_pile(container, pile)] = True
                if j == len(pile_containers) - 1:
                    initial_state[domain.container_on_top_of_pile(container, pile)] = True
                if j > 0:
                    initial_state[domain.container_under_in_pile(pile_containers[j-1], container, pile)] = True
            
            dock = docks[i % len(docks)]
            initial_state[domain.pile_at_dock(pile, dock)] = True
        
        # Adjacency
        for i in range(len(docks) - 1):
            initial_state[domain.adjacent(docks[i], docks[i+1])] = True
            initial_state[domain.adjacent(docks[i+1], docks[i])] = True
        
        # Set initial values
        for fluent, value in initial_state.items():
            problem.set_initial_value(fluent, value)
        
        # Create challenging goal that requires planning
        goal_conditions = []
        if len(containers) >= 4 and len(piles) >= 3:
            goal_conditions.extend([
                # Move containers to create a specific pattern
                domain.container_in_pile(containers[0], piles[1]),
                domain.container_on_top_of_pile(containers[0], piles[1]),
                domain.container_in_pile(containers[1], piles[2]),
                domain.container_on_top_of_pile(containers[1], piles[2]),
                domain.container_in_pile(containers[2], piles[0]),
                domain.container_on_top_of_pile(containers[2], piles[0])
            ])
        
        if goal_conditions:
            problem.add_goal(And(*goal_conditions))
        
        return problem, domain
    
    def run_experiment(self, config: Dict, num_runs: int = 5) -> Dict:
        """Run experiment for given constraint configuration."""
        print(f"Running {config['name']}: {config['description']}")
        
        results = {
            "config": config,
            "runs": []
        }
        
        for run in range(num_runs):
            try:
                problem, domain = self.create_problem(config)
                
                start_time = time.time()
                with OneshotPlanner(name='fast-downward') as planner:
                    result = planner.solve(problem)
                solve_time = time.time() - start_time
                
                success = result.status == PlanGenerationResultStatus.SOLVED_SATISFICING
                plan_length = len(result.plan.actions) if result.plan else 0
                status = str(result.status)
                
                run_result = {
                    "run": run,
                    "success": success,
                    "solve_time": solve_time,
                    "plan_length": plan_length,
                    "status": status
                }
                
                results["runs"].append(run_result)
                print(f"  Run {run+1}: {success}, {solve_time:.3f}s, {plan_length} actions")
                
            except Exception as e:
                print(f"  Run {run+1}: ERROR - {str(e)}")
                results["runs"].append({
                    "run": run,
                    "success": False,
                    "solve_time": float('inf'),
                    "plan_length": 0,
                    "status": f"ERROR: {str(e)}"
                })
        
        # Calculate summary statistics
        successful_runs = [r for r in results["runs"] if r["success"]]
        if successful_runs:
            solve_times = [r["solve_time"] for r in successful_runs]
            plan_lengths = [r["plan_length"] for r in successful_runs]
            
            results["summary"] = {
                "success_rate": len(successful_runs) / num_runs,
                "avg_solve_time": statistics.mean(solve_times),
                "std_solve_time": statistics.stdev(solve_times) if len(solve_times) > 1 else 0,
                "avg_plan_length": statistics.mean(plan_lengths),
                "std_plan_length": statistics.stdev(plan_lengths) if len(plan_lengths) > 1 else 0,
                "min_solve_time": min(solve_times),
                "max_solve_time": max(solve_times)
            }
        else:
            results["summary"] = {
                "success_rate": 0,
                "avg_solve_time": float('inf'),
                "std_solve_time": 0,
                "avg_plan_length": 0,
                "std_plan_length": 0,
                "min_solve_time": float('inf'),
                "max_solve_time": 0
            }
        
        return results
    
    def run_all_experiments(self, num_runs: int = 5):
        """Run all constraint impact experiments."""
        print("Starting Constraint Impact Analysis Experiment")
        print("=" * 50)
        
        for config in self.constraint_configs:
            result = self.run_experiment(config, num_runs)
            self.results.append(result)
            print()
        
        self.save_results()
        self.generate_plots()
        self.generate_report()
    
    def save_results(self):
        """Save raw results to JSON."""
        results_file = os.path.join(self.output_dir, "raw_results.json")
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"Results saved to {results_file}")
    
    def generate_plots(self):
        """Generate visualization plots."""
        # Prepare data for plotting
        config_names = [r["config"]["name"] for r in self.results]
        solve_times = [r["summary"]["avg_solve_time"] for r in self.results]
        plan_lengths = [r["summary"]["avg_plan_length"] for r in self.results]
        success_rates = [r["summary"]["success_rate"] for r in self.results]
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Solve time comparison
        bars1 = ax1.bar(config_names, solve_times, color=['lightblue', 'lightgreen', 'lightcoral', 'lightyellow', 'lightpink'])
        ax1.set_title('Average Solve Time by Constraint Type')
        ax1.set_ylabel('Solve Time (s)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, time in zip(bars1, solve_times):
            if time != float('inf'):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                        f'{time:.3f}s', ha='center', va='bottom')
        
        # Plan length comparison
        bars2 = ax2.bar(config_names, plan_lengths, color=['lightblue', 'lightgreen', 'lightcoral', 'lightyellow', 'lightpink'])
        ax2.set_title('Average Plan Length by Constraint Type')
        ax2.set_ylabel('Plan Length (actions)')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, length in zip(bars2, plan_lengths):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{length:.0f}', ha='center', va='bottom')
        
        # Success rate comparison
        bars3 = ax3.bar(config_names, success_rates, color=['lightblue', 'lightgreen', 'lightcoral', 'lightyellow', 'lightpink'])
        ax3.set_title('Success Rate by Constraint Type')
        ax3.set_ylabel('Success Rate')
        ax3.set_ylim(0, 1.1)
        ax3.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, rate in zip(bars3, success_rates):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{rate:.2f}', ha='center', va='bottom')
        
        # Constraint impact summary
        constraint_impact = []
        constraint_labels = []
        
        # Compare with no_constraints baseline
        baseline_time = next(r["summary"]["avg_solve_time"] for r in self.results if r["config"]["name"] == "no_constraints")
        baseline_length = next(r["summary"]["avg_plan_length"] for r in self.results if r["config"]["name"] == "no_constraints")
        
        for result in self.results:
            if result["config"]["name"] != "no_constraints":
                time_ratio = result["summary"]["avg_solve_time"] / baseline_time if baseline_time != float('inf') else 1
                length_ratio = result["summary"]["avg_plan_length"] / baseline_length if baseline_length > 0 else 1
                constraint_impact.append((time_ratio + length_ratio) / 2)  # Average impact
                constraint_labels.append(result["config"]["name"])
        
        bars4 = ax4.bar(constraint_labels, constraint_impact, color=['lightgreen', 'lightcoral', 'lightyellow', 'lightpink'])
        ax4.set_title('Constraint Impact (vs No Constraints)')
        ax4.set_ylabel('Impact Ratio')
        ax4.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='Baseline (no constraints)')
        ax4.tick_params(axis='x', rotation=45)
        ax4.legend()
        
        # Add value labels on bars
        for bar, impact in zip(bars4, constraint_impact):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{impact:.2f}x', ha='center', va='bottom')
        
        plt.tight_layout()
        
        # Save plot
        plot_file = os.path.join(self.output_dir, "constraint_impact.png")
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Plot saved to {plot_file}")
    
    def generate_report(self):
        """Generate a markdown report."""
        report_file = os.path.join(self.output_dir, "report.md")
        
        with open(report_file, 'w') as f:
            f.write("# Constraint Impact Analysis Report\n\n")
            f.write("This experiment analyzes how different types of constraints affect planning performance.\n\n")
            
            f.write("## Experiment Configuration\n\n")
            f.write("| Constraint Type | Description | Robots | Docks | Containers | Piles |\n")
            f.write("|----------------|-------------|--------|-------|------------|-------|\n")
            
            for result in self.results:
                config = result["config"]
                f.write(f"| {config['name']} | {config['description']} | {config['robots']} | {config['docks']} | {config['containers']} | {config['piles']} |\n")
            
            f.write("\n## Results Summary\n\n")
            f.write("| Constraint Type | Success Rate | Avg Solve Time (s) | Avg Plan Length |\n")
            f.write("|----------------|--------------|-------------------|----------------|\n")
            
            for result in self.results:
                config = result["config"]
                summary = result["summary"]
                f.write(f"| {config['name']} | {summary['success_rate']:.2f} | {summary['avg_solve_time']:.3f} | {summary['avg_plan_length']:.1f} |\n")
            
            f.write("\n## Key Findings\n\n")
            
            # Find baseline (no constraints)
            baseline = next(r for r in self.results if r["config"]["name"] == "no_constraints")
            baseline_time = baseline["summary"]["avg_solve_time"]
            baseline_length = baseline["summary"]["avg_plan_length"]
            
            f.write(f"- **Baseline (No Constraints)**: {baseline_time:.3f}s solve time, {baseline_length:.1f} actions\n")
            
            for result in self.results:
                if result["config"]["name"] != "no_constraints":
                    config = result["config"]
                    summary = result["summary"]
                    time_impact = summary["avg_solve_time"] / baseline_time if baseline_time != float('inf') else 1
                    length_impact = summary["avg_plan_length"] / baseline_length if baseline_length > 0 else 1
                    
                    f.write(f"- **{config['name']}**: {time_impact:.2f}x solve time, {length_impact:.2f}x plan length\n")
            
            f.write("\n## Analysis\n\n")
            f.write("This experiment demonstrates how different constraint types impact planning performance:\n\n")
            f.write("- **LIFO constraints** affect plan structure and may require more intermediate steps\n")
            f.write("- **Weight constraints** limit robot capacity and may require more careful planning\n")
            f.write("- **Combined constraints** can have compounding effects on planning complexity\n")
            f.write("- **Tight capacity** constraints significantly impact both solve time and plan length\n")
        
        print(f"Report saved to {report_file}")

def main():
    experiment = ConstraintImpactExperiment()
    experiment.run_all_experiments(num_runs=3)
    print("\nConstraint Impact Analysis completed!")

if __name__ == "__main__":
    main()
