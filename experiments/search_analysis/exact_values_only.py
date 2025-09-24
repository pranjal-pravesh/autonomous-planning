#!/usr/bin/env python3
"""
Exact Values Only Analysis - Unified Planning Fast Downward Interface

This experiment captures ONLY the exact values available from UP's Fast Downward interface:
- Solve Time (exact wall-clock time)
- Plan Length (exact number of actions)
- Success Rate (exact boolean)

No estimated or approximated values are included.
"""

import os
import sys
import json
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import the working experiment class
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'heuristics_comparison'))
from heuristic_comparison import HeuristicExperiment


class ExactValuesAnalysis(HeuristicExperiment):
    """Analysis focusing ONLY on exact values from UP's Fast Downward interface"""
    
    def __init__(self, output_dir: str = "experiments/search_analysis/results"):
        # Initialize with search-focused algorithms
        super().__init__(output_dir)
        
        # Focus on different search algorithms for exact analysis
        self.fd_searches = [
            {"name": "gbfs_ff", "search": "gbfs(ff())", "description": "Greedy Best-First (FF)"},
            {"name": "gbfs_hadd", "search": "gbfs(hadd())", "description": "Greedy Best-First (hAdd)"},
            {"name": "gbfs_hmax", "search": "gbfs(hmax())", "description": "Greedy Best-First (hMax)"},
            {"name": "astar_ff", "search": "astar(ff())", "description": "A* (FF)"},
            {"name": "astar_hadd", "search": "astar(hadd())", "description": "A* (hAdd)"},
            {"name": "bfs", "search": "bfs()", "description": "Breadth-First Search"},
        ]
        
        # Use proven solvable problems with varying characteristics
        self.test_problems = [
            {"name": "easy_4", "robots": 1, "docks": 3, "containers": 4, "piles": 3, "goal_type": "simple_swap"},
            {"name": "easy_6", "robots": 1, "docks": 4, "containers": 6, "piles": 4, "goal_type": "simple_swap"},
            {"name": "medium_8", "robots": 2, "docks": 4, "containers": 8, "piles": 4, "goal_type": "complex_redistribution"},
            {"name": "medium_10", "robots": 2, "docks": 5, "containers": 10, "piles": 5, "goal_type": "complex_redistribution"},
            {"name": "hard_14", "robots": 3, "docks": 6, "containers": 14, "piles": 6, "goal_type": "weight_constrained"},
        ]
    
    def run_exact_values_experiment(self):
        """Run experiment capturing ONLY exact values from UP's Fast Downward interface"""
        print("Starting EXACT VALUES ONLY Analysis")
        print("=" * 60)
        print("Capturing ONLY exact values from UP's Fast Downward interface:")
        print("- Solve Time (exact wall-clock time)")
        print("- Plan Length (exact number of actions)")
        print("- Success Rate (exact boolean)")
        print()
        
        # Create results directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        all_results = []
        
        for problem_config in self.test_problems:
            print(f"Testing problem: {problem_config['name']}")
            
            for search_config in self.fd_searches:
                print(f"  Testing {search_config['name']} ({search_config['description']})")
                
                # Run the experiment using the working base class method
                experiment_result = self.run_experiment(problem_config, search_config, num_runs=3)
                
                # Extract ONLY exact values from the experiment result
                runs = []
                for run_data in experiment_result["runs"]:
                    exact_run_data = {
                        "run": run_data["run"] + 1,  # Convert to 1-based indexing
                        "success": run_data["success"],           # EXACT boolean
                        "solve_time": float(run_data["solve_time"]),     # EXACT wall-clock time
                        "plan_length": int(run_data["plan_length"]),     # EXACT number of actions
                        "error": run_data.get("status", None) if not run_data["success"] else None
                    }
                    runs.append(exact_run_data)
                
                # Calculate exact statistics
                successful_runs = [run for run in runs if run["success"]]
                if successful_runs:
                    avg_solve_time = sum(run["solve_time"] for run in successful_runs) / len(successful_runs)
                    avg_plan_length = sum(run["plan_length"] for run in successful_runs) / len(successful_runs)
                    success_rate = len(successful_runs) / len(runs)
                else:
                    avg_solve_time = 0.0
                    avg_plan_length = 0
                    success_rate = 0.0
                
                # Store result with ONLY exact values
                result = {
                    "problem": problem_config,
                    "search": search_config,
                    "runs": runs,
                    "exact_statistics": {
                        "success_rate": success_rate,        # EXACT (calculated from exact booleans)
                        "avg_solve_time": avg_solve_time,    # EXACT (average of exact times)
                        "avg_plan_length": avg_plan_length,  # EXACT (average of exact lengths)
                        "total_runs": len(runs),             # EXACT count
                        "successful_runs": len(successful_runs)  # EXACT count
                    },
                    "timestamp": time.time()
                }
                all_results.append(result)
                
                # Print exact results
                if successful_runs:
                    print(f"    ✅ Success: {len(successful_runs)}/{len(runs)} runs, "
                          f"avg time: {avg_solve_time:.3f}s, avg plan: {avg_plan_length:.1f} actions")
                else:
                    print(f"    ❌ Failed: {len(successful_runs)}/{len(runs)} runs")
        
        # Save exact results
        with open(os.path.join(self.output_dir, "exact_values_results.json"), 'w') as f:
            json.dump(all_results, f, indent=2)
        
        # Create exact analysis and visualizations
        self.analyze_exact_values(all_results)
        self.create_exact_plots(all_results)
        
        print(f"\nEXACT VALUES experiment completed! Results saved to {self.output_dir}")
    
    def analyze_exact_values(self, results: List[Dict]):
        """Analyze ONLY exact values"""
        print("\nAnalyzing EXACT VALUES...")
        
        # Extract exact data
        exact_data = []
        for result in results:
            if result["exact_statistics"]["success_rate"] > 0:
                exact_data.append({
                    "problem": result["problem"]["name"],
                    "algorithm": result["search"]["name"],
                    "description": result["search"]["description"],
                    "success_rate": result["exact_statistics"]["success_rate"],      # EXACT
                    "avg_solve_time": result["exact_statistics"]["avg_solve_time"],  # EXACT
                    "avg_plan_length": result["exact_statistics"]["avg_plan_length"], # EXACT
                    "total_runs": result["exact_statistics"]["total_runs"],          # EXACT
                    "successful_runs": result["exact_statistics"]["successful_runs"] # EXACT
                })
        
        if not exact_data:
            print("No successful results to analyze")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(exact_data)
        
        # Create exact analysis
        analysis = {
            "total_experiments": len(results),
            "successful_experiments": len(exact_data),
            "overall_success_rate": len(exact_data) / len(results) if results else 0,
            
            "exact_algorithm_performance": {
                "solve_time": df.groupby('algorithm')['avg_solve_time'].agg(['mean', 'std', 'min', 'max']).round(4).to_dict(),
                "plan_length": df.groupby('algorithm')['avg_plan_length'].agg(['mean', 'std', 'min', 'max']).round(1).to_dict(),
                "success_rate": df.groupby('algorithm')['success_rate'].agg(['mean', 'std', 'min', 'max']).round(3).to_dict(),
            },
            
            "exact_problem_difficulty": df.groupby('problem')['avg_solve_time'].mean().sort_values(ascending=False).to_dict(),
            "exact_algorithm_ranking": df.groupby('algorithm')['avg_solve_time'].mean().sort_values(ascending=True).to_dict()
        }
        
        # Save exact analysis
        with open(os.path.join(self.output_dir, "exact_values_analysis.json"), 'w') as f:
            json.dump(analysis, f, indent=2)
        
        # Save exact data
        df.to_csv(os.path.join(self.output_dir, "exact_values_data.csv"), index=False)
        
        print("Exact analysis saved to exact_values_analysis.json and exact_values_data.csv")
    
    def create_exact_plots(self, results: List[Dict]):
        """Create plots using ONLY exact values"""
        print("Creating EXACT VALUES plots...")
        
        # Extract exact data
        exact_data = []
        for result in results:
            if result["exact_statistics"]["success_rate"] > 0:
                exact_data.append({
                    "problem": result["problem"]["name"],
                    "algorithm": result["search"]["name"],
                    "description": result["search"]["description"],
                    "success_rate": result["exact_statistics"]["success_rate"],
                    "avg_solve_time": result["exact_statistics"]["avg_solve_time"],
                    "avg_plan_length": result["exact_statistics"]["avg_plan_length"]
                })
        
        if not exact_data:
            print("No successful results to plot")
            return
        
        df = pd.DataFrame(exact_data)
        
        # Create comprehensive visualization of EXACT VALUES ONLY
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('EXACT VALUES ONLY - Unified Planning Fast Downward Interface', fontsize=16, fontweight='bold')
        
        # 1. Solve Time by Algorithm (EXACT)
        df.boxplot(column='avg_solve_time', by='algorithm', ax=axes[0,0])
        axes[0,0].set_title('Solve Time by Algorithm (EXACT)')
        axes[0,0].set_xlabel('Algorithm')
        axes[0,0].set_ylabel('Solve Time (s)')
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # 2. Plan Length by Algorithm (EXACT)
        df.boxplot(column='avg_plan_length', by='algorithm', ax=axes[0,1])
        axes[0,1].set_title('Plan Length by Algorithm (EXACT)')
        axes[0,1].set_xlabel('Algorithm')
        axes[0,1].set_ylabel('Plan Length (actions)')
        axes[0,1].tick_params(axis='x', rotation=45)
        
        # 3. Success Rate by Algorithm (EXACT)
        df.boxplot(column='success_rate', by='algorithm', ax=axes[0,2])
        axes[0,2].set_title('Success Rate by Algorithm (EXACT)')
        axes[0,2].set_xlabel('Algorithm')
        axes[0,2].set_ylabel('Success Rate')
        axes[0,2].tick_params(axis='x', rotation=45)
        
        # 4. Solve Time vs Plan Length (EXACT)
        for algorithm in df['algorithm'].unique():
            alg_data = df[df['algorithm'] == algorithm]
            axes[1,0].scatter(alg_data['avg_plan_length'], alg_data['avg_solve_time'], 
                            label=algorithm, alpha=0.7, s=60)
        axes[1,0].set_title('Solve Time vs Plan Length (EXACT)')
        axes[1,0].set_xlabel('Plan Length (actions)')
        axes[1,0].set_ylabel('Solve Time (s)')
        axes[1,0].legend()
        
        # 5. Problem Difficulty by Solve Time (EXACT)
        problem_difficulty = df.groupby('problem')['avg_solve_time'].mean().sort_values(ascending=False)
        problem_difficulty.plot(kind='bar', ax=axes[1,1])
        axes[1,1].set_title('Problem Difficulty by Solve Time (EXACT)')
        axes[1,1].set_xlabel('Problem')
        axes[1,1].set_ylabel('Average Solve Time (s)')
        axes[1,1].tick_params(axis='x', rotation=45)
        
        # 6. Algorithm Ranking by Solve Time (EXACT)
        algorithm_ranking = df.groupby('algorithm')['avg_solve_time'].mean().sort_values(ascending=True)
        algorithm_ranking.plot(kind='barh', ax=axes[1,2])
        axes[1,2].set_title('Algorithm Ranking by Solve Time (EXACT)')
        axes[1,2].set_xlabel('Average Solve Time (s)')
        axes[1,2].set_ylabel('Algorithm')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "exact_values_analysis.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Exact values plots saved to exact_values_analysis.png")


if __name__ == "__main__":
    experiment = ExactValuesAnalysis()
    experiment.run_exact_values_experiment()
