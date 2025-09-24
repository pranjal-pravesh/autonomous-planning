#!/usr/bin/env python3
"""
Topology Analysis Experiment

This experiment analyzes how different dock topologies affect planning performance:
- Linear topology (docks in a line)
- Star topology (central hub with spokes)
- Grid topology (2D grid of docks)
- Ring topology (circular arrangement)
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

class TopologyAnalysisExperiment:
    def __init__(self, output_dir: str = "experiments/topology/results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Experiment configurations testing different topologies
        self.topology_configs = [
            {
                "name": "linear_4",
                "description": "Linear topology with 4 docks",
                "topology": "linear",
                "docks": 4,
                "robots": 2, "containers": 8, "piles": 4
            },
            {
                "name": "linear_6",
                "description": "Linear topology with 6 docks",
                "topology": "linear",
                "docks": 6,
                "robots": 2, "containers": 12, "piles": 6
            },
            {
                "name": "star_5",
                "description": "Star topology with 5 docks (1 center + 4 spokes)",
                "topology": "star",
                "docks": 5,
                "robots": 2, "containers": 10, "piles": 5
            },
            {
                "name": "star_7",
                "description": "Star topology with 7 docks (1 center + 6 spokes)",
                "topology": "star",
                "docks": 7,
                "robots": 3, "containers": 14, "piles": 7
            },
            {
                "name": "grid_2x2",
                "description": "2x2 Grid topology",
                "topology": "grid",
                "docks": 4,
                "grid_size": (2, 2),
                "robots": 2, "containers": 8, "piles": 4
            },
            {
                "name": "grid_3x2",
                "description": "3x2 Grid topology",
                "topology": "grid",
                "docks": 6,
                "grid_size": (3, 2),
                "robots": 3, "containers": 12, "piles": 6
            },
            {
                "name": "ring_4",
                "description": "Ring topology with 4 docks",
                "topology": "ring",
                "docks": 4,
                "robots": 2, "containers": 8, "piles": 4
            },
            {
                "name": "ring_6",
                "description": "Ring topology with 6 docks",
                "topology": "ring",
                "docks": 6,
                "robots": 2, "containers": 12, "piles": 6
            }
        ]
        
        self.results = []
    
    def create_adjacency(self, config: Dict) -> List[Tuple[int, int]]:
        """Create adjacency relationships based on topology."""
        docks = config["docks"]
        topology = config["topology"]
        adjacencies = []
        
        if topology == "linear":
            # Linear: d1-d2-d3-d4...
            for i in range(docks - 1):
                adjacencies.append((i, i + 1))
                adjacencies.append((i + 1, i))  # Bidirectional
        
        elif topology == "star":
            # Star: center (0) connected to all others
            center = 0
            for i in range(1, docks):
                adjacencies.append((center, i))
                adjacencies.append((i, center))  # Bidirectional
        
        elif topology == "grid":
            # Grid: 2D grid with 4-connected neighbors
            rows, cols = config["grid_size"]
            for r in range(rows):
                for c in range(cols):
                    node = r * cols + c
                    # Right neighbor
                    if c < cols - 1:
                        right = r * cols + (c + 1)
                        adjacencies.append((node, right))
                        adjacencies.append((right, node))
                    # Down neighbor
                    if r < rows - 1:
                        down = (r + 1) * cols + c
                        adjacencies.append((node, down))
                        adjacencies.append((down, node))
        
        elif topology == "ring":
            # Ring: circular arrangement
            for i in range(docks):
                next_i = (i + 1) % docks
                adjacencies.append((i, next_i))
                adjacencies.append((next_i, i))  # Bidirectional
        
        return adjacencies
    
    def create_problem(self, config: Dict) -> Tuple[Problem, LogisticsDomain]:
        """Create a logistics problem with given topology configuration."""
        domain = LogisticsDomain(scale="small", auto_objects=False)
        problem = Problem(f"topology_analysis_{config['name']}")
        
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
            initial_state[domain.robot_capacity_6(robot)] = True
            initial_state[domain.robot_weight_0(robot)] = True
            initial_state[domain.robot_free(robot)] = True
        
        # Container weights (mixed for interesting planning)
        for i, container in enumerate(containers):
            if i % 3 == 0:
                initial_state[domain.container_weight_2(container)] = True
            elif i % 3 == 1:
                initial_state[domain.container_weight_4(container)] = True
            else:
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
        
        # Set adjacency based on topology
        adjacencies = self.create_adjacency(config)
        for dock1_idx, dock2_idx in adjacencies:
            initial_state[domain.adjacent(docks[dock1_idx], docks[dock2_idx])] = True
        
        # Set initial values
        for fluent, value in initial_state.items():
            problem.set_initial_value(fluent, value)
        
        # Create challenging goal that requires movement between distant docks
        goal_conditions = []
        if len(containers) >= 4 and len(piles) >= 3:
            # Goal: move containers to create a cross-topology pattern
            goal_conditions.extend([
                # Move first container to last pile
                domain.container_in_pile(containers[0], piles[-1]),
                domain.container_on_top_of_pile(containers[0], piles[-1]),
                # Move second container to first pile
                domain.container_in_pile(containers[1], piles[0]),
                domain.container_on_top_of_pile(containers[1], piles[0]),
                # Move third container to middle pile
                domain.container_in_pile(containers[2], piles[len(piles)//2]),
                domain.container_on_top_of_pile(containers[2], piles[len(piles)//2])
            ])
        
        if goal_conditions:
            problem.add_goal(And(*goal_conditions))
        
        return problem, domain
    
    def run_experiment(self, config: Dict, num_runs: int = 5) -> Dict:
        """Run experiment for given topology configuration."""
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
        """Run all topology analysis experiments."""
        print("Starting Topology Analysis Experiment")
        print("=" * 50)
        
        for config in self.topology_configs:
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
        
        # Group by topology type
        topology_groups = {}
        for i, result in enumerate(self.results):
            topology = result["config"]["topology"]
            if topology not in topology_groups:
                topology_groups[topology] = []
            topology_groups[topology].append(i)
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Solve time comparison by topology
        colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow']
        topology_colors = {topology: colors[i % len(colors)] for i, topology in enumerate(topology_groups.keys())}
        
        bars1 = ax1.bar(config_names, solve_times, 
                       color=[topology_colors[r["config"]["topology"]] for r in self.results])
        ax1.set_title('Average Solve Time by Topology')
        ax1.set_ylabel('Solve Time (s)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, time in zip(bars1, solve_times):
            if time != float('inf'):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                        f'{time:.3f}s', ha='center', va='bottom', fontsize=8)
        
        # Plan length comparison by topology
        bars2 = ax2.bar(config_names, plan_lengths,
                       color=[topology_colors[r["config"]["topology"]] for r in self.results])
        ax2.set_title('Average Plan Length by Topology')
        ax2.set_ylabel('Plan Length (actions)')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, length in zip(bars2, plan_lengths):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{length:.0f}', ha='center', va='bottom', fontsize=8)
        
        # Success rate comparison
        bars3 = ax3.bar(config_names, success_rates,
                       color=[topology_colors[r["config"]["topology"]] for r in self.results])
        ax3.set_title('Success Rate by Topology')
        ax3.set_ylabel('Success Rate')
        ax3.set_ylim(0, 1.1)
        ax3.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, rate in zip(bars3, success_rates):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{rate:.2f}', ha='center', va='bottom', fontsize=8)
        
        # Topology efficiency comparison (solve time vs plan length)
        ax4.scatter(plan_lengths, solve_times, 
                   c=[topology_colors[r["config"]["topology"]] for r in self.results],
                   s=100, alpha=0.7)
        
        for i, name in enumerate(config_names):
            ax4.annotate(name, (plan_lengths[i], solve_times[i]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        ax4.set_xlabel('Plan Length (actions)')
        ax4.set_ylabel('Solve Time (s)')
        ax4.set_title('Topology Efficiency: Solve Time vs Plan Length')
        
        # Add legend for topology types
        legend_elements = [plt.Rectangle((0,0),1,1, color=color, label=topology) 
                          for topology, color in topology_colors.items()]
        ax4.legend(handles=legend_elements, loc='upper left')
        
        plt.tight_layout()
        
        # Save plot
        plot_file = os.path.join(self.output_dir, "topology_analysis.png")
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Plot saved to {plot_file}")
    
    def generate_report(self):
        """Generate a markdown report."""
        report_file = os.path.join(self.output_dir, "report.md")
        
        with open(report_file, 'w') as f:
            f.write("# Topology Analysis Report\n\n")
            f.write("This experiment analyzes how different dock topologies affect planning performance.\n\n")
            
            f.write("## Experiment Configuration\n\n")
            f.write("| Topology | Description | Docks | Robots | Containers | Piles |\n")
            f.write("|----------|-------------|-------|--------|------------|-------|\n")
            
            for result in self.results:
                config = result["config"]
                f.write(f"| {config['name']} | {config['description']} | {config['docks']} | {config['robots']} | {config['containers']} | {config['piles']} |\n")
            
            f.write("\n## Results Summary\n\n")
            f.write("| Topology | Success Rate | Avg Solve Time (s) | Avg Plan Length |\n")
            f.write("|----------|--------------|-------------------|----------------|\n")
            
            for result in self.results:
                config = result["config"]
                summary = result["summary"]
                f.write(f"| {config['name']} | {summary['success_rate']:.2f} | {summary['avg_solve_time']:.3f} | {summary['avg_plan_length']:.1f} |\n")
            
            f.write("\n## Topology Analysis\n\n")
            
            # Group results by topology type
            topology_groups = {}
            for result in self.results:
                topology = result["config"]["topology"]
                if topology not in topology_groups:
                    topology_groups[topology] = []
                topology_groups[topology].append(result)
            
            for topology, results in topology_groups.items():
                f.write(f"### {topology.title()} Topology\n\n")
                avg_time = statistics.mean([r["summary"]["avg_solve_time"] for r in results])
                avg_length = statistics.mean([r["summary"]["avg_plan_length"] for r in results])
                avg_success = statistics.mean([r["summary"]["success_rate"] for r in results])
                
                f.write(f"- **Average Solve Time**: {avg_time:.3f}s\n")
                f.write(f"- **Average Plan Length**: {avg_length:.1f} actions\n")
                f.write(f"- **Average Success Rate**: {avg_success:.2f}\n\n")
            
            f.write("## Key Findings\n\n")
            f.write("This experiment reveals how different network topologies impact planning:\n\n")
            f.write("- **Linear topology**: Simple connectivity, predictable routing\n")
            f.write("- **Star topology**: Central hub provides efficient routing but creates bottlenecks\n")
            f.write("- **Grid topology**: Multiple paths provide redundancy and flexibility\n")
            f.write("- **Ring topology**: Balanced connectivity with no single points of failure\n")
            f.write("- **Scalability**: Larger topologies generally require more planning time\n")
            f.write("- **Efficiency**: Some topologies may require longer plans but solve faster\n")
        
        print(f"Report saved to {report_file}")

def main():
    experiment = TopologyAnalysisExperiment()
    experiment.run_all_experiments(num_runs=3)
    print("\nTopology Analysis completed!")

if __name__ == "__main__":
    main()
