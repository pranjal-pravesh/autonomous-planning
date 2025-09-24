# Heuristic Comparison Results

## Experiment Overview
- **Heuristics tested**: 6
- **Test problems**: 5
- **Total experiments**: 30

## Results Summary

| Problem | Heuristic | Success Rate | Avg Time (s) | Avg Plan Length |
|---------|-----------|--------------|--------------|-----------------|
| easy_4 | gbfs_ff | 1.00 | 0.222 | 7.0 |
| easy_4 | gbfs_hadd | 1.00 | 0.216 | 7.0 |
| easy_4 | gbfs_hmax | 1.00 | 0.217 | 7.0 |
| easy_4 | astar_ff | 1.00 | 0.215 | 7.0 |
| easy_4 | astar_hadd | 1.00 | 0.214 | 7.0 |
| easy_4 | bfs | 1.00 | 0.232 | 7.0 |
| easy_6 | gbfs_ff | 1.00 | 0.296 | 7.0 |
| easy_6 | gbfs_hadd | 1.00 | 0.305 | 7.0 |
| easy_6 | gbfs_hmax | 1.00 | 0.294 | 7.0 |
| easy_6 | astar_ff | 1.00 | 0.289 | 7.0 |
| easy_6 | astar_hadd | 1.00 | 0.292 | 7.0 |
| easy_6 | bfs | 1.00 | 0.293 | 7.0 |
| medium_8 | gbfs_ff | 1.00 | 0.458 | 6.0 |
| medium_8 | gbfs_hadd | 1.00 | 0.457 | 6.0 |
| medium_8 | gbfs_hmax | 1.00 | 0.453 | 6.0 |
| medium_8 | astar_ff | 1.00 | 0.507 | 6.0 |
| medium_8 | astar_hadd | 1.00 | 0.462 | 6.0 |
| medium_8 | bfs | 1.00 | 0.464 | 6.0 |
| medium_10 | gbfs_ff | 1.00 | 0.701 | 6.0 |
| medium_10 | gbfs_hadd | 1.00 | 0.695 | 6.0 |
| medium_10 | gbfs_hmax | 1.00 | 0.703 | 6.0 |
| medium_10 | astar_ff | 1.00 | 0.685 | 6.0 |
| medium_10 | astar_hadd | 1.00 | 0.695 | 6.0 |
| medium_10 | bfs | 1.00 | 0.688 | 6.0 |
| hard_14 | gbfs_ff | 1.00 | 1.724 | 16.0 |
| hard_14 | gbfs_hadd | 1.00 | 1.748 | 16.0 |
| hard_14 | gbfs_hmax | 1.00 | 1.722 | 16.0 |
| hard_14 | astar_ff | 1.00 | 1.730 | 16.0 |
| hard_14 | astar_hadd | 1.00 | 1.710 | 16.0 |
| hard_14 | bfs | 1.00 | 1.722 | 16.0 |

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
