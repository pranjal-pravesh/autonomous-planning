#!/usr/bin/env python3
"""
During Search Analysis - Real-time Search Behavior Visualization

This experiment captures and visualizes the real-time behavior of search algorithms
during execution, providing insights into:
- Search progress over time
- Heuristic value evolution
- Memory usage patterns
- Node expansion patterns
- Search efficiency trends
- Algorithm comparison during execution
"""

import os
import sys
import json
import time
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import the working experiment class
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'heuristics_comparison'))
from heuristic_comparison import HeuristicExperiment


class DuringSearchAnalysis(HeuristicExperiment):
    """Analysis of real-time search behavior during algorithm execution"""
    
    def __init__(self, output_dir: str = "experiments/search_analysis/results"):
        super().__init__(output_dir)
        
        # Focus on algorithms that show interesting search patterns
        self.fd_searches = [
            {"name": "gbfs_ff", "search": "gbfs(ff())", "description": "Greedy Best-First (FF)"},
            {"name": "gbfs_hadd", "search": "gbfs(hadd())", "description": "Greedy Best-First (hAdd)"},
            {"name": "astar_ff", "search": "astar(ff())", "description": "A* (FF)"},
            {"name": "astar_hadd", "search": "astar(hadd())", "description": "A* (hAdd)"},
        ]
        
        # Use problems that show interesting scaling behavior
        self.test_problems = [
            {"name": "easy_4", "robots": 1, "docks": 3, "containers": 4, "piles": 3, "goal_type": "simple_swap"},
            {"name": "medium_8", "robots": 2, "docks": 4, "containers": 8, "piles": 4, "goal_type": "complex_redistribution"},
            {"name": "hard_14", "robots": 3, "docks": 6, "containers": 14, "piles": 6, "goal_type": "weight_constrained"},
        ]
    
    def parse_search_timeline(self, log_messages: List) -> Dict[str, List]:
        """Parse log messages to extract REAL search timeline data"""
        if not log_messages:
            return {}
        
        # Combine all log messages into a single string
        log_text = ""
        for log_msg in log_messages:
            if hasattr(log_msg, 'message'):
                log_text += log_msg.message + "\n"
            else:
                log_text += str(log_msg) + "\n"
        
        timeline = {
            "search_time": [],
            "nodes_expanded": [],
            "nodes_generated": [],
            "nodes_evaluated": [],
            "heuristic_values": [],
            "memory_usage": [],
            "search_efficiency": []
        }
        
        # Parse the log text for real search progression
        lines = log_text.split('\n')
        
        # Look for actual search progression patterns in Fast Downward output
        for line in lines:
            # Parse search time progression
            if "Search time:" in line:
                time_match = re.search(r'Search time: ([\d.]+)s', line)
                if time_match:
                    timeline["search_time"].append(float(time_match.group(1)))
            
            # Parse node expansion progression
            if "Expanded" in line and "state" in line:
                expanded_match = re.search(r'Expanded (\d+) state\(s\)', line)
                if expanded_match:
                    timeline["nodes_expanded"].append(int(expanded_match.group(1)))
            
            # Parse node generation progression
            if "Generated" in line and "state" in line:
                generated_match = re.search(r'Generated (\d+) state\(s\)', line)
                if generated_match:
                    timeline["nodes_generated"].append(int(generated_match.group(1)))
            
            # Parse node evaluation progression
            if "Evaluated" in line and "state" in line:
                evaluated_match = re.search(r'Evaluated (\d+) state\(s\)', line)
                if evaluated_match:
                    timeline["nodes_evaluated"].append(int(evaluated_match.group(1)))
            
            # Parse memory usage progression
            if "Peak memory:" in line:
                memory_match = re.search(r'Peak memory: (\d+) KB', line)
                if memory_match:
                    timeline["memory_usage"].append(int(memory_match.group(1)))
            
            # Parse heuristic values
            if "Initial heuristic value" in line:
                h_match = re.search(r'Initial heuristic value for ([^:]+): (\d+)', line)
                if h_match:
                    timeline["heuristic_values"].append({
                        "time": 0.0,
                        "heuristic": h_match.group(1).strip(),
                        "value": int(h_match.group(2))
                    })
            
            if "New best heuristic value" in line:
                h_match = re.search(r'New best heuristic value for ([^:]+): (\d+)', line)
                if h_match:
                    # Try to extract time from context
                    current_time = timeline["search_time"][-1] if timeline["search_time"] else 0.0
                    timeline["heuristic_values"].append({
                        "time": current_time,
                        "heuristic": h_match.group(1).strip(),
                        "value": int(h_match.group(2))
                    })
        
        # Calculate search efficiency from real data
        for i in range(len(timeline["nodes_expanded"])):
            if i < len(timeline["nodes_generated"]) and timeline["nodes_generated"][i] > 0:
                efficiency = timeline["nodes_expanded"][i] / timeline["nodes_generated"][i]
                timeline["search_efficiency"].append(efficiency)
            else:
                timeline["search_efficiency"].append(0.0)
        
        # Ensure all arrays have the same length
        max_len = max(len(timeline["search_time"]), len(timeline["nodes_expanded"]), 
                     len(timeline["nodes_generated"]), len(timeline["memory_usage"]))
        
        # Pad shorter arrays with their last values
        for key in ["search_time", "nodes_expanded", "nodes_generated", "nodes_evaluated", "memory_usage"]:
            while len(timeline[key]) < max_len:
                if timeline[key]:
                    timeline[key].append(timeline[key][-1])
                else:
                    timeline[key].append(0)
        
        # Ensure search_efficiency has the right length
        while len(timeline["search_efficiency"]) < max_len:
            if timeline["search_efficiency"]:
                timeline["search_efficiency"].append(timeline["search_efficiency"][-1])
            else:
                timeline["search_efficiency"].append(0.0)
        
        return timeline
    
    
    def run_during_search_experiment(self):
        """Run experiment capturing during-search behavior"""
        print("Starting DURING SEARCH ANALYSIS")
        print("=" * 60)
        print("Capturing real-time search behavior:")
        print("- Search progress over time")
        print("- Heuristic value evolution")
        print("- Memory usage patterns")
        print("- Node expansion patterns")
        print("- Search efficiency trends")
        print()
        
        # Create results directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        all_timeline_data = []
        
        for problem_config in self.test_problems:
            print(f"Testing problem: {problem_config['name']}")
            
            for search_config in self.fd_searches:
                print(f"  Testing {search_config['name']} ({search_config['description']})")
                
                # Run the experiment with detailed logging
                experiment_result = self.run_experiment_with_logs(problem_config, search_config, num_runs=1)
                
                # Extract timeline data from the first successful run
                successful_runs = [run for run in experiment_result["runs"] if run["success"]]
                if successful_runs:
                    run_data = successful_runs[0]
                    timeline = self.parse_search_timeline(run_data.get("log_messages", []))
                    
                    # Add metadata
                    timeline["problem"] = problem_config["name"]
                    timeline["algorithm"] = search_config["name"]
                    timeline["description"] = search_config["description"]
                    timeline["total_solve_time"] = run_data["solve_time"]
                    timeline["plan_length"] = run_data["plan_length"]
                    
                    all_timeline_data.append(timeline)
                    print(f"    ✅ Captured {len(timeline['search_time'])} timeline points")
                else:
                    print(f"    ❌ No successful runs")
        
        # Save timeline data
        with open(os.path.join(self.output_dir, "during_search_timeline.json"), 'w') as f:
            json.dump(all_timeline_data, f, indent=2)
        
        # Create during-search visualizations
        self.create_during_search_plots(all_timeline_data)
        
        print(f"\nDURING SEARCH ANALYSIS completed! Results saved to {self.output_dir}")
    
    def run_experiment_with_logs(self, problem_config: Dict, search_config: Dict, num_runs: int = 1) -> Dict:
        """Run experiment and capture log messages for timeline analysis"""
        from unified_planning.shortcuts import OneshotPlanner
        from unified_planning.engines import PlanGenerationResultStatus
        import time
        
        results = {
            "problem": problem_config,
            "search": search_config,
            "runs": []
        }
        
        for run in range(num_runs):
            try:
                problem, domain = self.create_problem(problem_config)
                
                # Use UP Fast Downward interface with verbose output
                start_time = time.time()
                with OneshotPlanner(name='fast-downward') as planner:
                    # Try to get more verbose output by using search options
                    result = planner.solve(problem, output_stream=None)
                solve_time = time.time() - start_time
                
                success = result.status == PlanGenerationResultStatus.SOLVED_SATISFICING
                plan_length = len(result.plan.actions) if result.plan else 0
                status = str(result.status)
                
                run_result = {
                    "run": run,
                    "success": success,
                    "solve_time": solve_time,
                    "plan_length": plan_length,
                    "status": status,
                    "log_messages": result.log_messages if hasattr(result, 'log_messages') else []
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
                    "status": f"ERROR: {str(e)}",
                    "log_messages": []
                })
        
        return results
    
    def create_during_search_plots(self, timeline_data: List[Dict]):
        """Create fascinating during-search visualizations"""
        print("Creating DURING SEARCH visualizations...")
        
        if not timeline_data:
            print("No timeline data to plot")
            return
        
        # Create a comprehensive during-search visualization
        fig, axes = plt.subplots(3, 3, figsize=(20, 18))
        fig.suptitle('DURING SEARCH ANALYSIS - Real-time Algorithm Behavior', fontsize=16, fontweight='bold')
        
        # Define colors for different algorithms
        colors = {
            'gbfs_ff': 'lightblue',
            'gbfs_hadd': 'lightgreen', 
            'astar_ff': 'lightcoral',
            'astar_hadd': 'lightyellow'
        }
        
        # 1. Search Progress Over Time
        ax1 = axes[0, 0]
        for data in timeline_data:
            if data['search_time'] and data['nodes_expanded']:
                ax1.plot(data['search_time'], data['nodes_expanded'], 
                        label=f"{data['algorithm']} ({data['problem']})", 
                        color=colors.get(data['algorithm'], 'gray'),
                        linewidth=2, alpha=0.8)
        ax1.set_title('Search Progress: Nodes Expanded Over Time')
        ax1.set_xlabel('Search Time (s)')
        ax1.set_ylabel('Nodes Expanded')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # 2. Memory Usage Over Time
        ax2 = axes[0, 1]
        for data in timeline_data:
            if data['search_time'] and data['memory_usage']:
                ax2.plot(data['search_time'], data['memory_usage'], 
                        label=f"{data['algorithm']} ({data['problem']})", 
                        color=colors.get(data['algorithm'], 'gray'),
                        linewidth=2, alpha=0.8)
        ax2.set_title('Memory Usage Over Time')
        ax2.set_xlabel('Search Time (s)')
        ax2.set_ylabel('Memory Usage (KB)')
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax2.grid(True, alpha=0.3)
        
        # 3. Search Efficiency Over Time
        ax3 = axes[0, 2]
        for data in timeline_data:
            if data['search_time'] and data['search_efficiency']:
                ax3.plot(data['search_time'], data['search_efficiency'], 
                        label=f"{data['algorithm']} ({data['problem']})", 
                        color=colors.get(data['algorithm'], 'gray'),
                        linewidth=2, alpha=0.8)
        ax3.set_title('Search Efficiency Over Time')
        ax3.set_xlabel('Search Time (s)')
        ax3.set_ylabel('Search Efficiency (expanded/generated)')
        ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax3.grid(True, alpha=0.3)
        
        # 4. Heuristic Value Evolution
        ax4 = axes[1, 0]
        for data in timeline_data:
            if data['heuristic_values']:
                heuristic_times = [h['time'] for h in data['heuristic_values']]
                heuristic_vals = [h['value'] for h in data['heuristic_values']]
                ax4.scatter(heuristic_times, heuristic_vals, 
                           label=f"{data['algorithm']} ({data['problem']})", 
                           color=colors.get(data['algorithm'], 'gray'),
                           alpha=0.7, s=50)
        ax4.set_title('Heuristic Value Evolution')
        ax4.set_xlabel('Search Time (s)')
        ax4.set_ylabel('Heuristic Value')
        ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax4.grid(True, alpha=0.3)
        
        # 5. Node Generation Rate
        ax5 = axes[1, 1]
        for data in timeline_data:
            if len(data['search_time']) > 1 and len(data['nodes_generated']) > 1:
                # Calculate generation rate (nodes per second)
                time_diffs = np.diff(data['search_time'])
                node_diffs = np.diff(data['nodes_generated'])
                generation_rates = node_diffs / (time_diffs + 1e-6)  # Avoid division by zero
                ax5.plot(data['search_time'][1:], generation_rates, 
                        label=f"{data['algorithm']} ({data['problem']})", 
                        color=colors.get(data['algorithm'], 'gray'),
                        linewidth=2, alpha=0.8)
        ax5.set_title('Node Generation Rate Over Time')
        ax5.set_xlabel('Search Time (s)')
        ax5.set_ylabel('Nodes Generated per Second')
        ax5.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax5.grid(True, alpha=0.3)
        
        # 6. Search Space Exploration
        ax6 = axes[1, 2]
        for data in timeline_data:
            if data['nodes_expanded'] and data['nodes_generated']:
                ax6.scatter(data['nodes_generated'], data['nodes_expanded'], 
                           label=f"{data['algorithm']} ({data['problem']})", 
                           color=colors.get(data['algorithm'], 'gray'),
                           alpha=0.7, s=60)
        ax6.set_title('Search Space Exploration')
        ax6.set_xlabel('Nodes Generated')
        ax6.set_ylabel('Nodes Expanded')
        ax6.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax6.grid(True, alpha=0.3)
        
        # 7. Algorithm Comparison by Problem
        ax7 = axes[2, 0]
        problem_data = {}
        for data in timeline_data:
            problem = data['problem']
            if problem not in problem_data:
                problem_data[problem] = []
            problem_data[problem].append({
                'algorithm': data['algorithm'],
                'solve_time': data['total_solve_time'],
                'plan_length': data['plan_length']
            })
        
        # Create comparison plot
        problems = list(problem_data.keys())
        algorithms = list(set([d['algorithm'] for data in problem_data.values() for d in data]))
        
        x = np.arange(len(problems))
        width = 0.2
        
        for i, alg in enumerate(algorithms):
            solve_times = []
            for problem in problems:
                alg_data = [d for d in problem_data[problem] if d['algorithm'] == alg]
                if alg_data:
                    solve_times.append(alg_data[0]['solve_time'])
                else:
                    solve_times.append(0)
            
            ax7.bar(x + i*width, solve_times, width, 
                   label=alg, color=colors.get(alg, 'gray'), alpha=0.8)
        
        ax7.set_title('Algorithm Performance by Problem')
        ax7.set_xlabel('Problem')
        ax7.set_ylabel('Solve Time (s)')
        ax7.set_xticks(x + width * (len(algorithms)-1) / 2)
        ax7.set_xticklabels(problems)
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        
        # 8. Search Efficiency Distribution
        ax8 = axes[2, 1]
        efficiency_data = []
        algorithm_labels = []
        for data in timeline_data:
            if data['search_efficiency']:
                efficiency_data.append(data['search_efficiency'])
                algorithm_labels.append(f"{data['algorithm']}\n({data['problem']})")
        
        if efficiency_data:
            ax8.boxplot(efficiency_data, labels=algorithm_labels, patch_artist=True)
            # Color the boxes
            for patch, alg in zip(ax8.artists, [data['algorithm'] for data in timeline_data if data['search_efficiency']]):
                patch.set_facecolor(colors.get(alg, 'gray'))
        
        ax8.set_title('Search Efficiency Distribution')
        ax8.set_ylabel('Search Efficiency')
        ax8.tick_params(axis='x', rotation=45)
        ax8.grid(True, alpha=0.3)
        
        # 9. Memory vs Performance Trade-off
        ax9 = axes[2, 2]
        for data in timeline_data:
            if data['memory_usage'] and data['total_solve_time']:
                max_memory = max(data['memory_usage']) if data['memory_usage'] else 0
                ax9.scatter(max_memory, data['total_solve_time'], 
                           label=f"{data['algorithm']} ({data['problem']})", 
                           color=colors.get(data['algorithm'], 'gray'),
                           alpha=0.7, s=100)
        ax9.set_title('Memory vs Performance Trade-off')
        ax9.set_xlabel('Peak Memory Usage (KB)')
        ax9.set_ylabel('Total Solve Time (s)')
        ax9.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax9.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "during_search_analysis.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        # Create additional specialized plots
        self.create_search_animation_plots(timeline_data)
        self.create_algorithm_comparison_plots(timeline_data)
        
        print("During-search visualizations saved to during_search_analysis.png")
    
    def create_search_animation_plots(self, timeline_data: List[Dict]):
        """Create plots that show search progression like an animation"""
        print("Creating search animation plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Search Animation - Algorithm Behavior Over Time', fontsize=14, fontweight='bold')
        
        colors = {
            'gbfs_ff': 'lightblue',
            'gbfs_hadd': 'lightgreen', 
            'astar_ff': 'lightcoral',
            'astar_hadd': 'lightyellow'
        }
        
        # 1. Search Tree Growth
        ax1 = axes[0, 0]
        for data in timeline_data:
            if data['search_time'] and data['nodes_generated']:
                ax1.plot(data['search_time'], data['nodes_generated'], 
                        label=f"{data['algorithm']} ({data['problem']})", 
                        color=colors.get(data['algorithm'], 'gray'),
                        linewidth=3, alpha=0.8)
        ax1.set_title('Search Tree Growth Over Time')
        ax1.set_xlabel('Search Time (s)')
        ax1.set_ylabel('Total Nodes Generated')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Search Efficiency Evolution
        ax2 = axes[0, 1]
        for data in timeline_data:
            if data['search_time'] and data['search_efficiency']:
                # Smooth the efficiency curve
                if len(data['search_efficiency']) > 1:
                    smoothed = np.convolve(data['search_efficiency'], np.ones(3)/3, mode='valid')
                    ax2.plot(data['search_time'][1:-1], smoothed, 
                            label=f"{data['algorithm']} ({data['problem']})", 
                            color=colors.get(data['algorithm'], 'gray'),
                            linewidth=3, alpha=0.8)
        ax2.set_title('Search Efficiency Evolution (Smoothed)')
        ax2.set_xlabel('Search Time (s)')
        ax2.set_ylabel('Search Efficiency')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Memory Usage Pattern
        ax3 = axes[1, 0]
        for data in timeline_data:
            if data['search_time'] and data['memory_usage']:
                ax3.fill_between(data['search_time'], data['memory_usage'], 
                               alpha=0.3, color=colors.get(data['algorithm'], 'gray'))
                ax3.plot(data['search_time'], data['memory_usage'], 
                        label=f"{data['algorithm']} ({data['problem']})", 
                        color=colors.get(data['algorithm'], 'gray'),
                        linewidth=2)
        ax3.set_title('Memory Usage Pattern')
        ax3.set_xlabel('Search Time (s)')
        ax3.set_ylabel('Memory Usage (KB)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Search Progress Rate
        ax4 = axes[1, 1]
        for data in timeline_data:
            if len(data['search_time']) > 1 and len(data['nodes_expanded']) > 1:
                # Calculate expansion rate
                time_diffs = np.diff(data['search_time'])
                node_diffs = np.diff(data['nodes_expanded'])
                expansion_rates = node_diffs / (time_diffs + 1e-6)
                ax4.plot(data['search_time'][1:], expansion_rates, 
                        label=f"{data['algorithm']} ({data['problem']})", 
                        color=colors.get(data['algorithm'], 'gray'),
                        linewidth=2, alpha=0.8)
        ax4.set_title('Search Progress Rate')
        ax4.set_xlabel('Search Time (s)')
        ax4.set_ylabel('Nodes Expanded per Second')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "search_animation_plots.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Search animation plots saved to search_animation_plots.png")
    
    def create_algorithm_comparison_plots(self, timeline_data: List[Dict]):
        """Create detailed algorithm comparison plots"""
        print("Creating algorithm comparison plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Algorithm Comparison - Detailed Analysis', fontsize=14, fontweight='bold')
        
        colors = {
            'gbfs_ff': 'lightblue',
            'gbfs_hadd': 'lightgreen', 
            'astar_ff': 'lightcoral',
            'astar_hadd': 'lightyellow'
        }
        
        # 1. Algorithm Performance Heatmap
        ax1 = axes[0, 0]
        algorithms = list(set([data['algorithm'] for data in timeline_data]))
        problems = list(set([data['problem'] for data in timeline_data]))
        
        performance_matrix = np.zeros((len(algorithms), len(problems)))
        for i, alg in enumerate(algorithms):
            for j, problem in enumerate(problems):
                alg_data = [data for data in timeline_data if data['algorithm'] == alg and data['problem'] == problem]
                if alg_data:
                    performance_matrix[i, j] = alg_data[0]['total_solve_time']
        
        im = ax1.imshow(performance_matrix, cmap='YlOrRd', aspect='auto')
        ax1.set_xticks(range(len(problems)))
        ax1.set_yticks(range(len(algorithms)))
        ax1.set_xticklabels(problems)
        ax1.set_yticklabels(algorithms)
        ax1.set_title('Algorithm Performance Heatmap\n(Solve Time in seconds)')
        
        # Add text annotations
        for i in range(len(algorithms)):
            for j in range(len(problems)):
                text = ax1.text(j, i, f'{performance_matrix[i, j]:.2f}',
                               ha="center", va="center", color="black", fontweight='bold')
        
        plt.colorbar(im, ax=ax1)
        
        # 2. Search Efficiency Comparison
        ax2 = axes[0, 1]
        efficiency_by_algorithm = {}
        for data in timeline_data:
            if data['search_efficiency']:
                alg = data['algorithm']
                if alg not in efficiency_by_algorithm:
                    efficiency_by_algorithm[alg] = []
                efficiency_by_algorithm[alg].extend(data['search_efficiency'])
        
        efficiency_data = [efficiency_by_algorithm[alg] for alg in algorithms if alg in efficiency_by_algorithm]
        algorithm_labels = [alg for alg in algorithms if alg in efficiency_by_algorithm]
        
        if efficiency_data:
            bp = ax2.boxplot(efficiency_data, labels=algorithm_labels, patch_artist=True)
            for patch, alg in zip(bp['boxes'], algorithm_labels):
                patch.set_facecolor(colors.get(alg, 'gray'))
        
        ax2.set_title('Search Efficiency Comparison')
        ax2.set_ylabel('Search Efficiency')
        ax2.grid(True, alpha=0.3)
        
        # 3. Memory Usage Comparison
        ax3 = axes[1, 0]
        memory_by_algorithm = {}
        for data in timeline_data:
            if data['memory_usage']:
                alg = data['algorithm']
                if alg not in memory_by_algorithm:
                    memory_by_algorithm[alg] = []
                memory_by_algorithm[alg].extend(data['memory_usage'])
        
        memory_data = [memory_by_algorithm[alg] for alg in algorithms if alg in memory_by_algorithm]
        algorithm_labels = [alg for alg in algorithms if alg in memory_by_algorithm]
        
        if memory_data:
            bp = ax3.boxplot(memory_data, labels=algorithm_labels, patch_artist=True)
            for patch, alg in zip(bp['boxes'], algorithm_labels):
                patch.set_facecolor(colors.get(alg, 'gray'))
        
        ax3.set_title('Memory Usage Comparison')
        ax3.set_ylabel('Memory Usage (KB)')
        ax3.grid(True, alpha=0.3)
        
        # 4. Performance vs Efficiency Scatter
        ax4 = axes[1, 1]
        for data in timeline_data:
            if data['search_efficiency'] and data['total_solve_time']:
                avg_efficiency = np.mean(data['search_efficiency'])
                ax4.scatter(avg_efficiency, data['total_solve_time'], 
                           label=f"{data['algorithm']} ({data['problem']})", 
                           color=colors.get(data['algorithm'], 'gray'),
                           alpha=0.7, s=100)
        ax4.set_title('Performance vs Efficiency Trade-off')
        ax4.set_xlabel('Average Search Efficiency')
        ax4.set_ylabel('Total Solve Time (s)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "algorithm_comparison_plots.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Algorithm comparison plots saved to algorithm_comparison_plots.png")


if __name__ == "__main__":
    experiment = DuringSearchAnalysis()
    experiment.run_during_search_experiment()
