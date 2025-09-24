#!/usr/bin/env python3
"""
Comprehensive Exact Statistics Analysis - Unified Planning Fast Downward Interface

This experiment captures ALL exact values available from UP's Fast Downward interface:
- Basic metrics (solve time, plan length, success rate)
- Detailed search statistics (nodes expanded, generated, evaluated)
- Memory usage statistics (peak memory, hash table info)
- Time breakdown (search time, total time, actual search time)
- Heuristic statistics (initial values, best values, evaluations)
- Problem characteristics (variables, facts, operators, task size)

All statistics are parsed from the log_messages attribute of PlanGenerationResult.
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

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import the working experiment class
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'heuristics_comparison'))
from heuristic_comparison import HeuristicExperiment


class ComprehensiveExactStatsAnalysis(HeuristicExperiment):
    """Analysis capturing ALL exact statistics from UP's Fast Downward interface"""
    
    def __init__(self, output_dir: str = "experiments/search_analysis/results"):
        # Initialize with search-focused algorithms
        super().__init__(output_dir)
        
        # Focus on different search algorithms for comprehensive analysis
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
    
    def parse_fast_downward_logs(self, log_messages: List) -> Dict[str, Any]:
        """Parse Fast Downward log messages to extract exact statistics"""
        if not log_messages:
            return {}
        
        # Combine all log messages into a single string
        log_text = ""
        for log_msg in log_messages:
            if hasattr(log_msg, 'message'):
                log_text += log_msg.message + "\n"
            else:
                log_text += str(log_msg) + "\n"
        
        stats = {}
        
        # Search Statistics (EXACT)
        expanded_match = re.search(r'Expanded (\d+) state\(s\)', log_text)
        if expanded_match:
            stats['nodes_expanded'] = int(expanded_match.group(1))
        
        generated_match = re.search(r'Generated (\d+) state\(s\)', log_text)
        if generated_match:
            stats['nodes_generated'] = int(generated_match.group(1))
        
        evaluated_match = re.search(r'Evaluated (\d+) state\(s\)', log_text)
        if evaluated_match:
            stats['nodes_evaluated'] = int(evaluated_match.group(1))
        
        evaluations_match = re.search(r'Evaluations: (\d+)', log_text)
        if evaluations_match:
            stats['heuristic_evaluations'] = int(evaluations_match.group(1))
        
        reopened_match = re.search(r'Reopened (\d+) state\(s\)', log_text)
        if reopened_match:
            stats['nodes_reopened'] = int(reopened_match.group(1))
        
        dead_ends_match = re.search(r'Dead ends: (\d+) state\(s\)', log_text)
        if dead_ends_match:
            stats['dead_ends'] = int(dead_ends_match.group(1))
        
        # Memory Statistics (EXACT)
        peak_memory_match = re.search(r'Peak memory: (\d+) KB', log_text)
        if peak_memory_match:
            stats['peak_memory_kb'] = int(peak_memory_match.group(1))
        
        bytes_per_state_match = re.search(r'Bytes per state: (\d+)', log_text)
        if bytes_per_state_match:
            stats['bytes_per_state'] = int(bytes_per_state_match.group(1))
        
        registered_states_match = re.search(r'Number of registered states: (\d+)', log_text)
        if registered_states_match:
            stats['registered_states'] = int(registered_states_match.group(1))
        
        load_factor_match = re.search(r'Int hash set load factor: (\d+)/(\d+) = ([\d.]+)', log_text)
        if load_factor_match:
            stats['hash_load_factor'] = float(load_factor_match.group(3))
            stats['hash_used_slots'] = int(load_factor_match.group(1))
            stats['hash_total_slots'] = int(load_factor_match.group(2))
        
        hash_resizes_match = re.search(r'Int hash set resizes: (\d+)', log_text)
        if hash_resizes_match:
            stats['hash_resizes'] = int(hash_resizes_match.group(1))
        
        # Time Statistics (EXACT)
        search_time_match = re.search(r'Search time: ([\d.]+)s', log_text)
        if search_time_match:
            stats['search_time_s'] = float(search_time_match.group(1))
        
        total_time_match = re.search(r'Total time: ([\d.]+)s', log_text)
        if total_time_match:
            stats['total_time_s'] = float(total_time_match.group(1))
        
        actual_search_time_match = re.search(r'Actual search time: ([\d.]+)s', log_text)
        if actual_search_time_match:
            stats['actual_search_time_s'] = float(actual_search_time_match.group(1))
        
        # Heuristic Statistics (EXACT)
        initial_h_matches = re.findall(r'Initial heuristic value for ([^:]+): (\d+)', log_text)
        if initial_h_matches:
            stats['initial_heuristic_values'] = {heuristic.strip(): int(value) for heuristic, value in initial_h_matches}
        
        best_h_matches = re.findall(r'New best heuristic value for ([^:]+): (\d+)', log_text)
        if best_h_matches:
            stats['best_heuristic_values'] = {heuristic.strip(): int(value) for heuristic, value in best_h_matches}
        
        # Problem Statistics (EXACT)
        variables_match = re.search(r'Variables: (\d+)', log_text)
        if variables_match:
            stats['variables'] = int(variables_match.group(1))
        
        fact_pairs_match = re.search(r'FactPairs: (\d+)', log_text)
        if fact_pairs_match:
            stats['fact_pairs'] = int(fact_pairs_match.group(1))
        
        translator_vars_match = re.search(r'Translator variables: (\d+)', log_text)
        if translator_vars_match:
            stats['translator_variables'] = int(translator_vars_match.group(1))
        
        translator_facts_match = re.search(r'Translator facts: (\d+)', log_text)
        if translator_facts_match:
            stats['translator_facts'] = int(translator_facts_match.group(1))
        
        translator_ops_match = re.search(r'Translator operators: (\d+)', log_text)
        if translator_ops_match:
            stats['translator_operators'] = int(translator_ops_match.group(1))
        
        task_size_match = re.search(r'Translator task size: (\d+)', log_text)
        if task_size_match:
            stats['task_size'] = int(task_size_match.group(1))
        
        # Plan Statistics (EXACT)
        plan_length_match = re.search(r'Plan length: (\d+) step\(s\)', log_text)
        if plan_length_match:
            stats['plan_length_steps'] = int(plan_length_match.group(1))
        
        plan_cost_match = re.search(r'Plan cost: (\d+)', log_text)
        if plan_cost_match:
            stats['plan_cost'] = int(plan_cost_match.group(1))
        
        # Search efficiency metrics
        if 'nodes_expanded' in stats and 'nodes_generated' in stats:
            stats['search_efficiency'] = stats['nodes_expanded'] / stats['nodes_generated'] if stats['nodes_generated'] > 0 else 0
        
        if 'nodes_expanded' in stats and 'nodes_evaluated' in stats:
            stats['evaluation_efficiency'] = stats['nodes_expanded'] / stats['nodes_evaluated'] if stats['nodes_evaluated'] > 0 else 0
        
        if 'nodes_generated' in stats and 'nodes_evaluated' in stats:
            stats['generation_efficiency'] = stats['nodes_generated'] / stats['nodes_evaluated'] if stats['nodes_evaluated'] > 0 else 0
        
        return stats
    
    def run_experiment_with_logs(self, problem_config: Dict, search_config: Dict, num_runs: int = 3) -> Dict:
        """Run experiment and capture log messages for detailed statistics"""
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
        
        # Calculate summary statistics
        successful_runs = [r for r in results["runs"] if r["success"]]
        if successful_runs:
            solve_times = [r["solve_time"] for r in successful_runs]
            plan_lengths = [r["plan_length"] for r in successful_runs]
            
            results["summary"] = {
                "success_rate": len(successful_runs) / num_runs,
                "avg_solve_time": sum(solve_times) / len(solve_times),
                "std_solve_time": np.std(solve_times) if len(solve_times) > 1 else 0,
                "avg_plan_length": sum(plan_lengths) / len(plan_lengths),
                "std_plan_length": np.std(plan_lengths) if len(plan_lengths) > 1 else 0,
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

    def run_comprehensive_experiment(self):
        """Run experiment capturing ALL exact statistics from UP's Fast Downward interface"""
        print("Starting COMPREHENSIVE EXACT STATISTICS Analysis")
        print("=" * 70)
        print("Capturing ALL exact values from UP's Fast Downward interface:")
        print("- Basic metrics (solve time, plan length, success rate)")
        print("- Search statistics (nodes expanded, generated, evaluated)")
        print("- Memory usage (peak memory, hash table info)")
        print("- Time breakdown (search time, total time, actual search time)")
        print("- Heuristic statistics (initial values, best values)")
        print("- Problem characteristics (variables, facts, operators)")
        print()
        
        # Create results directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        all_results = []
        
        for problem_config in self.test_problems:
            print(f"Testing problem: {problem_config['name']}")
            
            for search_config in self.fd_searches:
                print(f"  Testing {search_config['name']} ({search_config['description']})")
                
                # Run the experiment with log capture
                experiment_result = self.run_experiment_with_logs(problem_config, search_config, num_runs=3)
                
                # Extract basic exact values from the experiment result
                runs = []
                for run_data in experiment_result["runs"]:
                    # Parse detailed statistics from log messages
                    detailed_stats = self.parse_fast_downward_logs(run_data.get("log_messages", []))
                    
                    # Combine basic and detailed statistics
                    comprehensive_run_data = {
                        "run": run_data["run"] + 1,  # Convert to 1-based indexing
                        "success": run_data["success"],           # EXACT boolean
                        "solve_time": float(run_data["solve_time"]),     # EXACT wall-clock time
                        "plan_length": int(run_data["plan_length"]),     # EXACT number of actions
                        "error": run_data.get("status", None) if not run_data["success"] else None,
                        
                        # Add all parsed detailed statistics
                        **detailed_stats
                    }
                    runs.append(comprehensive_run_data)
                
                # Calculate comprehensive statistics
                successful_runs = [run for run in runs if run["success"]]
                if successful_runs:
                    # Basic statistics
                    avg_solve_time = sum(run["solve_time"] for run in successful_runs) / len(successful_runs)
                    avg_plan_length = sum(run["plan_length"] for run in successful_runs) / len(successful_runs)
                    success_rate = len(successful_runs) / len(runs)
                    
                    # Detailed statistics (average across successful runs)
                    detailed_stats = {}
                    for key in successful_runs[0].keys():
                        if key not in ["run", "success", "solve_time", "plan_length", "error"]:
                            values = [run[key] for run in successful_runs if key in run and run[key] is not None]
                            if values:
                                if isinstance(values[0], (int, float)):
                                    detailed_stats[f"avg_{key}"] = sum(values) / len(values)
                                    detailed_stats[f"min_{key}"] = min(values)
                                    detailed_stats[f"max_{key}"] = max(values)
                                else:
                                    detailed_stats[key] = values[0]  # Take first non-null value for non-numeric
                else:
                    avg_solve_time = 0.0
                    avg_plan_length = 0
                    success_rate = 0.0
                    detailed_stats = {}
                
                # Store comprehensive result
                result = {
                    "problem": problem_config,
                    "search": search_config,
                    "runs": runs,
                    "basic_statistics": {
                        "success_rate": success_rate,        # EXACT (calculated from exact booleans)
                        "avg_solve_time": avg_solve_time,    # EXACT (average of exact times)
                        "avg_plan_length": avg_plan_length,  # EXACT (average of exact lengths)
                        "total_runs": len(runs),             # EXACT count
                        "successful_runs": len(successful_runs)  # EXACT count
                    },
                    "detailed_statistics": detailed_stats,
                    "timestamp": time.time()
                }
                all_results.append(result)
                
                # Print comprehensive results
                if successful_runs:
                    print(f"    ✅ Success: {len(successful_runs)}/{len(runs)} runs")
                    print(f"       Basic: avg time: {avg_solve_time:.3f}s, avg plan: {avg_plan_length:.1f} actions")
                    if 'avg_nodes_expanded' in detailed_stats:
                        print(f"       Search: {detailed_stats['avg_nodes_expanded']:.1f} expanded, {detailed_stats['avg_nodes_generated']:.1f} generated")
                    if 'avg_peak_memory_kb' in detailed_stats:
                        print(f"       Memory: {detailed_stats['avg_peak_memory_kb']:.0f} KB peak")
                else:
                    print(f"    ❌ Failed: {len(successful_runs)}/{len(runs)} runs")
        
        # Save comprehensive results
        with open(os.path.join(self.output_dir, "comprehensive_exact_results.json"), 'w') as f:
            json.dump(all_results, f, indent=2)
        
        # Create comprehensive analysis and visualizations
        self.analyze_comprehensive_stats(all_results)
        self.create_comprehensive_plots(all_results)
        
        print(f"\nCOMPREHENSIVE EXACT STATISTICS experiment completed! Results saved to {self.output_dir}")
    
    def analyze_comprehensive_stats(self, results: List[Dict]):
        """Analyze comprehensive exact statistics"""
        print("\nAnalyzing COMPREHENSIVE EXACT STATISTICS...")
        
        # Extract comprehensive data
        comprehensive_data = []
        for result in results:
            if result["basic_statistics"]["success_rate"] > 0:
                data_row = {
                    "problem": result["problem"]["name"],
                    "algorithm": result["search"]["name"],
                    "description": result["search"]["description"],
                    
                    # Basic statistics
                    "success_rate": result["basic_statistics"]["success_rate"],
                    "avg_solve_time": result["basic_statistics"]["avg_solve_time"],
                    "avg_plan_length": result["basic_statistics"]["avg_plan_length"],
                    "total_runs": result["basic_statistics"]["total_runs"],
                    "successful_runs": result["basic_statistics"]["successful_runs"],
                    
                    # Detailed statistics
                    **result["detailed_statistics"]
                }
                comprehensive_data.append(data_row)
        
        if not comprehensive_data:
            print("No successful results to analyze")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(comprehensive_data)
        
        # Create comprehensive analysis
        analysis = {
            "total_experiments": len(results),
            "successful_experiments": len(comprehensive_data),
            "overall_success_rate": len(comprehensive_data) / len(results) if results else 0,
            
            "basic_algorithm_performance": {
                "solve_time": df.groupby('algorithm')['avg_solve_time'].agg(['mean', 'std', 'min', 'max']).round(4).to_dict(),
                "plan_length": df.groupby('algorithm')['avg_plan_length'].agg(['mean', 'std', 'min', 'max']).round(1).to_dict(),
                "success_rate": df.groupby('algorithm')['success_rate'].agg(['mean', 'std', 'min', 'max']).round(3).to_dict(),
            },
            
            "search_efficiency_analysis": {},
            "memory_usage_analysis": {},
            "heuristic_analysis": {},
            "problem_difficulty_analysis": {}
        }
        
        # Search efficiency analysis
        if 'avg_nodes_expanded' in df.columns:
            analysis["search_efficiency_analysis"] = {
                "nodes_expanded": df.groupby('algorithm')['avg_nodes_expanded'].agg(['mean', 'std', 'min', 'max']).round(1).to_dict(),
                "nodes_generated": df.groupby('algorithm')['avg_nodes_generated'].agg(['mean', 'std', 'min', 'max']).round(1).to_dict(),
                "nodes_evaluated": df.groupby('algorithm')['avg_nodes_evaluated'].agg(['mean', 'std', 'min', 'max']).round(1).to_dict(),
                "search_efficiency": df.groupby('algorithm')['avg_search_efficiency'].agg(['mean', 'std', 'min', 'max']).round(3).to_dict() if 'avg_search_efficiency' in df.columns else {}
            }
        
        # Memory usage analysis
        if 'avg_peak_memory_kb' in df.columns:
            analysis["memory_usage_analysis"] = {
                "peak_memory_kb": df.groupby('algorithm')['avg_peak_memory_kb'].agg(['mean', 'std', 'min', 'max']).round(0).to_dict(),
                "bytes_per_state": df.groupby('algorithm')['avg_bytes_per_state'].agg(['mean', 'std', 'min', 'max']).round(0).to_dict() if 'avg_bytes_per_state' in df.columns else {}
            }
        
        # Problem difficulty analysis
        analysis["problem_difficulty_analysis"] = {
            "by_solve_time": df.groupby('problem')['avg_solve_time'].mean().sort_values(ascending=False).to_dict(),
            "by_nodes_expanded": df.groupby('problem')['avg_nodes_expanded'].mean().sort_values(ascending=False).to_dict() if 'avg_nodes_expanded' in df.columns else {},
            "by_memory_usage": df.groupby('problem')['avg_peak_memory_kb'].mean().sort_values(ascending=False).to_dict() if 'avg_peak_memory_kb' in df.columns else {}
        }
        
        # Algorithm ranking
        analysis["algorithm_ranking"] = {
            "by_solve_time": df.groupby('algorithm')['avg_solve_time'].mean().sort_values(ascending=True).to_dict(),
            "by_search_efficiency": df.groupby('algorithm')['avg_search_efficiency'].mean().sort_values(ascending=False).to_dict() if 'avg_search_efficiency' in df.columns else {},
            "by_memory_efficiency": df.groupby('algorithm')['avg_peak_memory_kb'].mean().sort_values(ascending=True).to_dict() if 'avg_peak_memory_kb' in df.columns else {}
        }
        
        # Save comprehensive analysis
        with open(os.path.join(self.output_dir, "comprehensive_exact_analysis.json"), 'w') as f:
            json.dump(analysis, f, indent=2)
        
        # Save comprehensive data
        df.to_csv(os.path.join(self.output_dir, "comprehensive_exact_data.csv"), index=False)
        
        print("Comprehensive analysis saved to comprehensive_exact_analysis.json and comprehensive_exact_data.csv")
    
    def create_comprehensive_plots(self, results: List[Dict]):
        """Create comprehensive plots using ALL exact statistics"""
        print("Creating COMPREHENSIVE EXACT STATISTICS plots...")
        
        # Extract comprehensive data
        comprehensive_data = []
        for result in results:
            if result["basic_statistics"]["success_rate"] > 0:
                data_row = {
                    "problem": result["problem"]["name"],
                    "algorithm": result["search"]["name"],
                    "description": result["search"]["description"],
                    
                    # Basic statistics
                    "success_rate": result["basic_statistics"]["success_rate"],
                    "avg_solve_time": result["basic_statistics"]["avg_solve_time"],
                    "avg_plan_length": result["basic_statistics"]["avg_plan_length"],
                    
                    # Detailed statistics
                    **result["detailed_statistics"]
                }
                comprehensive_data.append(data_row)
        
        if not comprehensive_data:
            print("No successful results to plot")
            return
        
        df = pd.DataFrame(comprehensive_data)
        
        # Create comprehensive visualization
        fig, axes = plt.subplots(3, 3, figsize=(20, 18))
        fig.suptitle('COMPREHENSIVE EXACT STATISTICS - Unified Planning Fast Downward Interface', fontsize=16, fontweight='bold')
        
        # Define colors for box plots
        colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow', 'lightpink', 'lightgray']
        
        # 1. Solve Time by Algorithm (EXACT)
        df.boxplot(column='avg_solve_time', by='algorithm', ax=axes[0,0], patch_artist=True)
        # Color the boxes
        for patch, color in zip(axes[0,0].artists, colors):
            patch.set_facecolor(color)
        axes[0,0].set_title('Solve Time by Algorithm (EXACT)')
        axes[0,0].set_xlabel('Algorithm')
        axes[0,0].set_ylabel('Solve Time (s)')
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # 2. Plan Length by Algorithm (EXACT)
        df.boxplot(column='avg_plan_length', by='algorithm', ax=axes[0,1], patch_artist=True)
        # Color the boxes
        for patch, color in zip(axes[0,1].artists, colors):
            patch.set_facecolor(color)
        axes[0,1].set_title('Plan Length by Algorithm (EXACT)')
        axes[0,1].set_xlabel('Algorithm')
        axes[0,1].set_ylabel('Plan Length (actions)')
        axes[0,1].tick_params(axis='x', rotation=45)
        # Fix overlapping text by adjusting layout
        axes[0,1].tick_params(axis='x', labelsize=8)
        
        # 3. Nodes Expanded by Algorithm (EXACT)
        if 'avg_nodes_expanded' in df.columns:
            df.boxplot(column='avg_nodes_expanded', by='algorithm', ax=axes[0,2], patch_artist=True)
            # Color the boxes
            for patch, color in zip(axes[0,2].artists, colors):
                patch.set_facecolor(color)
            axes[0,2].set_title('Nodes Expanded by Algorithm (EXACT)')
            axes[0,2].set_xlabel('Algorithm')
            axes[0,2].set_ylabel('Nodes Expanded')
            axes[0,2].tick_params(axis='x', rotation=45)
        else:
            axes[0,2].text(0.5, 0.5, 'Nodes Expanded\nData Not Available', ha='center', va='center', transform=axes[0,2].transAxes)
            axes[0,2].set_title('Nodes Expanded by Algorithm (EXACT)')
        
        # 4. Search Efficiency (EXACT)
        if 'avg_search_efficiency' in df.columns:
            df.boxplot(column='avg_search_efficiency', by='algorithm', ax=axes[1,0], patch_artist=True)
            # Color the boxes
            for patch, color in zip(axes[1,0].artists, colors):
                patch.set_facecolor(color)
            axes[1,0].set_title('Search Efficiency by Algorithm (EXACT)')
            axes[1,0].set_xlabel('Algorithm')
            axes[1,0].set_ylabel('Search Efficiency (expanded/generated)')
            axes[1,0].tick_params(axis='x', rotation=45)
        else:
            axes[1,0].text(0.5, 0.5, 'Search Efficiency\nData Not Available', ha='center', va='center', transform=axes[1,0].transAxes)
            axes[1,0].set_title('Search Efficiency by Algorithm (EXACT)')
        
        # 5. Memory Usage by Algorithm (EXACT)
        if 'avg_peak_memory_kb' in df.columns:
            df.boxplot(column='avg_peak_memory_kb', by='algorithm', ax=axes[1,1], patch_artist=True)
            # Color the boxes
            for patch, color in zip(axes[1,1].artists, colors):
                patch.set_facecolor(color)
            axes[1,1].set_title('Peak Memory by Algorithm (EXACT)')
            axes[1,1].set_xlabel('Algorithm')
            axes[1,1].set_ylabel('Peak Memory (KB)')
            axes[1,1].tick_params(axis='x', rotation=45)
        else:
            axes[1,1].text(0.5, 0.5, 'Memory Usage\nData Not Available', ha='center', va='center', transform=axes[1,1].transAxes)
            axes[1,1].set_title('Peak Memory by Algorithm (EXACT)')
        
        # 6. Problem Difficulty by Solve Time (EXACT)
        problem_difficulty = df.groupby('problem')['avg_solve_time'].mean().sort_values(ascending=False)
        problem_difficulty.plot(kind='bar', ax=axes[1,2])
        axes[1,2].set_title('Problem Difficulty by Solve Time (EXACT)')
        axes[1,2].set_xlabel('Problem')
        axes[1,2].set_ylabel('Average Solve Time (s)')
        axes[1,2].tick_params(axis='x', rotation=45)
        
        # 7. Algorithm Ranking by Solve Time (EXACT)
        algorithm_ranking = df.groupby('algorithm')['avg_solve_time'].mean().sort_values(ascending=True)
        algorithm_ranking.plot(kind='barh', ax=axes[2,0])
        axes[2,0].set_title('Algorithm Ranking by Solve Time (EXACT)')
        axes[2,0].set_xlabel('Average Solve Time (s)')
        axes[2,0].set_ylabel('Algorithm')
        
        # 8. Search Efficiency vs Solve Time (EXACT)
        if 'avg_search_efficiency' in df.columns:
            for algorithm in df['algorithm'].unique():
                alg_data = df[df['algorithm'] == algorithm]
                axes[2,1].scatter(alg_data['avg_search_efficiency'], alg_data['avg_solve_time'], 
                                label=algorithm, alpha=0.7, s=60)
            axes[2,1].set_title('Search Efficiency vs Solve Time (EXACT)')
            axes[2,1].set_xlabel('Search Efficiency (expanded/generated)')
            axes[2,1].set_ylabel('Solve Time (s)')
            axes[2,1].legend()
        else:
            axes[2,1].text(0.5, 0.5, 'Search Efficiency vs Solve Time\nData Not Available', ha='center', va='center', transform=axes[2,1].transAxes)
            axes[2,1].set_title('Search Efficiency vs Solve Time (EXACT)')
        
        # 9. Memory Usage vs Problem Size (EXACT)
        if 'avg_peak_memory_kb' in df.columns:
            for algorithm in df['algorithm'].unique():
                alg_data = df[df['algorithm'] == algorithm]
                axes[2,2].scatter(alg_data['avg_plan_length'], alg_data['avg_peak_memory_kb'], 
                                label=algorithm, alpha=0.7, s=60)
            axes[2,2].set_title('Memory Usage vs Plan Length (EXACT)')
            axes[2,2].set_xlabel('Plan Length (actions)')
            axes[2,2].set_ylabel('Peak Memory (KB)')
            axes[2,2].legend()
        else:
            axes[2,2].text(0.5, 0.5, 'Memory Usage vs Plan Length\nData Not Available', ha='center', va='center', transform=axes[2,2].transAxes)
            axes[2,2].set_title('Memory Usage vs Plan Length (EXACT)')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "comprehensive_exact_analysis.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Comprehensive exact statistics plots saved to comprehensive_exact_analysis.png")


if __name__ == "__main__":
    experiment = ComprehensiveExactStatsAnalysis()
    experiment.run_comprehensive_experiment()
