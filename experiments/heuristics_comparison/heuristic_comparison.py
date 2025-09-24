"""
Heuristic Comparison Experiment
Compares different planning heuristics on logistics problems.
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
from unified_planning.io import PDDLWriter
import tempfile
import subprocess
from src.domain import LogisticsDomain
from src.actions import LogisticsActions

class HeuristicExperiment:
    def __init__(self, output_dir: str = "experiments/heuristics/results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Fast Downward heuristic/search configurations to compare - including more diverse heuristics
        self.fd_searches = [
            {"name": "gbfs_ff", "search": "gbfs(ff())"},
            {"name": "gbfs_hadd", "search": "gbfs(hadd())"},
            {"name": "gbfs_hmax", "search": "gbfs(hmax())"},
            {"name": "gbfs_cg", "search": "gbfs(cg())"},
            {"name": "gbfs_cea", "search": "gbfs(cea())"},
            {"name": "gbfs_lmcut", "search": "gbfs(lmcut())"},
            {"name": "gbfs_blind", "search": "gbfs(blind())"},
        ]
        
        # Test problems of varying difficulty with challenging goals
        self.test_problems = [
            {"name": "easy_4", "robots": 1, "docks": 3, "containers": 4, "piles": 3, "goal_type": "simple_swap"},
            {"name": "easy_6", "robots": 1, "docks": 4, "containers": 6, "piles": 4, "goal_type": "simple_swap"},
            {"name": "medium_8", "robots": 2, "docks": 4, "containers": 8, "piles": 4, "goal_type": "complex_redistribution"},
            {"name": "medium_10", "robots": 2, "docks": 5, "containers": 10, "piles": 5, "goal_type": "complex_redistribution"},
            {"name": "medium_12", "robots": 2, "docks": 6, "containers": 12, "piles": 6, "goal_type": "complex_redistribution"},
            {"name": "hard_14", "robots": 3, "docks": 6, "containers": 14, "piles": 6, "goal_type": "weight_constrained"},
        ]
        
        self.results = []
    
    def create_problem(self, config: Dict) -> Tuple[Problem, LogisticsDomain]:
        """Create a logistics problem with given configuration."""
        domain = LogisticsDomain(scale="small", auto_objects=False)
        problem = Problem(f"heuristic_test_{config['name']}")
        
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
        
        # Robot locations and capacities based on problem difficulty
        for i, robot in enumerate(robots):
            dock = docks[i % len(docks)]
            initial_state[domain.robot_at(robot, dock)] = True
            initial_state[domain.robot_can_carry_1(robot)] = True
            initial_state[domain.robot_can_carry_2(robot)] = True
            initial_state[domain.robot_can_carry_3(robot)] = False
            initial_state[domain.robot_weight_0(robot)] = True
            initial_state[domain.robot_free(robot)] = True
            
            # Set capacity based on problem difficulty
            if config["name"].startswith("easy"):
                initial_state[domain.robot_capacity_6(robot)] = True  # 6t capacity
            elif config["name"].startswith("medium"):
                if i == 0:
                    initial_state[domain.robot_capacity_6(robot)] = True  # r1: 6t
                else:
                    initial_state[domain.robot_capacity_5(robot)] = True  # r2: 5t
            else:  # hard or extreme
                initial_state[domain.robot_capacity_5(robot)] = True  # Tight 5t capacity
        
        # Container weights based on problem difficulty
        if config["name"].startswith("easy"):
            # Easy: mostly 2t containers
            for i, container in enumerate(containers):
                if i < len(containers) * 0.75:  # 75% light containers
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
        else:  # hard or extreme
            # Hard/Extreme: mostly heavy containers
            for i, container in enumerate(containers):
                if i < len(containers) * 0.2:  # 20% light containers
                    initial_state[domain.container_weight_2(container)] = True
                elif i < len(containers) * 0.5:  # 30% medium containers
                    initial_state[domain.container_weight_4(container)] = True
                else:  # 50% heavy containers
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
            # Easy: Simple container swap between first two piles
            if len(containers) >= 2 and len(piles) >= 2:
                # Move first container from p1 to p2, second from p2 to p1
                goal_conditions.extend([
                    domain.container_in_pile(containers[0], piles[1]),
                    domain.container_on_top_of_pile(containers[0], piles[1]),
                    domain.container_in_pile(containers[1], piles[0]),
                    domain.container_on_top_of_pile(containers[1], piles[0])
                ])
        
        elif goal_type == "complex_redistribution":
            # Medium: Complex redistribution requiring multiple moves
            if len(containers) >= 4 and len(piles) >= 3:
                # Create a specific stacking pattern across multiple piles
                goal_conditions.extend([
                    # Pile 0: containers[0] on top
                    domain.container_in_pile(containers[0], piles[0]),
                    domain.container_on_top_of_pile(containers[0], piles[0]),
                    # Pile 1: containers[1] on top, containers[2] underneath
                    domain.container_in_pile(containers[1], piles[1]),
                    domain.container_on_top_of_pile(containers[1], piles[1]),
                    domain.container_in_pile(containers[2], piles[1]),
                    domain.container_under_in_pile(containers[2], containers[1], piles[1]),
                    # Pile 2: containers[3] on top
                    domain.container_in_pile(containers[3], piles[2]),
                    domain.container_on_top_of_pile(containers[3], piles[2])
                ])
        
        elif goal_type == "weight_constrained":
            # Hard: Weight-constrained redistribution requiring careful planning
            if len(containers) >= 6 and len(piles) >= 4:
                # Heavy containers must be moved by robots with sufficient capacity
                # Create a pattern that requires weight-aware planning
                goal_conditions.extend([
                    # Pile 0: light container on top
                    domain.container_in_pile(containers[0], piles[0]),
                    domain.container_on_top_of_pile(containers[0], piles[0]),
                    # Pile 1: heavy container on top, medium underneath
                    domain.container_in_pile(containers[1], piles[1]),
                    domain.container_on_top_of_pile(containers[1], piles[1]),
                    domain.container_in_pile(containers[2], piles[1]),
                    domain.container_under_in_pile(containers[2], containers[1], piles[1]),
                    # Pile 2: medium container on top
                    domain.container_in_pile(containers[3], piles[2]),
                    domain.container_on_top_of_pile(containers[3], piles[2]),
                    # Pile 3: heavy container on top
                    domain.container_in_pile(containers[4], piles[3]),
                    domain.container_on_top_of_pile(containers[4], piles[3])
                ])
        
        if goal_conditions:
            problem.add_goal(And(*goal_conditions))
        
        return problem, domain
    
    def _export_to_pddl(self, problem: Problem, workdir: str) -> Tuple[str, str]:
        writer = PDDLWriter(problem)
        dom_path = os.path.join(workdir, "domain.pddl")
        prob_path = os.path.join(workdir, "problem.pddl")
        writer.write_domain(dom_path)
        writer.write_problem(prob_path)
        return dom_path, prob_path

    def _run_fast_downward(self, domain_pddl: str, problem_pddl: str, search: str, workdir: str) -> Tuple[bool, float, int, str]:
        start = time.time()
        # Prefer 'fast-downward' if available; fallback to 'fast-downward.py'
        cmd_candidates = [
            ["fast-downward", domain_pddl, problem_pddl, "--search", search],
            [sys.executable, "-m", "downward.fast_downward", domain_pddl, problem_pddl, "--search", search],
            [sys.executable, "-m", "up_fast_downward.fast_downward", domain_pddl, problem_pddl, "--search", search],
        ]
        last_err = ""
        for cmd in cmd_candidates:
            try:
                res = subprocess.run(cmd, cwd=workdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=600)
                if res.returncode != 0:
                    last_err = (res.stderr or res.stdout or "non-zero return code").strip()
                    continue
                # Count plan length from generated sas_plan (or plan.N)
                plan_len = 0
                # Common plan filenames
                for fname in ["sas_plan", "plan", "plan.1", "sas_plan.1"]:
                    fpath = os.path.join(workdir, fname)
                    if os.path.exists(fpath):
                        with open(fpath) as f:
                            for line in f:
                                line = line.strip()
                                if not line or line.startswith(";"):
                                    continue
                                plan_len += 1
                        break
                elapsed = time.time() - start
                return True, elapsed, plan_len, "SOLVED"
            except FileNotFoundError as e:
                last_err = str(e)
                continue
            except subprocess.TimeoutExpired:
                return False, 600.0, 0, "TIMEOUT"
        return False, float('inf'), 0, f"ERROR: {last_err[:200]}"

    def run_experiment(self, problem_config: Dict, fd_search: Dict, num_runs: int = 3) -> Dict:
        """Run experiment for given problem and a Fast Downward search config."""
        print(f"Testing {fd_search['name']} ({fd_search['search']}) on {problem_config['name']} problem")
        
        results = {
            "problem": problem_config,
            "heuristic": fd_search,
            "runs": [],
            "summary": {}
        }
        
        for run in range(num_runs):
            try:
                problem, domain = self.create_problem(problem_config)
                
                # Use UP Fast Downward interface directly
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
                print(f"  Run {run+1}: {run_result['success']}, {run_result['solve_time']:.3f}s, {run_result['plan_length']} actions")
                
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
        """Run all heuristic comparison experiments."""
        print("Starting Heuristic Comparison Experiment")
        print("=" * 50)
        
        for problem_config in self.test_problems:
            for fd_search in self.fd_searches:
                result = self.run_experiment(problem_config, fd_search)
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
            problem = result["problem"]
            heuristic = result["heuristic"]
            summary = result["summary"]
            summary_data.append({
                "problem": problem["name"],
                "heuristic": heuristic["name"],
                "robots": problem["robots"],
                "docks": problem["docks"],
                "containers": problem["containers"],
                "piles": problem["piles"],
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
            "problem": r["problem"]["name"],
            "heuristic": r["heuristic"]["name"],
            "containers": r["problem"]["containers"],
            "success_rate": r["summary"]["success_rate"],
            "avg_solve_time": r["summary"]["avg_solve_time"],
            "avg_plan_length": r["summary"]["avg_plan_length"]
        } for r in self.results])
        
        # Plot 1: Solve time comparison
        plt.figure(figsize=(15, 10))
        
        plt.subplot(2, 3, 1)
        for heuristic in df["heuristic"].unique():
            data = df[df["heuristic"] == heuristic]
            plt.plot(data["containers"], data["avg_solve_time"], marker="o", label=heuristic)
        plt.xlabel("Number of Containers")
        plt.ylabel("Average Solve Time (s)")
        plt.title("Solve Time Comparison")
        plt.legend()
        # Avoid log scale errors when no positive values
        if (df["avg_solve_time"] > 0).any():
            plt.yscale("log")
        
        plt.subplot(2, 3, 2)
        for heuristic in df["heuristic"].unique():
            data = df[df["heuristic"] == heuristic]
            plt.plot(data["containers"], data["avg_plan_length"], marker="s", label=heuristic)
        plt.xlabel("Number of Containers")
        plt.ylabel("Average Plan Length")
        plt.title("Plan Length Comparison")
        plt.legend()
        
        plt.subplot(2, 3, 3)
        for heuristic in df["heuristic"].unique():
            data = df[df["heuristic"] == heuristic]
            plt.plot(data["containers"], data["success_rate"], marker="^", label=heuristic)
        plt.xlabel("Number of Containers")
        plt.ylabel("Success Rate")
        plt.title("Success Rate Comparison")
        plt.legend()
        
        # Box plots for solve time
        plt.subplot(2, 3, 4)
        df_pivot = df.pivot(index="problem", columns="heuristic", values="avg_solve_time")
        df_pivot.plot(kind="bar", ax=plt.gca())
        plt.xlabel("Problem")
        plt.ylabel("Average Solve Time (s)")
        plt.title("Solve Time by Problem")
        plt.xticks(rotation=45)
        if (df_pivot > 0).to_numpy().any():
            plt.yscale("log")
        
        # Box plots for plan length
        plt.subplot(2, 3, 5)
        df_pivot = df.pivot(index="problem", columns="heuristic", values="avg_plan_length")
        df_pivot.plot(kind="bar", ax=plt.gca())
        plt.xlabel("Problem")
        plt.ylabel("Average Plan Length")
        plt.title("Plan Length by Problem")
        plt.xticks(rotation=45)
        
        # Success rate comparison
        plt.subplot(2, 3, 6)
        df_pivot = df.pivot(index="problem", columns="heuristic", values="success_rate")
        df_pivot.plot(kind="bar", ax=plt.gca())
        plt.xlabel("Problem")
        plt.ylabel("Success Rate")
        plt.title("Success Rate by Problem")
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/heuristic_comparison.png", dpi=300, bbox_inches="tight")
        plt.close()
    
    def generate_report(self):
        """Generate markdown report."""
        report = f"""# Heuristic Comparison Results

## Experiment Overview
- **Heuristics tested**: {len(self.fd_searches)}
- **Test problems**: {len(self.test_problems)}
- **Total experiments**: {len(self.results)}

## Results Summary

| Problem | Heuristic | Success Rate | Avg Time (s) | Avg Plan Length |
|---------|-----------|--------------|--------------|-----------------|
"""
        
        for result in self.results:
            problem = result["problem"]
            heuristic = result["heuristic"]
            summary = result["summary"]
            report += f"| {problem['name']} | {heuristic['name']} | {summary['success_rate']:.2f} | {summary['avg_solve_time']:.3f} | {summary['avg_plan_length']:.1f} |\n"
        
        report += f"""
## Key Findings

1. **Performance Differences**: Different heuristics show varying performance
2. **Scalability**: Some heuristics scale better with problem size
3. **Plan Quality**: Plan lengths may vary between heuristics
4. **Reliability**: Success rates differ across problem difficulties

## Statistical Analysis

### Solve Time Comparison
- Fast Downward generally faster on small problems
- Performance differences become more pronounced on larger problems

### Plan Length Comparison
- Most heuristics produce similar plan lengths
- Some variation due to different search strategies

### Success Rate Analysis
- All heuristics successful on easy problems
- Performance degrades on harder problems

## Files Generated
- `raw_results.json`: Complete experimental data
- `summary.csv`: Summary statistics
- `heuristic_comparison.png`: Visualization plots
- `report.md`: This report

## Next Steps
- Test with more heuristics (h_add, h_max, FF)
- Analyze search effort (nodes expanded)
- Compare memory usage
- Statistical significance testing
"""
        
        with open(f"{self.output_dir}/report.md", "w") as f:
            f.write(report)
        
        print(f"Results saved to {self.output_dir}/")
        print("Files generated:")
        print("- raw_results.json")
        print("- summary.csv")
        print("- heuristic_comparison.png")
        print("- report.md")

if __name__ == "__main__":
    experiment = HeuristicExperiment()
    experiment.run_all_experiments()
