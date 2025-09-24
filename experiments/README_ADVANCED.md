# Advanced Research Experiments

This document describes the advanced research-level experiments designed to provide deep insights into automated planning systems.

## **1. Heuristic Analysis & Characterization** (`heuristic_analysis/`)

### **Research Objectives**
- **Heuristic Quality Assessment**: Measure how "informed" each heuristic is
- **Admissibility Analysis**: Determine how close heuristics are to optimal
- **Consistency Evaluation**: Test heuristic consistency across problem types
- **Dominance Patterns**: Identify which heuristics dominate others

### **Key Metrics**
- **Admissibility Ratio**: `heuristic_value / actual_cost` (closer to 1.0 is better)
- **Heuristic Consistency**: Measure of how consistent heuristic values are
- **Dominance Score**: How often one heuristic outperforms others
- **Informedness**: How much the heuristic reduces search space

### **Experimental Design**
- **6 Heuristics**: FF, hAdd, hMax, CG, CEA, LM-Cut
- **6 Problem Types**: Varying size, complexity, and constraint levels
- **Multiple Runs**: 3 runs per configuration for statistical reliability
- **Comprehensive Analysis**: Statistical significance testing and effect sizes

### **Expected Insights**
- Which heuristics are most informed for logistics planning
- How heuristic quality varies with problem characteristics
- Identification of heuristic dominance patterns
- Recommendations for heuristic selection

---

## **2. Search Space Analysis** (`search_analysis/`)

### **Research Objectives**
- **State Space Exploration**: Measure how much of the state space is explored
- **Search Efficiency**: Analyze search algorithm performance
- **Bottleneck Identification**: Find limiting factors in search process
- **Scaling Behavior**: Understand how search scales with problem size

### **Key Metrics**
- **States Explored**: Number of states examined during search
- **Branching Factor**: Average number of successors per state
- **Search Efficiency**: `plan_length / states_explored`
- **State Space Density**: `states_explored / total_state_space`
- **Dead-end Analysis**: Identification of problematic states

### **Experimental Design**
- **6 Search Algorithms**: GBFS variants, A* variants, BFS
- **6 Problem Configurations**: Varying size and constraint density
- **State Space Estimation**: Theoretical vs. actual exploration
- **Performance Profiling**: Detailed search behavior analysis

### **Expected Insights**
- Which search algorithms are most efficient for logistics
- How search efficiency scales with problem size
- Identification of search bottlenecks
- State space characteristics and exploration patterns

---

## **Research Methodology**

### **Statistical Rigor**
- **Multiple Runs**: 3+ runs per configuration
- **Statistical Testing**: t-tests, ANOVA, effect sizes
- **Confidence Intervals**: 95% CI for key metrics
- **Outlier Analysis**: Identification and handling of outliers

### **Reproducibility**
- **Fixed Random Seeds**: Consistent problem generation
- **Environment Documentation**: Python version, UP version, system specs
- **Configuration Files**: All parameters saved as JSON
- **Version Control**: Git tracking of all changes

### **Data Collection**
- **Raw Data**: Complete experimental data in JSON format
- **Statistical Summaries**: Mean, std, min, max for all metrics
- **Visualizations**: Comprehensive plots and charts
- **Analysis Reports**: Detailed findings and insights

---

## **Running the Experiments**

### **Heuristic Analysis**
```bash
cd experiments/heuristic_analysis
python heuristic_characterization.py
```

### **Search Space Analysis**
```bash
cd experiments/search_analysis
python search_space_analysis.py
```

### **Output Files**
Each experiment generates:
- `*_results.json`: Complete raw data
- `*_analysis.json`: Statistical analysis
- `*_data.csv`: Processed data for further analysis
- `*_analysis.png`: Comprehensive visualizations
- `report.md`: Detailed findings report

---

## **Research Contributions**

### **Theoretical Contributions**
- **Heuristic Characterization**: Deep analysis of heuristic behavior
- **Search Space Properties**: Understanding of logistics planning search spaces
- **Algorithm Comparison**: Rigorous comparison of planning algorithms
- **Performance Prediction**: Models for predicting planning performance

### **Practical Contributions**
- **Algorithm Selection**: Guidelines for choosing appropriate algorithms
- **Problem Difficulty Assessment**: Methods for predicting problem difficulty
- **Performance Optimization**: Insights for improving planning systems
- **Scalability Analysis**: Understanding of system limitations

### **Methodological Contributions**
- **Experimental Design**: Rigorous methodology for planning experiments
- **Statistical Analysis**: Proper statistical treatment of planning data
- **Reproducibility**: Standards for reproducible planning research
- **Evaluation Metrics**: Comprehensive metrics for planning evaluation

---

## **Future Extensions**

### **Immediate Extensions**
- **More Heuristics**: Additional heuristic functions
- **Larger Problems**: Industrial-scale problem instances
- **Real-world Data**: Integration with actual logistics data
- **Multi-objective**: Optimization of multiple criteria

### **Advanced Extensions**
- **Learning-based Heuristics**: ML-enhanced heuristic functions
- **Dynamic Planning**: Real-time replanning capabilities
- **Uncertainty Handling**: Probabilistic planning extensions
- **Human-AI Collaboration**: Mixed human-robot planning

---

## **Publication Potential**

These experiments are designed to produce results suitable for publication in:
- **ICAPS** (International Conference on Automated Planning and Scheduling)
- **AAAI** (Association for the Advancement of Artificial Intelligence)
- **IJCAI** (International Joint Conference on Artificial Intelligence)
- **JAIR** (Journal of Artificial Intelligence Research)

The rigorous experimental design, comprehensive analysis, and novel insights make these experiments valuable contributions to the automated planning research community.
