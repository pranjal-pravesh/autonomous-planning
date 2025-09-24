# Topology Analysis Report

This experiment analyzes how different dock topologies affect planning performance.

## Experiment Configuration

| Topology | Description | Docks | Robots | Containers | Piles |
|----------|-------------|-------|--------|------------|-------|
| linear_4 | Linear topology with 4 docks | 4 | 2 | 8 | 4 |
| linear_6 | Linear topology with 6 docks | 6 | 2 | 12 | 6 |
| star_5 | Star topology with 5 docks (1 center + 4 spokes) | 5 | 2 | 10 | 5 |
| star_7 | Star topology with 7 docks (1 center + 6 spokes) | 7 | 3 | 14 | 7 |
| grid_2x2 | 2x2 Grid topology | 4 | 2 | 8 | 4 |
| grid_3x2 | 3x2 Grid topology | 6 | 3 | 12 | 6 |
| ring_4 | Ring topology with 4 docks | 4 | 2 | 8 | 4 |
| ring_6 | Ring topology with 6 docks | 6 | 2 | 12 | 6 |

## Results Summary

| Topology | Success Rate | Avg Solve Time (s) | Avg Plan Length |
|----------|--------------|-------------------|----------------|
| linear_4 | 1.00 | 0.466 | 17.0 |
| linear_6 | 1.00 | 1.045 | 21.0 |
| star_5 | 1.00 | 0.687 | 17.0 |
| star_7 | 1.00 | 2.171 | 15.0 |
| grid_2x2 | 1.00 | 0.457 | 18.0 |
| grid_3x2 | 1.00 | 1.451 | 19.0 |
| ring_4 | 1.00 | 0.461 | 15.0 |
| ring_6 | 1.00 | 1.078 | 39.0 |

## Topology Analysis

### Linear Topology

- **Average Solve Time**: 0.755s
- **Average Plan Length**: 19.0 actions
- **Average Success Rate**: 1.00

### Star Topology

- **Average Solve Time**: 1.429s
- **Average Plan Length**: 16.0 actions
- **Average Success Rate**: 1.00

### Grid Topology

- **Average Solve Time**: 0.954s
- **Average Plan Length**: 18.5 actions
- **Average Success Rate**: 1.00

### Ring Topology

- **Average Solve Time**: 0.769s
- **Average Plan Length**: 27.0 actions
- **Average Success Rate**: 1.00

## Key Findings

This experiment reveals how different network topologies impact planning:

- **Linear topology**: Simple connectivity, predictable routing
- **Star topology**: Central hub provides efficient routing but creates bottlenecks
- **Grid topology**: Multiple paths provide redundancy and flexibility
- **Ring topology**: Balanced connectivity with no single points of failure
- **Scalability**: Larger topologies generally require more planning time
- **Efficiency**: Some topologies may require longer plans but solve faster
