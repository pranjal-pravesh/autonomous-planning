#!/usr/bin/env python3
"""
Search Trajectory Analysis - Advanced Search Behavior Visualization

This creates specialized plots that show the "trajectory" of search algorithms
through the search space, revealing fascinating patterns in how different
algorithms explore and converge to solutions.
"""

import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


class SearchTrajectoryAnalysis:
    """Advanced search trajectory visualization"""
    
    def __init__(self, results_dir: str = "experiments/search_analysis/results"):
        self.results_dir = results_dir
    
    def load_timeline_data(self) -> List[Dict]:
        """Load the timeline data from the during-search analysis"""
        timeline_file = os.path.join(self.results_dir, "during_search_timeline.json")
        if not os.path.exists(timeline_file):
            print(f"Timeline file not found: {timeline_file}")
            return []
        
        with open(timeline_file, 'r') as f:
            return json.load(f)
    
    def create_search_trajectory_plots(self):
        """Create advanced search trajectory visualizations"""
        print("Creating SEARCH TRAJECTORY visualizations...")
        
        timeline_data = self.load_timeline_data()
        if not timeline_data:
            print("No timeline data available")
            return
        
        # Create multiple specialized trajectory plots
        self.create_phase_space_plots(timeline_data)
        self.create_convergence_plots(timeline_data)
        self.create_efficiency_landscape_plots(timeline_data)
        self.create_algorithm_signature_plots(timeline_data)
        
        print("Search trajectory visualizations completed!")
    
    def create_phase_space_plots(self, timeline_data: List[Dict]):
        """Create phase space plots showing search dynamics"""
        print("Creating phase space plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Search Phase Space Analysis - Algorithm Dynamics', fontsize=14, fontweight='bold')
        
        colors = {
            'gbfs_ff': 'lightblue',
            'gbfs_hadd': 'lightgreen', 
            'astar_ff': 'lightcoral',
            'astar_hadd': 'lightyellow'
        }
        
        # 1. Nodes Generated vs Nodes Expanded (Phase Space)
        ax1 = axes[0, 0]
        for data in timeline_data:
            if data['nodes_generated'] and data['nodes_expanded']:
                # Create trajectory with arrows showing direction
                x = data['nodes_generated']
                y = data['nodes_expanded']
                
                ax1.plot(x, y, color=colors.get(data['algorithm'], 'gray'), 
                        linewidth=2, alpha=0.7, 
                        label=f"{data['algorithm']} ({data['problem']})")
                
                # Add arrows to show direction
                if len(x) > 1:
                    for i in range(0, len(x)-1, max(1, len(x)//10)):
                        dx = x[i+1] - x[i]
                        dy = y[i+1] - y[i]
                        ax1.arrow(x[i], y[i], dx*0.1, dy*0.1, 
                                head_width=0.5, head_length=0.3, 
                                fc=colors.get(data['algorithm'], 'gray'), 
                                ec=colors.get(data['algorithm'], 'gray'), alpha=0.6)
        
        ax1.set_title('Search Phase Space: Generated vs Expanded')
        ax1.set_xlabel('Nodes Generated')
        ax1.set_ylabel('Nodes Expanded')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Memory vs Time (Resource Usage Trajectory)
        ax2 = axes[0, 1]
        for data in timeline_data:
            if data['search_time'] and data['memory_usage']:
                ax2.plot(data['search_time'], data['memory_usage'], 
                        color=colors.get(data['algorithm'], 'gray'), 
                        linewidth=2, alpha=0.7,
                        label=f"{data['algorithm']} ({data['problem']})")
                
                # Fill area under curve to show memory accumulation
                ax2.fill_between(data['search_time'], data['memory_usage'], 
                               alpha=0.2, color=colors.get(data['algorithm'], 'gray'))
        
        ax2.set_title('Memory Usage Trajectory')
        ax2.set_xlabel('Search Time (s)')
        ax2.set_ylabel('Memory Usage (KB)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Efficiency vs Progress (Search Quality Trajectory)
        ax3 = axes[1, 0]
        for data in timeline_data:
            if data['search_efficiency'] and data['nodes_expanded']:
                ax3.plot(data['nodes_expanded'], data['search_efficiency'], 
                        color=colors.get(data['algorithm'], 'gray'), 
                        linewidth=2, alpha=0.7,
                        label=f"{data['algorithm']} ({data['problem']})")
                
                # Add markers at key points
                if len(data['search_efficiency']) > 0:
                    ax3.scatter(data['nodes_expanded'][-1], data['search_efficiency'][-1], 
                              color=colors.get(data['algorithm'], 'gray'), 
                              s=100, marker='*', edgecolor='black', linewidth=1)
        
        ax3.set_title('Search Quality Trajectory')
        ax3.set_xlabel('Nodes Expanded (Progress)')
        ax3.set_ylabel('Search Efficiency')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 3D-like trajectory (Time, Generated, Expanded)
        ax4 = axes[1, 1]
        for data in timeline_data:
            if data['search_time'] and data['nodes_generated'] and data['nodes_expanded']:
                # Create a 3D-like effect using color gradient
                times = np.array(data['search_time'])
                generated = np.array(data['nodes_generated'])
                expanded = np.array(data['nodes_expanded'])
                
                # Normalize time for color mapping
                norm_times = (times - times.min()) / (times.max() - times.min() + 1e-6)
                
                # Plot with color gradient
                for i in range(len(times)-1):
                    ax4.plot(generated[i:i+2], expanded[i:i+2], 
                            color=colors.get(data['algorithm'], 'gray'), 
                            alpha=0.3 + 0.7*norm_times[i], linewidth=3)
                
                # Add start and end markers
                ax4.scatter(generated[0], expanded[0], 
                          color=colors.get(data['algorithm'], 'gray'), 
                          s=100, marker='o', edgecolor='black', linewidth=2, label=f"{data['algorithm']} start")
                ax4.scatter(generated[-1], expanded[-1], 
                          color=colors.get(data['algorithm'], 'gray'), 
                          s=100, marker='s', edgecolor='black', linewidth=2, label=f"{data['algorithm']} end")
        
        ax4.set_title('Search Trajectory with Time Gradient')
        ax4.set_xlabel('Nodes Generated')
        ax4.set_ylabel('Nodes Expanded')
        ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, "search_phase_space.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Phase space plots saved to search_phase_space.png")
    
    def create_convergence_plots(self, timeline_data: List[Dict]):
        """Create plots showing how algorithms converge to solutions"""
        print("Creating convergence plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Algorithm Convergence Analysis', fontsize=14, fontweight='bold')
        
        colors = {
            'gbfs_ff': 'lightblue',
            'gbfs_hadd': 'lightgreen', 
            'astar_ff': 'lightcoral',
            'astar_hadd': 'lightyellow'
        }
        
        # 1. Convergence Rate Analysis
        ax1 = axes[0, 0]
        for data in timeline_data:
            if data['search_time'] and data['nodes_expanded']:
                # Calculate convergence rate (nodes expanded per unit time)
                times = np.array(data['search_time'])
                nodes = np.array(data['nodes_expanded'])
                
                if len(times) > 1:
                    # Calculate instantaneous rate
                    time_diffs = np.diff(times)
                    node_diffs = np.diff(nodes)
                    rates = node_diffs / (time_diffs + 1e-6)
                    
                    ax1.plot(times[1:], rates, 
                            color=colors.get(data['algorithm'], 'gray'), 
                            linewidth=2, alpha=0.7,
                            label=f"{data['algorithm']} ({data['problem']})")
        
        ax1.set_title('Convergence Rate Over Time')
        ax1.set_xlabel('Search Time (s)')
        ax1.set_ylabel('Nodes Expanded per Second')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Search Progress Curves
        ax2 = axes[0, 1]
        for data in timeline_data:
            if data['search_time'] and data['nodes_expanded']:
                # Normalize progress to 0-1 scale
                times = np.array(data['search_time'])
                nodes = np.array(data['nodes_expanded'])
                
                norm_times = times / times[-1] if times[-1] > 0 else times
                norm_nodes = nodes / nodes[-1] if nodes[-1] > 0 else nodes
                
                ax2.plot(norm_times, norm_nodes, 
                        color=colors.get(data['algorithm'], 'gray'), 
                        linewidth=2, alpha=0.7,
                        label=f"{data['algorithm']} ({data['problem']})")
        
        ax2.set_title('Normalized Search Progress')
        ax2.set_xlabel('Normalized Time')
        ax2.set_ylabel('Normalized Progress')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Efficiency Convergence
        ax3 = axes[1, 0]
        for data in timeline_data:
            if data['search_efficiency'] and data['nodes_expanded']:
                # Show how efficiency changes as search progresses
                ax3.plot(data['nodes_expanded'], data['search_efficiency'], 
                        color=colors.get(data['algorithm'], 'gray'), 
                        linewidth=2, alpha=0.7,
                        label=f"{data['algorithm']} ({data['problem']})")
                
                # Add trend line
                if len(data['search_efficiency']) > 2:
                    z = np.polyfit(data['nodes_expanded'], data['search_efficiency'], 1)
                    p = np.poly1d(z)
                    ax3.plot(data['nodes_expanded'], p(data['nodes_expanded']), 
                            color=colors.get(data['algorithm'], 'gray'), 
                            linestyle='--', alpha=0.5)
        
        ax3.set_title('Efficiency Convergence')
        ax3.set_xlabel('Nodes Expanded')
        ax3.set_ylabel('Search Efficiency')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Algorithm Comparison - Final Performance
        ax4 = axes[1, 1]
        algorithms = list(set([data['algorithm'] for data in timeline_data]))
        problems = list(set([data['problem'] for data in timeline_data]))
        
        # Create performance comparison
        performance_data = []
        algorithm_labels = []
        problem_labels = []
        
        for alg in algorithms:
            for problem in problems:
                alg_data = [data for data in timeline_data if data['algorithm'] == alg and data['problem'] == problem]
                if alg_data:
                    data = alg_data[0]
                    performance_data.append(data['total_solve_time'])
                    algorithm_labels.append(alg)
                    problem_labels.append(problem)
        
        # Create grouped bar chart
        x = np.arange(len(problems))
        width = 0.2
        
        for i, alg in enumerate(algorithms):
            alg_performance = []
            for problem in problems:
                alg_data = [data for data in timeline_data if data['algorithm'] == alg and data['problem'] == problem]
                if alg_data:
                    alg_performance.append(alg_data[0]['total_solve_time'])
                else:
                    alg_performance.append(0)
            
            ax4.bar(x + i*width, alg_performance, width, 
                   label=alg, color=colors.get(alg, 'gray'), alpha=0.8)
        
        ax4.set_title('Final Performance Comparison')
        ax4.set_xlabel('Problem')
        ax4.set_ylabel('Solve Time (s)')
        ax4.set_xticks(x + width * (len(algorithms)-1) / 2)
        ax4.set_xticklabels(problems)
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, "convergence_analysis.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Convergence plots saved to convergence_analysis.png")
    
    def create_efficiency_landscape_plots(self, timeline_data: List[Dict]):
        """Create plots showing the efficiency landscape of search"""
        print("Creating efficiency landscape plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Search Efficiency Landscape Analysis', fontsize=14, fontweight='bold')
        
        colors = {
            'gbfs_ff': 'lightblue',
            'gbfs_hadd': 'lightgreen', 
            'astar_ff': 'lightcoral',
            'astar_hadd': 'lightyellow'
        }
        
        # 1. Efficiency Heatmap
        ax1 = axes[0, 0]
        algorithms = list(set([data['algorithm'] for data in timeline_data]))
        problems = list(set([data['problem'] for data in timeline_data]))
        
        efficiency_matrix = np.zeros((len(algorithms), len(problems)))
        for i, alg in enumerate(algorithms):
            for j, problem in enumerate(problems):
                alg_data = [data for data in timeline_data if data['algorithm'] == alg and data['problem'] == problem]
                if alg_data and alg_data[0]['search_efficiency']:
                    efficiency_matrix[i, j] = np.mean(alg_data[0]['search_efficiency'])
        
        im = ax1.imshow(efficiency_matrix, cmap='RdYlGn', aspect='auto')
        ax1.set_xticks(range(len(problems)))
        ax1.set_yticks(range(len(algorithms)))
        ax1.set_xticklabels(problems)
        ax1.set_yticklabels(algorithms)
        ax1.set_title('Search Efficiency Heatmap')
        
        # Add text annotations
        for i in range(len(algorithms)):
            for j in range(len(problems)):
                text = ax1.text(j, i, f'{efficiency_matrix[i, j]:.3f}',
                               ha="center", va="center", color="black", fontweight='bold')
        
        plt.colorbar(im, ax=ax1)
        
        # 2. Efficiency Distribution
        ax2 = axes[0, 1]
        efficiency_by_algorithm = {}
        for data in timeline_data:
            if data['search_efficiency']:
                alg = data['algorithm']
                if alg not in efficiency_by_algorithm:
                    efficiency_by_algorithm[alg] = []
                efficiency_by_algorithm[alg].extend(data['search_efficiency'])
        
        # Create violin plot
        efficiency_data = [efficiency_by_algorithm[alg] for alg in algorithms if alg in efficiency_by_algorithm]
        algorithm_labels = [alg for alg in algorithms if alg in efficiency_by_algorithm]
        
        if efficiency_data:
            parts = ax2.violinplot(efficiency_data, positions=range(len(algorithm_labels)), 
                                  showmeans=True, showmedians=True)
            
            # Color the violins
            for i, pc in enumerate(parts['bodies']):
                pc.set_facecolor(colors.get(algorithm_labels[i], 'gray'))
                pc.set_alpha(0.7)
        
        ax2.set_xticks(range(len(algorithm_labels)))
        ax2.set_xticklabels(algorithm_labels)
        ax2.set_title('Search Efficiency Distribution')
        ax2.set_ylabel('Search Efficiency')
        ax2.grid(True, alpha=0.3)
        
        # 3. Efficiency vs Problem Size
        ax3 = axes[1, 0]
        problem_sizes = {'easy_4': 4, 'medium_8': 8, 'hard_14': 14}
        
        for data in timeline_data:
            if data['search_efficiency'] and data['problem'] in problem_sizes:
                size = problem_sizes[data['problem']]
                avg_efficiency = np.mean(data['search_efficiency'])
                ax3.scatter(size, avg_efficiency, 
                           color=colors.get(data['algorithm'], 'gray'), 
                           s=100, alpha=0.7, label=f"{data['algorithm']}")
        
        ax3.set_title('Efficiency vs Problem Size')
        ax3.set_xlabel('Problem Size (containers)')
        ax3.set_ylabel('Average Search Efficiency')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Efficiency Trend Analysis
        ax4 = axes[1, 1]
        for data in timeline_data:
            if data['search_efficiency'] and len(data['search_efficiency']) > 1:
                # Calculate efficiency trend
                efficiency = np.array(data['search_efficiency'])
                x = np.arange(len(efficiency))
                
                # Fit trend line
                z = np.polyfit(x, efficiency, 1)
                trend = np.poly1d(z)
                
                ax4.plot(x, efficiency, 
                        color=colors.get(data['algorithm'], 'gray'), 
                        alpha=0.5, linewidth=1)
                ax4.plot(x, trend(x), 
                        color=colors.get(data['algorithm'], 'gray'), 
                        linewidth=3, alpha=0.8,
                        label=f"{data['algorithm']} ({data['problem']})")
        
        ax4.set_title('Search Efficiency Trends')
        ax4.set_xlabel('Search Progress (timeline points)')
        ax4.set_ylabel('Search Efficiency')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, "efficiency_landscape.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Efficiency landscape plots saved to efficiency_landscape.png")
    
    def create_algorithm_signature_plots(self, timeline_data: List[Dict]):
        """Create plots showing unique 'signatures' of each algorithm"""
        print("Creating algorithm signature plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Algorithm Signatures - Unique Behavioral Patterns', fontsize=14, fontweight='bold')
        
        colors = {
            'gbfs_ff': 'lightblue',
            'gbfs_hadd': 'lightgreen', 
            'astar_ff': 'lightcoral',
            'astar_hadd': 'lightyellow'
        }
        
        # 1. Algorithm Fingerprints (Radar-like plots)
        ax1 = axes[0, 0]
        
        # Calculate signature metrics for each algorithm
        signature_metrics = {}
        for data in timeline_data:
            alg = data['algorithm']
            if alg not in signature_metrics:
                signature_metrics[alg] = {
                    'avg_efficiency': [],
                    'max_memory': [],
                    'solve_time': [],
                    'plan_length': []
                }
            
            if data['search_efficiency']:
                signature_metrics[alg]['avg_efficiency'].append(np.mean(data['search_efficiency']))
            if data['memory_usage']:
                signature_metrics[alg]['max_memory'].append(max(data['memory_usage']))
            signature_metrics[alg]['solve_time'].append(data['total_solve_time'])
            signature_metrics[alg]['plan_length'].append(data['plan_length'])
        
        # Create signature comparison
        metrics = ['avg_efficiency', 'max_memory', 'solve_time', 'plan_length']
        metric_labels = ['Avg Efficiency', 'Max Memory', 'Solve Time', 'Plan Length']
        
        x = np.arange(len(metrics))
        width = 0.2
        
        for i, alg in enumerate(signature_metrics.keys()):
            values = []
            for metric in metrics:
                if signature_metrics[alg][metric]:
                    # Normalize values for comparison
                    val = np.mean(signature_metrics[alg][metric])
                    if metric == 'solve_time':
                        val = 1 / (val + 1e-6)  # Invert so higher is better
                    elif metric == 'max_memory':
                        val = 1 / (val + 1e-6)  # Invert so higher is better
                    values.append(val)
                else:
                    values.append(0)
            
            # Normalize values to 0-1 scale
            if values:
                max_val = max(values)
                if max_val > 0:
                    values = [v/max_val for v in values]
            
            ax1.bar(x + i*width, values, width, 
                   label=alg, color=colors.get(alg, 'gray'), alpha=0.8)
        
        ax1.set_title('Algorithm Signatures (Normalized)')
        ax1.set_xlabel('Metrics')
        ax1.set_ylabel('Normalized Performance')
        ax1.set_xticks(x + width * (len(signature_metrics)-1) / 2)
        ax1.set_xticklabels(metric_labels, rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Search Pattern Recognition
        ax2 = axes[0, 1]
        for data in timeline_data:
            if data['search_time'] and data['nodes_expanded']:
                # Create a "search pattern" by plotting normalized curves
                times = np.array(data['search_time'])
                nodes = np.array(data['nodes_expanded'])
                
                # Normalize to 0-1 scale
                norm_times = (times - times.min()) / (times.max() - times.min() + 1e-6)
                norm_nodes = (nodes - nodes.min()) / (nodes.max() - nodes.min() + 1e-6)
                
                ax2.plot(norm_times, norm_nodes, 
                        color=colors.get(data['algorithm'], 'gray'), 
                        linewidth=2, alpha=0.7,
                        label=f"{data['algorithm']} ({data['problem']})")
        
        ax2.set_title('Search Pattern Recognition')
        ax2.set_xlabel('Normalized Time')
        ax2.set_ylabel('Normalized Progress')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Algorithm Clustering
        ax3 = axes[1, 0]
        
        # Create feature vectors for clustering
        features = []
        labels = []
        for data in timeline_data:
            feature_vector = [
                data['total_solve_time'],
                data['plan_length'],
                np.mean(data['search_efficiency']) if data['search_efficiency'] else 0,
                max(data['memory_usage']) if data['memory_usage'] else 0
            ]
            features.append(feature_vector)
            labels.append(f"{data['algorithm']}_{data['problem']}")
        
        if features:
            features = np.array(features)
            
            # Simple 2D projection using first two features
            ax3.scatter(features[:, 0], features[:, 1], 
                       c=[colors.get(data['algorithm'], 'gray') for data in timeline_data],
                       s=100, alpha=0.7)
            
            # Add labels
            for i, label in enumerate(labels):
                ax3.annotate(label, (features[i, 0], features[i, 1]), 
                           xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        ax3.set_title('Algorithm Clustering (2D Projection)')
        ax3.set_xlabel('Solve Time')
        ax3.set_ylabel('Plan Length')
        ax3.grid(True, alpha=0.3)
        
        # 4. Performance Stability
        ax4 = axes[1, 1]
        
        # Calculate coefficient of variation for each algorithm
        stability_data = {}
        for data in timeline_data:
            alg = data['algorithm']
            if alg not in stability_data:
                stability_data[alg] = []
            stability_data[alg].append(data['total_solve_time'])
        
        algorithms = list(stability_data.keys())
        stability_values = []
        
        for alg in algorithms:
            times = stability_data[alg]
            if len(times) > 1:
                cv = np.std(times) / np.mean(times)  # Coefficient of variation
                stability_values.append(1 / (cv + 1e-6))  # Invert so higher is better
            else:
                stability_values.append(1.0)
        
        bars = ax4.bar(algorithms, stability_values, 
                      color=[colors.get(alg, 'gray') for alg in algorithms], alpha=0.8)
        
        ax4.set_title('Algorithm Stability (Inverse CV)')
        ax4.set_xlabel('Algorithm')
        ax4.set_ylabel('Stability Score')
        ax4.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, stability_values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{value:.2f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, "algorithm_signatures.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Algorithm signature plots saved to algorithm_signatures.png")


if __name__ == "__main__":
    analysis = SearchTrajectoryAnalysis()
    analysis.create_search_trajectory_plots()

