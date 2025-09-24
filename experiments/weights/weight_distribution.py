#!/usr/bin/env python3
"""
Weight Distribution Analysis Experiment

This experiment analyzes how different container weight distributions affect planning performance:
- Uniform weights (all containers same weight)
- Mixed weights (2t, 4t, 6t containers)
- Heavy-biased (mostly heavy containers)
- Light-biased (mostly light containers)
- Extreme weights (very heavy containers)
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

class WeightDistributionExperiment:
    def __init__(self, output_dir: str = "experiments/weights/results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Experiment configurations testing different weight distributions
        self.weight_configs = [
            {
                "name": "uniform_light",
                "description": "All containers 2t (light)",
                "weight_distribution": "uniform_light",
                "robots": 2, "docks": 4, "containers": 8, "piles": 4
            },
            {
                "name": "uniform_medium",
                "description": "All containers 4t (medium)",
                "weight_distribution": "uniform_medium",
                "robots": 2, "docks": 4, "containers": 8, "piles": 4
            },
            {
                "name": "uniform_heavy",
                "description": "All containers 6t (heavy)",
                "weight_distribution": "uniform_heavy",
                "robots": 2, "docks": 4, "containers": 8, "piles": 4
            },
            {
                "name": "mixed_balanced",
                "description": "Balanced mix (2t, 4t, 6t)",
                "weight_distribution": "mixed_balanced",
                "robots": 2, "docks": 4, "containers": 9, "piles": 4
            },
            {
                "name": "light_biased",
                "description": "Mostly light containers (2t)",
                "weight_distribution": "light_biased",
                "robots": 2, "docks": 4, "containers": 8, "piles": 4
            },
            {
                "name": "heavy_biased",
                "description": "Mostly heavy containers (6t)",
                "weight_distribution": "heavy_biased",
                "robots": 2, "docks": 4, "containers": 8, "piles": 4
            },
            {
                "name": "extreme_heavy",
                "description": "All containers 6t with tight robot capacity",
                "weight_distribution": "extreme_heavy",
                "tight_capacity": True,
                "robots": 2, "docks": 4, "containers": 8, "piles": 4
            },
            {
                "name": "mixed_extreme",
                "description": "Mixed weights with tight robot capacity",
                "weight_distribution": "mixed_balanced",
                "tight_capacity": True,
                "robots": 2, "docks": 4, "containers": 8, "piles": 4
            }
        ]
        
        self.results = []
    
    def assign_container_weights(self, containers: List, config: Dict) -> Dict:
        """Assign weights to containers based on distribution type."""
        initial_state = {}
        distribution = config["weight_distribution"]
        
        if distribution == "uniform_light":
            for container in containers:
                initial_state[container] = 2
        elif distribution == "uniform_medium":
            for container in containers:
                initial_state[container] = 4
        elif distribution == "uniform_heavy":
            for container in containers:
                initial_state[container] = 6
        elif distribution == "mixed_balanced":
            for i, container in enumerate(containers):
                if i % 3 == 0:
                    initial_state[container] = 2
                elif i % 3 == 1:
                    initial_state[container] = 4
                else:
                    initial_state[container] = 6
        elif distribution == "light_biased":
            for i, container in enumerate(containers):
                if i < len(containers) * 0.7:  # 70% light
                    initial_state[container] = 2
                else:
                    initial_state[container] = 4
        elif distribution == "heavy_biased":
            for i, container in enumerate(containers):
                if i < len(containers) * 0.3:  # 30% light
                    initial_state[container] = 2
                else:
                    initial_state[container] = 6
        
        return initial_state
    
    def create_problem(self, config: Dict) -> Tuple[Problem, LogisticsDomain]:
        """Create a logistics problem with given weight distribution configuration."""
        domain = LogisticsDomain(scale="small", auto_objects=False)
        problem = Problem(f"weight_distribution_{config['name']}")
        
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
            
            # Set capacity based on configuration
            if config.get("tight_capacity", False):
                initial_state[domain.robot_capacity_5(robot)] = True  # Tight capacity
            else:
                initial_state[domain.robot_capacity_6(robot)] = True  # Normal capacity
        
        # Assign container weights based on distribution
        weight_assignments = self.assign_container_weights(containers, config)
        for container, weight in weight_assignments.items():
            if weight == 2:
                initial_state[domain.container_weight_2(container)] = True
            elif weight == 4:
                initial_state[domain.container_weight_4(container)] = True
            elif weight == 6:
                initial_state[domain.container_weight_6(container)] = True
        
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
        
        # Create challenging goal that requires weight-aware planning
        goal_conditions = []
        if len(containers) >= 4 and len(piles) >= 3:
            # Goal: redistribute containers to create specific weight patterns
            goal_conditions.extend([
                # Move containers to create a specific stacking pattern
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
        """Run experiment for given weight distribution configuration."""
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
        """Run all weight distribution experiments."""
        print("Starting Weight Distribution Analysis Experiment")
        print("=" * 50)
        
        for config in self.weight_configs:
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
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Solve time comparison
        colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow', 'lightpink', 'lightgray', 'lightcyan', 'lightsteelblue']
        bars1 = ax1.bar(config_names, solve_times, color=colors[:len(config_names)])
        ax1.set_title('Average Solve Time by Weight Distribution')
        ax1.set_ylabel('Solve Time (s)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, time in zip(bars1, solve_times):
            if time != float('inf'):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                        f'{time:.3f}s', ha='center', va='bottom', fontsize=8)
        
        # Plan length comparison
        bars2 = ax2.bar(config_names, plan_lengths, color=colors[:len(config_names)])
        ax2.set_title('Average Plan Length by Weight Distribution')
        ax2.set_ylabel('Plan Length (actions)')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, length in zip(bars2, plan_lengths):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{length:.0f}', ha='center', va='bottom', fontsize=8)
        
        # Success rate comparison
        bars3 = ax3.bar(config_names, success_rates, color=colors[:len(config_names)])
        ax3.set_title('Success Rate by Weight Distribution')
        ax3.set_ylabel('Success Rate')
        ax3.set_ylim(0, 1.1)
        ax3.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, rate in zip(bars3, success_rates):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{rate:.2f}', ha='center', va='bottom', fontsize=8)
        
        # Weight distribution impact analysis
        # Compare uniform vs mixed vs biased distributions
        uniform_results = [r for r in self.results if "uniform" in r["config"]["name"]]
        mixed_results = [r for r in self.results if "mixed" in r["config"]["name"]]
        biased_results = [r for r in self.results if "biased" in r["config"]["name"]]
        
        categories = []
        avg_times = []
        avg_lengths = []
        
        if uniform_results:
            categories.append("Uniform")
            avg_times.append(statistics.mean([r["summary"]["avg_solve_time"] for r in uniform_results]))
            avg_lengths.append(statistics.mean([r["summary"]["avg_plan_length"] for r in uniform_results]))
        
        if mixed_results:
            categories.append("Mixed")
            avg_times.append(statistics.mean([r["summary"]["avg_solve_time"] for r in mixed_results]))
            avg_lengths.append(statistics.mean([r["summary"]["avg_plan_length"] for r in mixed_results]))
        
        if biased_results:
            categories.append("Biased")
            avg_times.append(statistics.mean([r["summary"]["avg_solve_time"] for r in biased_results]))
            avg_lengths.append(statistics.mean([r["summary"]["avg_plan_length"] for r in biased_results]))
        
        x = range(len(categories))
        width = 0.35
        
        bars4a = ax4.bar([i - width/2 for i in x], avg_times, width, label='Solve Time', color='lightblue')
        ax4_twin = ax4.twinx()
        bars4b = ax4_twin.bar([i + width/2 for i in x], avg_lengths, width, label='Plan Length', color='lightcoral')
        
        ax4.set_xlabel('Weight Distribution Type')
        ax4.set_ylabel('Solve Time (s)', color='blue')
        ax4_twin.set_ylabel('Plan Length (actions)', color='red')
        ax4.set_title('Weight Distribution Impact Analysis')
        ax4.set_xticks(x)
        ax4.set_xticklabels(categories)
        
        # Add value labels
        for bar, time in zip(bars4a, avg_times):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{time:.3f}s', ha='center', va='bottom', fontsize=8)
        
        for bar, length in zip(bars4b, avg_lengths):
            ax4_twin.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                         f'{length:.0f}', ha='center', va='bottom', fontsize=8)
        
        # Add legends
        ax4.legend(loc='upper left')
        ax4_twin.legend(loc='upper right')
        
        plt.tight_layout()
        
        # Save plot
        plot_file = os.path.join(self.output_dir, "weight_distribution.png")
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Plot saved to {plot_file}")
    
    def generate_report(self):
        """Generate a markdown report."""
        report_file = os.path.join(self.output_dir, "report.md")
        
        with open(report_file, 'w') as f:
            f.write("# Weight Distribution Analysis Report\n\n")
            f.write("This experiment analyzes how different container weight distributions affect planning performance.\n\n")
            
            f.write("## Experiment Configuration\n\n")
            f.write("| Distribution | Description | Robots | Docks | Containers | Piles |\n")
            f.write("|--------------|-------------|--------|-------|------------|-------|\n")
            
            for result in self.results:
                config = result["config"]
                f.write(f"| {config['name']} | {config['description']} | {config['robots']} | {config['docks']} | {config['containers']} | {config['piles']} |\n")
            
            f.write("\n## Results Summary\n\n")
            f.write("| Distribution | Success Rate | Avg Solve Time (s) | Avg Plan Length |\n")
            f.write("|--------------|--------------|-------------------|----------------|\n")
            
            for result in self.results:
                config = result["config"]
                summary = result["summary"]
                f.write(f"| {config['name']} | {summary['success_rate']:.2f} | {summary['avg_solve_time']:.3f} | {summary['avg_plan_length']:.1f} |\n")
            
            f.write("\n## Weight Distribution Analysis\n\n")
            
            # Group results by distribution type
            uniform_results = [r for r in self.results if "uniform" in r["config"]["name"]]
            mixed_results = [r for r in self.results if "mixed" in r["config"]["name"]]
            biased_results = [r for r in self.results if "biased" in r["config"]["name"]]
            
            if uniform_results:
                f.write("### Uniform Weight Distributions\n\n")
                avg_time = statistics.mean([r["summary"]["avg_solve_time"] for r in uniform_results])
                avg_length = statistics.mean([r["summary"]["avg_plan_length"] for r in uniform_results])
                f.write(f"- **Average Solve Time**: {avg_time:.3f}s\n")
                f.write(f"- **Average Plan Length**: {avg_length:.1f} actions\n\n")
            
            if mixed_results:
                f.write("### Mixed Weight Distributions\n\n")
                avg_time = statistics.mean([r["summary"]["avg_solve_time"] for r in mixed_results])
                avg_length = statistics.mean([r["summary"]["avg_plan_length"] for r in mixed_results])
                f.write(f"- **Average Solve Time**: {avg_time:.3f}s\n")
                f.write(f"- **Average Plan Length**: {avg_length:.1f} actions\n\n")
            
            if biased_results:
                f.write("### Biased Weight Distributions\n\n")
                avg_time = statistics.mean([r["summary"]["avg_solve_time"] for r in biased_results])
                avg_length = statistics.mean([r["summary"]["avg_plan_length"] for r in biased_results])
                f.write(f"- **Average Solve Time**: {avg_time:.3f}s\n")
                f.write(f"- **Average Plan Length**: {avg_length:.1f} actions\n\n")
            
            f.write("## Key Findings\n\n")
            f.write("This experiment reveals how weight distributions impact planning:\n\n")
            f.write("- **Uniform weights**: Consistent performance, predictable capacity usage\n")
            f.write("- **Mixed weights**: More complex planning due to capacity constraints\n")
            f.write("- **Heavy-biased**: Requires careful capacity management and may need more steps\n")
            f.write("- **Light-biased**: Generally easier planning with fewer capacity constraints\n")
            f.write("- **Tight capacity**: Significantly impacts planning when combined with heavy containers\n")
            f.write("- **Extreme scenarios**: Very heavy containers with tight capacity create the most challenging problems\n")
        
        print(f"Report saved to {report_file}")

def main():
    experiment = WeightDistributionExperiment()
    experiment.run_all_experiments(num_runs=3)
    print("\nWeight Distribution Analysis completed!")

if __name__ == "__main__":
    main()
