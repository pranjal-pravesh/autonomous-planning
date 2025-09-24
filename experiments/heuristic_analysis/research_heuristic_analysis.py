#!/usr/bin/env python3
"""
Research-Focused Heuristic Analysis Experiment

This experiment uses the proven working infrastructure from the existing
heuristic comparison experiment to conduct focused research on heuristic
quality and behavior.
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
from experiments.heuristics.heuristic_comparison import HeuristicExperiment


class ResearchHeuristicAnalysis(HeuristicExperiment):
    """Research-focused heuristic analysis extending the working experiment"""
    
    def __init__(self, output_dir: str = "experiments/heuristic_analysis/results"):
        # Initialize with fewer heuristics for focused analysis
        super().__init__(output_dir)
        
        # Focus on 3 most important heuristics for research
        self.fd_searches = [
            {"name": "gbfs_ff", "search": "gbfs(ff())", "description": "Fast Forward"},
            {"name": "gbfs_hadd", "search": "gbfs(hadd())", "description": "Additive Heuristic"},
            {"name": "gbfs_hmax", "search": "gbfs(hmax())", "description": "Max Heuristic"},
        ]
        
        # Use proven solvable problems
        self.test_problems = [
            {"name": "easy_4", "robots": 1, "docks": 3, "containers": 4, "piles": 3, "goal_type": "simple_swap"},
            {"name": "easy_6", "robots": 1, "docks": 4, "containers": 6, "piles": 4, "goal_type": "simple_swap"},
            {"name": "medium_8", "robots": 2, "docks": 4, "containers": 8, "piles": 4, "goal_type": "complex_redistribution"},
            {"name": "medium_10", "robots": 2, "docks": 5, "containers": 10, "piles": 5, "goal_type": "complex_redistribution"},
            {"name": "hard_14", "robots": 3, "docks": 6, "containers": 14, "piles": 6, "goal_type": "weight_constrained"},
        ]
        
        # Research-specific metrics
        self.research_metrics = []
    
    def analyze_heuristic_quality(self, problem_config: Dict, heuristic_config: Dict, 
                                solve_time: float, plan_length: int, success: bool) -> Dict[str, Any]:
        """Analyze heuristic quality for research purposes"""
        
        # Estimate initial heuristic value (simplified approach)
        initial_h_value = self.estimate_initial_heuristic(problem_config, heuristic_config)
        
        if success:
            actual_cost = plan_length
            
            # Calculate heuristic quality metrics
            final_h_value = 0  # At goal state
            
            # Admissibility ratio (heuristic should be <= actual cost)
            admissibility_ratio = initial_h_value / actual_cost if actual_cost > 0 else 0
            
            # Consistency (heuristic should be consistent)
            heuristic_consistency = abs(initial_h_value - final_h_value) / max(initial_h_value, 1)
            
            # Search efficiency
            search_efficiency = actual_cost / solve_time if solve_time > 0 else 0
            
            return {
                "success": True,
                "initial_h_value": initial_h_value,
                "final_h_value": final_h_value,
                "actual_cost": actual_cost,
                "plan_length": plan_length,
                "solve_time": solve_time,
                "admissibility_ratio": admissibility_ratio,
                "heuristic_consistency": heuristic_consistency,
                "search_efficiency": search_efficiency,
            }
        else:
            return {
                "success": False,
                "initial_h_value": initial_h_value,
                "final_h_value": 0,
                "actual_cost": float('inf'),
                "plan_length": 0,
                "solve_time": solve_time,
                "admissibility_ratio": 0,
                "heuristic_consistency": 0,
                "search_efficiency": 0,
            }
    
    def estimate_initial_heuristic(self, problem_config: Dict, heuristic_config: Dict) -> float:
        """Estimate initial heuristic value based on problem characteristics"""
        
        # Count unsatisfied goals as a rough heuristic estimate
        unsatisfied_goals = 2 if problem_config["goal_type"] == "simple_swap" else 4
        
        # Adjust based on problem complexity
        if heuristic_config["name"] == "gbfs_ff":
            return unsatisfied_goals * 1.2  # Fast Forward tends to be optimistic
        elif heuristic_config["name"] == "gbfs_hadd":
            return unsatisfied_goals * 1.0  # Additive is often more accurate
        elif heuristic_config["name"] == "gbfs_hmax":
            return unsatisfied_goals * 0.8  # Max is often pessimistic
        else:
            return unsatisfied_goals
    
    def run_research_experiment(self):
        """Run the research-focused heuristic analysis"""
        print("Starting Research-Focused Heuristic Analysis")
        print("=" * 60)
        
        # Run the base experiment
        self.run_all_experiments()
        
        # Add research-specific analysis
        self.analyze_heuristic_quality_research()
        self.create_research_visualizations()
        
        print(f"\nResearch experiment completed! Results saved to {self.output_dir}")
    
    def analyze_heuristic_quality_research(self):
        """Analyze heuristic quality from research perspective"""
        print("\nAnalyzing Heuristic Quality for Research...")
        
        # Load the results from the base experiment
        try:
            with open(os.path.join(self.output_dir, "raw_results.json"), 'r') as f:
                base_results = json.load(f)
        except FileNotFoundError:
            print("Base experiment results not found!")
            return
        
        # Analyze each result for research metrics
        research_data = []
        for result in base_results:
            # Get the problem and heuristic configs
            problem_config = result["problem"]
            heuristic_config = result["heuristic"]
            
            # Calculate average metrics across runs
            successful_runs = [run for run in result["runs"] if run["success"]]
            if successful_runs:
                avg_solve_time = sum(run["solve_time"] for run in successful_runs) / len(successful_runs)
                avg_plan_length = sum(run["plan_length"] for run in successful_runs) / len(successful_runs)
                success_rate = len(successful_runs) / len(result["runs"])
                
                # Analyze heuristic quality
                quality_metrics = self.analyze_heuristic_quality(
                    problem_config, heuristic_config,
                    avg_solve_time, avg_plan_length, True
                )
                
                # Store research data
                research_data.append({
                    "problem": result["problem"]["name"],
                    "heuristic": result["heuristic"]["name"],
                    "description": heuristic_config["description"],
                    "initial_h": quality_metrics["initial_h_value"],
                    "actual_cost": quality_metrics["actual_cost"],
                    "plan_length": quality_metrics["plan_length"],
                    "solve_time": quality_metrics["solve_time"],
                    "admissibility_ratio": quality_metrics["admissibility_ratio"],
                    "consistency": quality_metrics["heuristic_consistency"],
                    "search_efficiency": quality_metrics["search_efficiency"],
                    "success_rate": success_rate
                })
        
        if not research_data:
            print("No successful results to analyze!")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(research_data)
        
        # Research-specific analysis
        analysis = {
            "heuristic_quality_ranking": df.groupby('heuristic')['admissibility_ratio'].mean().sort_values(ascending=False).to_dict(),
            
            "heuristic_consistency_analysis": df.groupby('heuristic')['consistency'].agg(['mean', 'std', 'min', 'max']).round(4).to_dict(),
            
            "search_efficiency_ranking": df.groupby('heuristic')['search_efficiency'].mean().sort_values(ascending=False).to_dict(),
            
            "problem_difficulty_analysis": df.groupby('problem')['solve_time'].mean().sort_values(ascending=False).to_dict(),
            
            "heuristic_informedness": df.groupby('heuristic')['admissibility_ratio'].mean().to_dict(),
            
            "scaling_behavior": df.groupby(['problem', 'heuristic'])['solve_time'].mean().unstack().to_dict()
        }
        
        # Save research analysis
        with open(os.path.join(self.output_dir, "research_heuristic_analysis.json"), 'w') as f:
            json.dump(analysis, f, indent=2)
        
        # Save research data
        df.to_csv(os.path.join(self.output_dir, "research_heuristic_data.csv"), index=False)
        
        print("Research analysis saved to research_heuristic_analysis.json and research_heuristic_data.csv")
    
    def create_research_visualizations(self):
        """Create research-focused visualizations"""
        print("Creating research visualizations...")
        
        # Load research data
        try:
            df = pd.read_csv(os.path.join(self.output_dir, "research_heuristic_data.csv"))
        except FileNotFoundError:
            print("No research data to visualize!")
            return
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig = plt.figure(figsize=(18, 12))
        
        # 1. Heuristic Quality Comparison (Admissibility)
        plt.subplot(3, 3, 1)
        sns.boxplot(data=df, x='heuristic', y='admissibility_ratio')
        plt.title('Heuristic Admissibility Ratio\n(Lower is better, closer to 1.0)')
        plt.xticks(rotation=45)
        plt.axhline(y=1.0, color='red', linestyle='--', alpha=0.7, label='Perfect Admissibility')
        plt.legend()
        
        # 2. Heuristic Consistency
        plt.subplot(3, 3, 2)
        sns.boxplot(data=df, x='heuristic', y='consistency')
        plt.title('Heuristic Consistency\n(Lower is better)')
        plt.xticks(rotation=45)
        
        # 3. Search Efficiency
        plt.subplot(3, 3, 3)
        sns.boxplot(data=df, x='heuristic', y='search_efficiency')
        plt.title('Search Efficiency\n(Higher is better)')
        plt.xticks(rotation=45)
        
        # 4. Heuristic vs Actual Cost Scatter
        plt.subplot(3, 3, 4)
        for heuristic in df['heuristic'].unique():
            subset = df[df['heuristic'] == heuristic]
            plt.scatter(subset['initial_h'], subset['actual_cost'], label=heuristic, alpha=0.7)
        plt.plot([0, df['actual_cost'].max()], [0, df['actual_cost'].max()], 'r--', alpha=0.7, label='Perfect Heuristic')
        plt.xlabel('Initial Heuristic Value')
        plt.ylabel('Actual Cost')
        plt.title('Heuristic vs Actual Cost')
        plt.legend()
        
        # 5. Problem Difficulty Analysis
        plt.subplot(3, 3, 5)
        problem_difficulty = df.groupby('problem')['solve_time'].mean().sort_values(ascending=False)
        plt.bar(range(len(problem_difficulty)), problem_difficulty.values)
        plt.xticks(range(len(problem_difficulty)), problem_difficulty.index, rotation=45)
        plt.title('Problem Difficulty (by solve time)')
        plt.ylabel('Average Solve Time (s)')
        
        # 6. Heuristic Performance Heatmap
        plt.subplot(3, 3, 6)
        pivot_data = df.pivot_table(values='admissibility_ratio', index='problem', columns='heuristic', aggfunc='mean')
        sns.heatmap(pivot_data, annot=True, cmap='RdYlBu_r', center=1.0)
        plt.title('Heuristic Admissibility by Problem')
        
        # 7. Scaling Analysis
        plt.subplot(3, 3, 7)
        scaling_data = df.groupby(['problem', 'heuristic'])['solve_time'].mean().unstack()
        for heuristic in scaling_data.columns:
            plt.plot(range(len(scaling_data)), scaling_data[heuristic], marker='o', label=heuristic)
        plt.xticks(range(len(scaling_data)), scaling_data.index, rotation=45)
        plt.title('Scaling Analysis: Solve Time')
        plt.ylabel('Solve Time (s)')
        plt.yscale('log')
        plt.legend()
        
        # 8. Heuristic Ranking
        plt.subplot(3, 3, 8)
        ranking = df.groupby('heuristic')['admissibility_ratio'].mean().sort_values(ascending=True)
        plt.barh(range(len(ranking)), ranking.values)
        plt.yticks(range(len(ranking)), ranking.index)
        plt.xlabel('Average Admissibility Ratio')
        plt.title('Heuristic Ranking\n(Lower is better)')
        
        # 9. Search Efficiency vs Admissibility
        plt.subplot(3, 3, 9)
        sns.scatterplot(data=df, x='admissibility_ratio', y='search_efficiency', hue='heuristic')
        plt.xlabel('Admissibility Ratio')
        plt.ylabel('Search Efficiency')
        plt.title('Search Efficiency vs Admissibility')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "research_heuristic_analysis.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Research visualizations saved to research_heuristic_analysis.png")


if __name__ == "__main__":
    experiment = ResearchHeuristicAnalysis()
    experiment.run_research_experiment()
