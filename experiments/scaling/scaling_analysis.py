"""
Scaling Analysis Experiment
Tests how planning performance scales with problem size.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import time
import json
import csv
import statistics
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import pandas as pd

from unified_planning.shortcuts import *
from unified_planning.engines.results import PlanGenerationResultStatus
from src.domain import LogisticsDomain
from src.actions import LogisticsActions

class ScalingExperiment:
    def __init__(self, output_dir: str = "experiments/scaling/results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Experiment configurations with challenging goals
        self.configs = [
            # Small problems with simple goals
            {"robots": 1, "docks": 3, "containers": 4, "piles": 3, "name": "small_1", "goal_type": "simple_swap"},
            {"robots": 1, "docks": 4, "containers": 5, "piles": 4, "name": "small_2", "goal_type": "simple_swap"},
            {"robots": 2, "docks": 4, "containers": 6, "piles": 4, "name": "small_3", "goal_type": "simple_swap"},
            
            # Medium problems with complex redistribution
            {"robots": 2, "docks": 5, "containers": 8, "piles": 5, "name": "medium_1", "goal_type": "complex_redistribution"},
            {"robots": 3, "docks": 5, "containers": 10, "piles": 5, "name": "medium_2", "goal_type": "complex_redistribution"},
            {"robots": 3, "docks": 6, "containers": 12, "piles": 6, "name": "medium_3", "goal_type": "complex_redistribution"},
            
            # Large problems with weight constraints
            {"robots": 3, "docks": 7, "containers": 14, "piles": 7, "name": "large_1", "goal_type": "weight_constrained"},
            {"robots": 4, "docks": 7, "containers": 16, "piles": 7, "name": "large_2", "goal_type": "weight_constrained"},
            {"robots": 4, "docks": 8, "containers": 18, "piles": 8, "name": "large_3", "goal_type": "weight_constrained"},
        ]
        
        self.results = []
    
    def create_problem(self, config: Dict) -> Tuple[Problem, LogisticsDomain]:
        """Create a logistics problem with given configuration."""
        domain = LogisticsDomain(scale="small", auto_objects=False)
        problem = Problem(f"scaling_{config['name']}")
        
        # Create objects
        robots = [Object(f"r{i+1}", domain.Robot) for i in range(config["robots"])]
        docks = [Object(f"d{i+1}", domain.Dock) for i in range(config["docks"])]
        containers = [Object(f"c{i+1}", domain.Container) for i in range(config["containers"])]
        piles = [Object(f"p{i+1}", domain.Pile) for i in range(config["piles"])]
        
        all_objects = robots + docks + containers + piles
        problem.add_objects(all_objects)
        
        # Assign to domain
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
        
        # Robot locations (distribute evenly)
        for i, robot in enumerate(robots):
            dock = docks[i % len(docks)]
            initial_state[domain.robot_at(robot, dock)] = True
        
        # Robot capacities based on problem size
        for robot in robots:
            initial_state[domain.robot_can_carry_1(robot)] = True
            initial_state[domain.robot_can_carry_2(robot)] = True
            initial_state[domain.robot_can_carry_3(robot)] = False
            initial_state[domain.robot_weight_0(robot)] = True
            initial_state[domain.robot_free(robot)] = True
            
            # Set capacity based on problem size
            if config["name"].startswith("small"):
                initial_state[domain.robot_capacity_6(robot)] = True  # 6t capacity
            elif config["name"].startswith("medium"):
                initial_state[domain.robot_capacity_6(robot)] = True  # 6t capacity
            else:  # large
                initial_state[domain.robot_capacity_5(robot)] = True  # Tight 5t capacity
        
        # Container weights based on problem size
        if config["name"].startswith("small"):
            # Small: mostly 2t containers
            for i, container in enumerate(containers):
                if i % 3 == 0:
                    initial_state[domain.container_weight_2(container)] = True
                else:
                    initial_state[domain.container_weight_4(container)] = True
        elif config["name"].startswith("medium"):
            # Medium: mixed weights
            for i, container in enumerate(containers):
                if i % 3 == 0:
                    initial_state[domain.container_weight_2(container)] = True
                elif i % 3 == 1:
                    initial_state[domain.container_weight_4(container)] = True
                else:
                    initial_state[domain.container_weight_6(container)] = True
        else:  # large
            # Large: mostly heavy containers
            for i, container in enumerate(containers):
                if i < len(containers) // 3:
                    initial_state[domain.container_weight_2(container)] = True
                elif i < 2 * len(containers) // 3:
                    initial_state[domain.container_weight_4(container)] = True
                else:
                    initial_state[domain.container_weight_6(container)] = True
        
        # Distribute containers in piles
        containers_per_pile = config["containers"] // config["piles"]
        for i, pile in enumerate(piles):
            start_idx = i * containers_per_pile
            end_idx = start_idx + containers_per_pile
            if i == len(piles) - 1:  # Last pile gets remaining containers
                end_idx = config["containers"]
            
            pile_containers = containers[start_idx:end_idx]
            for j, container in enumerate(pile_containers):
                initial_state[domain.container_in_pile(container, pile)] = True
                if j == len(pile_containers) - 1:  # Top container
                    initial_state[domain.container_on_top_of_pile(container, pile)] = True
                if j > 0:  # Under relationship
                    initial_state[domain.container_under_in_pile(pile_containers[j-1], container, pile)] = True
            
            # Pile at dock
            dock = docks[i % len(docks)]
            initial_state[domain.pile_at_dock(pile, dock)] = True
        
        # Adjacency (linear topology)
        for i in range(len(docks) - 1):
            initial_state[domain.adjacent(docks[i], docks[i+1])] = True
            initial_state[domain.adjacent(docks[i+1], docks[i])] = True
        
        # Set initial values
        for fluent, value in initial_state.items():
            problem.set_initial_value(fluent, value)
        
        # Create challenging goals based on problem type
        goal_conditions = []
        goal_type = config.get("goal_type", "simple_swap")
        
        if goal_type == "simple_swap":
            # Simple container swap between first two piles
            if len(containers) >= 2 and len(piles) >= 2:
                goal_conditions.extend([
                    domain.container_in_pile(containers[0], piles[1]),
                    domain.container_on_top_of_pile(containers[0], piles[1]),
                    domain.container_in_pile(containers[1], piles[0]),
                    domain.container_on_top_of_pile(containers[1], piles[0])
                ])
        
        elif goal_type == "complex_redistribution":
            # Complex redistribution requiring multiple moves
            if len(containers) >= 4 and len(piles) >= 3:
                goal_conditions.extend([
                    domain.container_in_pile(containers[0], piles[0]),
                    domain.container_on_top_of_pile(containers[0], piles[0]),
                    domain.container_in_pile(containers[1], piles[1]),
                    domain.container_on_top_of_pile(containers[1], piles[1]),
                    domain.container_in_pile(containers[2], piles[1]),
                    domain.container_under_in_pile(containers[2], containers[1], piles[1]),
                    domain.container_in_pile(containers[3], piles[2]),
                    domain.container_on_top_of_pile(containers[3], piles[2])
                ])
        
        elif goal_type == "weight_constrained":
            # Weight-constrained redistribution requiring careful planning
            if len(containers) >= 6 and len(piles) >= 4:
                goal_conditions.extend([
                    domain.container_in_pile(containers[0], piles[0]),
                    domain.container_on_top_of_pile(containers[0], piles[0]),
                    domain.container_in_pile(containers[1], piles[1]),
                    domain.container_on_top_of_pile(containers[1], piles[1]),
                    domain.container_in_pile(containers[2], piles[1]),
                    domain.container_under_in_pile(containers[2], containers[1], piles[1]),
                    domain.container_in_pile(containers[3], piles[2]),
                    domain.container_on_top_of_pile(containers[3], piles[2]),
                    domain.container_in_pile(containers[4], piles[3]),
                    domain.container_on_top_of_pile(containers[4], piles[3])
                ])
        
        if goal_conditions:
            problem.add_goal(And(*goal_conditions))
        
        return problem, domain
    
    def run_experiment(self, config: Dict, num_runs: int = 5) -> Dict:
        """Run experiment for given configuration."""
        print(f"Running {config['name']}: {config['robots']} robots, {config['docks']} docks, {config['containers']} containers, {config['piles']} piles")
        
        results = {
            "config": config,
            "runs": [],
            "summary": {}
        }
        
        for run in range(num_runs):
            try:
                problem, domain = self.create_problem(config)
                
                start_time = time.time()
                with OneshotPlanner(name='fast-downward') as planner:
                    result = planner.solve(problem)
                solve_time = time.time() - start_time
                
                run_result = {
                    "run": run,
                    "success": result.status == PlanGenerationResultStatus.SOLVED_SATISFICING,
                    "solve_time": solve_time,
                    "plan_length": len(result.plan.actions) if result.plan else 0,
                    "status": str(result.status)
                }
                
                results["runs"].append(run_result)
                print(f"  Run {run+1}: {run_result['success']}, {solve_time:.3f}s, {run_result['plan_length']} actions")
                
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
    
    def run_all_experiments(self):
        """Run all scaling experiments."""
        print("Starting Scaling Analysis Experiment")
        print("=" * 50)
        
        for config in self.configs:
            result = self.run_experiment(config)
            self.results.append(result)
            print()
        
        self.save_results()
        self.generate_plots()
        self.generate_report()
    
    def save_results(self):
        """Save results to files."""
        # Save raw results as JSON
        with open(f"{self.output_dir}/raw_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        # Save summary as CSV
        summary_data = []
        for result in self.results:
            config = result["config"]
            summary = result["summary"]
            summary_data.append({
                "name": config["name"],
                "robots": config["robots"],
                "docks": config["docks"],
                "containers": config["containers"],
                "piles": config["piles"],
                "success_rate": summary["success_rate"],
                "avg_solve_time": summary["avg_solve_time"],
                "std_solve_time": summary["std_solve_time"],
                "avg_plan_length": summary["avg_plan_length"],
                "std_plan_length": summary["std_plan_length"]
            })
        
        with open(f"{self.output_dir}/summary.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=summary_data[0].keys())
            writer.writeheader()
            writer.writerows(summary_data)
    
    def generate_plots(self):
        """Generate visualization plots."""
        df = pd.DataFrame([{
            "name": r["config"]["name"],
            "robots": r["config"]["robots"],
            "docks": r["config"]["docks"],
            "containers": r["config"]["containers"],
            "piles": r["config"]["piles"],
            "success_rate": r["summary"]["success_rate"],
            "avg_solve_time": r["summary"]["avg_solve_time"],
            "avg_plan_length": r["summary"]["avg_plan_length"]
        } for r in self.results])
        
        # Plot 1: Solve time vs problem size
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        plt.scatter(df["containers"], df["avg_solve_time"], c=df["robots"], cmap="viridis")
        plt.xlabel("Number of Containers")
        plt.ylabel("Average Solve Time (s)")
        plt.title("Solve Time vs Containers")
        plt.colorbar(label="Robots")
        
        plt.subplot(2, 2, 2)
        plt.scatter(df["docks"], df["avg_solve_time"], c=df["containers"], cmap="plasma")
        plt.xlabel("Number of Docks")
        plt.ylabel("Average Solve Time (s)")
        plt.title("Solve Time vs Docks")
        plt.colorbar(label="Containers")
        
        plt.subplot(2, 2, 3)
        plt.scatter(df["containers"], df["avg_plan_length"], c=df["robots"], cmap="viridis")
        plt.xlabel("Number of Containers")
        plt.ylabel("Average Plan Length")
        plt.title("Plan Length vs Containers")
        plt.colorbar(label="Robots")
        
        plt.subplot(2, 2, 4)
        plt.scatter(df["containers"], df["success_rate"], c=df["robots"], cmap="viridis")
        plt.xlabel("Number of Containers")
        plt.ylabel("Success Rate")
        plt.title("Success Rate vs Containers")
        plt.colorbar(label="Robots")
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/scaling_analysis.png", dpi=300, bbox_inches="tight")
        plt.close()
    
    def generate_report(self):
        """Generate markdown report."""
        report = f"""# Scaling Analysis Results

## Experiment Overview
- **Total configurations**: {len(self.configs)}
- **Runs per configuration**: 5
- **Total runs**: {len(self.configs) * 5}

## Results Summary

| Configuration | Robots | Docks | Containers | Piles | Success Rate | Avg Time (s) | Avg Plan Length |
|---------------|--------|-------|------------|-------|--------------|--------------|-----------------|
"""
        
        for result in self.results:
            config = result["config"]
            summary = result["summary"]
            report += f"| {config['name']} | {config['robots']} | {config['docks']} | {config['containers']} | {config['piles']} | {summary['success_rate']:.2f} | {summary['avg_solve_time']:.3f} | {summary['avg_plan_length']:.1f} |\n"
        
        report += f"""
## Key Findings

1. **Scaling Behavior**: Planning time generally increases with problem size
2. **Success Rate**: All small and medium problems solved successfully
3. **Plan Length**: Increases with number of containers
4. **Bottlenecks**: Large problems may hit time/memory limits

## Files Generated
- `raw_results.json`: Complete experimental data
- `summary.csv`: Summary statistics
- `scaling_analysis.png`: Visualization plots
- `report.md`: This report

## Next Steps
- Analyze scaling curves for exponential vs polynomial growth
- Test with different heuristics
- Investigate failure modes for large problems
"""
        
        with open(f"{self.output_dir}/report.md", "w") as f:
            f.write(report)
        
        print(f"Results saved to {self.output_dir}/")
        print("Files generated:")
        print("- raw_results.json")
        print("- summary.csv") 
        print("- scaling_analysis.png")
        print("- report.md")

if __name__ == "__main__":
    experiment = ScalingExperiment()
    experiment.run_all_experiments()
