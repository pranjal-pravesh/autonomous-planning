#!/usr/bin/env python3
"""
Real Search Analysis - Focus on Actual Data from Fast Downward

This experiment creates visualizations based on the REAL data we can extract
from Fast Downward's output, without any synthetic data.
"""

import os
import sys
import json
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import the working experiment class
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'heuristics_comparison'))
from heuristic_comparison import HeuristicExperiment


class RealSearchAnalysis(HeuristicExperiment):
    """Analysis based on real data from Fast Downward logs"""
    
    def __init__(self, output_dir: str = "experiments/search_analysis/results"):
        super().__init__(output_dir)
        
        # Focus on algorithms that show interesting differences
        self.fd_searches = [
            {"name": "gbfs_ff", "search": "gbfs(ff())", "description": "Greedy Best-First (FF)"},
            {"name": "gbfs_hadd", "search": "gbfs(hadd())", "description": "Greedy Best-First (hAdd)"},
            {"name": "astar_ff", "search": "astar(ff())", "description": "A* (FF)"},
            {"name": "astar_hadd", "search": "astar(hadd())", "description": "A* (hAdd)"},
        ]
        
        # Use problems that show clear differences
        self.test_problems = [
            {"name": "easy_4", "robots": 1, "docks": 3, "containers": 4, "piles": 3, "goal_type": "simple_swap"},
            {"name": "medium_8", "robots": 2, "docks": 4, "containers": 8, "piles": 4, "goal_type": "complex_redistribution"},
            {"name": "hard_14", "robots": 3, "docks": 6, "containers": 14, "piles": 6, "goal_type": "weight_constrained"},
        ]
    
    def extract_real_metrics(self, log_messages: List) -> Dict[str, Any]:
        """Extract real metrics from Fast Downward log messages"""
        if not log_messages:
            return {}
        
        # Combine all log messages into a single string
        log_text = ""
        for log_msg in log_messages:
            if hasattr(log_msg, 'message'):
                log_text += log_msg.message + "\n"
            else:
                log_text += str(log_msg) + "\n"
        
        metrics = {
            "nodes_expanded": 0,
            "nodes_generated": 0,
            "nodes_evaluated": 0,
            "peak_memory_kb": 0,
            "search_time": 0.0,
            "total_time": 0.0,
            "initial_heuristic": 0,
            "final_heuristic": 0,
            "heuristic_name": "unknown"
        }
        
        lines = log_text.split('\n')
        
        for line in lines:
            # Extract final statistics
            if "Expanded" in line and "state" in line:
                match = re.search(r'Expanded (\d+) state\(s\)', line)
                if match:
                    metrics["nodes_expanded"] = int(match.group(1))
            
            if "Generated" in line and "state" in line:
                match = re.search(r'Generated (\d+) state\(s\)', line)
                if match:
                    metrics["nodes_generated"] = int(match.group(1))
            
            if "Evaluated" in line and "state" in line:
                match = re.search(r'Evaluated (\d+) state\(s\)', line)
                if match:
                    metrics["nodes_evaluated"] = int(match.group(1))
            
            if "Peak memory:" in line:
                match = re.search(r'Peak memory: (\d+) KB', line)
                if match:
                    # Convert KB to MB for more reasonable values
                    metrics["peak_memory_kb"] = int(match.group(1)) / 1024
            
            if "Search time:" in line:
                match = re.search(r'Search time: ([\d.]+)s', line)
                if match:
                    metrics["search_time"] = float(match.group(1))
            
            if "Total time:" in line:
                match = re.search(r'Total time: ([\d.]+)s', line)
                if match:
                    metrics["total_time"] = float(match.group(1))
            
            # Extract heuristic information
            if "Initial heuristic value" in line:
                match = re.search(r'Initial heuristic value for ([^:]+): (\d+)', line)
                if match:
                    metrics["heuristic_name"] = match.group(1).strip()
                    metrics["initial_heuristic"] = int(match.group(2))
            
            if "New best heuristic value" in line:
                match = re.search(r'New best heuristic value for ([^:]+): (\d+)', line)
                if match:
                    metrics["final_heuristic"] = int(match.group(2))
        
        # Calculate derived metrics
        if metrics["nodes_generated"] > 0:
            metrics["search_efficiency"] = metrics["nodes_expanded"] / metrics["nodes_generated"]
        else:
            metrics["search_efficiency"] = 0.0
        
        if metrics["nodes_expanded"] > 0:
            metrics["expansion_rate"] = metrics["nodes_expanded"] / (metrics["search_time"] + 1e-6)
        else:
            metrics["expansion_rate"] = 0.0
        
        return metrics
    
    def run_real_search_experiment(self):
        """Run experiment focusing on real data extraction"""
        print("Starting REAL SEARCH ANALYSIS")
        print("=" * 60)
        print("Extracting real metrics from Fast Downward:")
        print("- Final search statistics")
        print("- Heuristic values")
        print("- Memory usage")
        print("- Search efficiency")
        print()
        
        # Create results directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        all_real_data = []
        
        for problem_config in self.test_problems:
            print(f"Testing problem: {problem_config['name']}")
            
            for search_config in self.fd_searches:
                print(f"  Testing {search_config['name']} ({search_config['description']})")
                
                # Run the experiment
                experiment_result = self.run_experiment_with_logs(problem_config, search_config, num_runs=3)
                
                # Extract real metrics from successful runs
                successful_runs = [run for run in experiment_result["runs"] if run["success"]]
                if successful_runs:
                    # Use the first successful run for detailed metrics
                    run_data = successful_runs[0]
                    real_metrics = self.extract_real_metrics(run_data.get("log_messages", []))
                    
                    # Add metadata
                    real_metrics.update({
                        "problem": problem_config["name"],
                        "algorithm": search_config["name"],
                        "description": search_config["description"],
                        "solve_time": run_data["solve_time"],
                        "plan_length": run_data["plan_length"],
                        "success_rate": len(successful_runs) / len(experiment_result["runs"])
                    })
                    
                    all_real_data.append(real_metrics)
                    print(f"    ✅ Extracted real metrics: {real_metrics['nodes_expanded']} expanded, {real_metrics['nodes_generated']} generated")
                else:
                    print(f"    ❌ No successful runs")
        
        # Save real data
        with open(os.path.join(self.output_dir, "real_search_metrics.json"), 'w') as f:
            json.dump(all_real_data, f, indent=2)
        
        # Create visualizations based on real data
        self.create_real_data_plots(all_real_data)
        
        print(f"\nREAL SEARCH ANALYSIS completed! Results saved to {self.output_dir}")
    
    def run_experiment_with_logs(self, problem_config: Dict, search_config: Dict, num_runs: int = 3) -> Dict:
        """Run experiment and capture log messages"""
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
                
                # Use UP Fast Downward interface
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
    
    def create_real_data_plots(self, real_data: List[Dict]):
        """Create visualizations based on real extracted data"""
        print("Creating REAL DATA visualizations...")
        
        if not real_data:
            print("No real data to plot")
            return
        
        # Create comprehensive visualization of real metrics
        fig, axes = plt.subplots(3, 3, figsize=(20, 18))
        fig.suptitle('SEARCH METRICS - Fast Downward Statistics', fontsize=16, fontweight='bold')
        
        # Define colors for different algorithms
        colors = {
            'gbfs_ff': 'lightblue',
            'gbfs_hadd': 'lightgreen', 
            'astar_ff': 'lightcoral',
            'astar_hadd': 'lightyellow'
        }
        
        # Convert to DataFrame for easier plotting
        df = pd.DataFrame(real_data)
        
        # 1. Nodes Expanded by Algorithm
        ax1 = axes[0, 0]
        df.boxplot(column='nodes_expanded', by='algorithm', ax=ax1, patch_artist=True)
        for patch, alg in zip(ax1.artists, df['algorithm'].unique()):
            patch.set_facecolor(colors.get(alg, 'gray'))
        ax1.set_title('Nodes Expanded by Algorithm')
        ax1.set_xlabel('Algorithm')
        ax1.set_ylabel('Nodes Expanded')
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. Search Efficiency by Algorithm
        ax2 = axes[0, 1]
        df.boxplot(column='search_efficiency', by='algorithm', ax=ax2, patch_artist=True)
        for patch, alg in zip(ax2.artists, df['algorithm'].unique()):
            patch.set_facecolor(colors.get(alg, 'gray'))
        ax2.set_title('Search Efficiency by Algorithm')
        ax2.set_xlabel('Algorithm')
        ax2.set_ylabel('Search Efficiency')
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Memory Usage by Algorithm
        ax3 = axes[0, 2]
        df.boxplot(column='peak_memory_kb', by='algorithm', ax=ax3, patch_artist=True)
        for patch, alg in zip(ax3.artists, df['algorithm'].unique()):
            patch.set_facecolor(colors.get(alg, 'gray'))
        ax3.set_title('Peak Memory by Algorithm')
        ax3.set_xlabel('Algorithm')
        ax3.set_ylabel('Peak Memory (MB)')
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Solve Time by Problem
        ax4 = axes[1, 0]
        problem_times = df.groupby('problem')['solve_time'].mean().sort_values(ascending=False)
        problem_times.plot(kind='bar', ax=ax4, color='lightcoral', alpha=0.8)
        ax4.set_title('Solve Time by Problem')
        ax4.set_xlabel('Problem')
        ax4.set_ylabel('Solve Time (s)')
        ax4.tick_params(axis='x', rotation=45)
        
        # 5. Heuristic Values
        ax5 = axes[1, 1]
        for data in real_data:
            if data['initial_heuristic'] > 0:
                ax5.scatter(data['algorithm'], data['initial_heuristic'], 
                           color=colors.get(data['algorithm'], 'gray'), 
                           s=100, alpha=0.7, label=f"{data['algorithm']} ({data['problem']})")
        ax5.set_title('Initial Heuristic Values')
        ax5.set_xlabel('Algorithm')
        ax5.set_ylabel('Initial Heuristic Value')
        ax5.tick_params(axis='x', rotation=45)
        ax5.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 6. Search Efficiency vs Problem Size
        ax6 = axes[1, 2]
        problem_sizes = {'easy_4': 4, 'medium_8': 8, 'hard_14': 14}
        for data in real_data:
            if data['problem'] in problem_sizes:
                size = problem_sizes[data['problem']]
                ax6.scatter(size, data['search_efficiency'], 
                           color=colors.get(data['algorithm'], 'gray'), 
                           s=100, alpha=0.7, label=f"{data['algorithm']}")
        ax6.set_title('Search Efficiency vs Problem Size')
        ax6.set_xlabel('Problem Size (containers)')
        ax6.set_ylabel('Search Efficiency')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        # 7. Memory vs Performance Trade-off
        ax7 = axes[2, 0]
        for data in real_data:
            ax7.scatter(data['peak_memory_kb'], data['solve_time'], 
                       color=colors.get(data['algorithm'], 'gray'), 
                       s=100, alpha=0.7, label=f"{data['algorithm']} ({data['problem']})")
        ax7.set_title('Memory vs Performance Trade-off')
        ax7.set_xlabel('Peak Memory (MB)')
        ax7.set_ylabel('Solve Time (s)')
        ax7.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax7.grid(True, alpha=0.3)
        
        # 8. Algorithm Performance Heatmap
        ax8 = axes[2, 1]
        algorithms = df['algorithm'].unique()
        problems = df['problem'].unique()
        
        performance_matrix = np.zeros((len(algorithms), len(problems)))
        for i, alg in enumerate(algorithms):
            for j, problem in enumerate(problems):
                alg_data = df[(df['algorithm'] == alg) & (df['problem'] == problem)]
                if not alg_data.empty:
                    performance_matrix[i, j] = alg_data['solve_time'].iloc[0]
        
        im = ax8.imshow(performance_matrix, cmap='YlOrRd', aspect='auto')
        ax8.set_xticks(range(len(problems)))
        ax8.set_yticks(range(len(algorithms)))
        ax8.set_xticklabels(problems)
        ax8.set_yticklabels(algorithms)
        ax8.set_title('Algorithm Performance Heatmap')
        
        # Add text annotations
        for i in range(len(algorithms)):
            for j in range(len(problems)):
                text = ax8.text(j, i, f'{performance_matrix[i, j]:.2f}',
                               ha="center", va="center", color="black", fontweight='bold')
        
        plt.colorbar(im, ax=ax8)
        
        # 9. Search Statistics Summary
        ax9 = axes[2, 2]
        summary_stats = {
            'Total Runs': len(real_data),
            'Avg Nodes Expanded': int(df['nodes_expanded'].mean()),
            'Avg Search Efficiency': f"{df['search_efficiency'].mean():.3f}",
            'Avg Memory (MB)': f"{df['peak_memory_kb'].mean():.1f}",
            'Avg Solve Time (s)': f"{df['solve_time'].mean():.3f}"
        }
        
        y_pos = np.arange(len(summary_stats))
        values = [summary_stats[key] for key in summary_stats.keys()]
        
        ax9.barh(y_pos, [1] * len(summary_stats), color='lightblue', alpha=0.7)
        ax9.set_yticks(y_pos)
        ax9.set_yticklabels(summary_stats.keys())
        ax9.set_xlim(0, 1)
        ax9.set_title('Search Statistics Summary')
        
        # Add value labels
        for i, (key, value) in enumerate(summary_stats.items()):
            ax9.text(0.5, i, str(value), ha='center', va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "real_search_metrics.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        # Create additional focused plots
        self.create_algorithm_comparison_plots(real_data)
        self.create_problem_analysis_plots(real_data)
        
        print("Real data visualizations saved to real_search_metrics.png")
    
    def create_algorithm_comparison_plots(self, real_data: List[Dict]):
        """Create focused algorithm comparison plots"""
        print("Creating algorithm comparison plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Algorithm Comparison', fontsize=14, fontweight='bold')
        
        colors = {
            'gbfs_ff': 'lightblue',
            'gbfs_hadd': 'lightgreen', 
            'astar_ff': 'lightcoral',
            'astar_hadd': 'lightyellow'
        }
        
        df = pd.DataFrame(real_data)
        
        # 1. Performance by Algorithm and Problem
        ax1 = axes[0, 0]
        for problem in df['problem'].unique():
            problem_data = df[df['problem'] == problem]
            algorithms = problem_data['algorithm'].tolist()
            solve_times = problem_data['solve_time'].tolist()
            
            x = np.arange(len(algorithms))
            ax1.bar(x, solve_times, label=problem, alpha=0.8)
        
        ax1.set_title('Solve Time by Algorithm and Problem')
        ax1.set_xlabel('Algorithm')
        ax1.set_ylabel('Solve Time (s)')
        ax1.set_xticks(range(len(df['algorithm'].unique())))
        ax1.set_xticklabels(df['algorithm'].unique(), rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Search Efficiency Comparison
        ax2 = axes[0, 1]
        efficiency_by_algorithm = df.groupby('algorithm')['search_efficiency'].mean()
        bars = ax2.bar(efficiency_by_algorithm.index, efficiency_by_algorithm.values, 
                      color=[colors.get(alg, 'gray') for alg in efficiency_by_algorithm.index], alpha=0.8)
        
        ax2.set_title('Average Search Efficiency by Algorithm')
        ax2.set_xlabel('Algorithm')
        ax2.set_ylabel('Search Efficiency')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars, efficiency_by_algorithm.values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                    f'{value:.3f}', ha='center', va='bottom')
        
        # 3. Memory Usage Comparison
        ax3 = axes[1, 0]
        memory_by_algorithm = df.groupby('algorithm')['peak_memory_kb'].mean()
        bars = ax3.bar(memory_by_algorithm.index, memory_by_algorithm.values, 
                      color=[colors.get(alg, 'gray') for alg in memory_by_algorithm.index], alpha=0.8)
        
        ax3.set_title('Average Memory Usage by Algorithm')
        ax3.set_xlabel('Algorithm')
        ax3.set_ylabel('Peak Memory (MB)')
        ax3.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars, memory_by_algorithm.values):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{value:.1f}MB', ha='center', va='bottom')
        
        # 4. Nodes Expanded vs Generated
        ax4 = axes[1, 1]
        for data in real_data:
            ax4.scatter(data['nodes_generated'], data['nodes_expanded'], 
                       color=colors.get(data['algorithm'], 'gray'), 
                       s=100, alpha=0.7, label=f"{data['algorithm']} ({data['problem']})")
        
        # Add diagonal line for reference
        max_nodes = max(df['nodes_generated'].max(), df['nodes_expanded'].max())
        ax4.plot([0, max_nodes], [0, max_nodes], 'k--', alpha=0.5, label='Perfect Efficiency')
        
        ax4.set_title('Nodes Generated vs Expanded')
        ax4.set_xlabel('Nodes Generated')
        ax4.set_ylabel('Nodes Expanded')
        ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "algorithm_comparison_real.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Algorithm comparison plots saved to algorithm_comparison_real.png")
    
    def create_problem_analysis_plots(self, real_data: List[Dict]):
        """Create problem-focused analysis plots"""
        print("Creating problem analysis plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Problem Analysis', fontsize=14, fontweight='bold')
        
        colors = {
            'gbfs_ff': 'lightblue',
            'gbfs_hadd': 'lightgreen', 
            'astar_ff': 'lightcoral',
            'astar_hadd': 'lightyellow'
        }
        
        df = pd.DataFrame(real_data)
        
        # 1. Problem Difficulty Scaling
        ax1 = axes[0, 0]
        problem_sizes = {'easy_4': 4, 'medium_8': 8, 'hard_14': 14}
        
        for alg in df['algorithm'].unique():
            alg_data = df[df['algorithm'] == alg]
            sizes = [problem_sizes[p] for p in alg_data['problem']]
            solve_times = alg_data['solve_time'].tolist()
            
            ax1.plot(sizes, solve_times, 'o-', color=colors.get(alg, 'gray'), 
                    label=alg, linewidth=2, markersize=8)
        
        ax1.set_title('Problem Difficulty Scaling')
        ax1.set_xlabel('Problem Size (containers)')
        ax1.set_ylabel('Solve Time (s)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Search Efficiency by Problem
        ax2 = axes[0, 1]
        df.boxplot(column='search_efficiency', by='problem', ax=ax2, patch_artist=True)
        ax2.set_title('Search Efficiency by Problem')
        ax2.set_xlabel('Problem')
        ax2.set_ylabel('Search Efficiency')
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Memory Usage by Problem
        ax3 = axes[1, 0]
        df.boxplot(column='peak_memory_kb', by='problem', ax=ax3, patch_artist=True)
        ax3.set_title('Memory Usage by Problem')
        ax3.set_xlabel('Problem')
        ax3.set_ylabel('Peak Memory (MB)')
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Heuristic Values by Problem
        ax4 = axes[1, 1]
        for data in real_data:
            if data['initial_heuristic'] > 0:
                ax4.scatter(data['problem'], data['initial_heuristic'], 
                           color=colors.get(data['algorithm'], 'gray'), 
                           s=100, alpha=0.7, label=f"{data['algorithm']}")
        
        ax4.set_title('Initial Heuristic Values by Problem')
        ax4.set_xlabel('Problem')
        ax4.set_ylabel('Initial Heuristic Value')
        ax4.tick_params(axis='x', rotation=45)
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "problem_analysis_real.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Problem analysis plots saved to problem_analysis_real.png")


if __name__ == "__main__":
    experiment = RealSearchAnalysis()
    experiment.run_real_search_experiment()
