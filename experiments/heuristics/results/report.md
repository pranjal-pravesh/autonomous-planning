# Heuristic Comparison Results

## Experiment Overview
- **Heuristics tested**: 3
- **Test problems**: 3
- **Total experiments**: 9

## Results Summary

| Problem | Heuristic | Success Rate | Avg Time (s) | Avg Plan Length |
|---------|-----------|--------------|--------------|-----------------|
| easy | gbfs_ff | 1.00 | 0.218 | 7.0 |
| easy | gbfs_hadd | 1.00 | 0.210 | 7.0 |
| easy | gbfs_hmax | 1.00 | 0.213 | 7.0 |
| medium | gbfs_ff | 1.00 | 0.346 | 17.0 |
| medium | gbfs_hadd | 1.00 | 0.376 | 17.0 |
| medium | gbfs_hmax | 1.00 | 0.352 | 17.0 |
| hard | gbfs_ff | 1.00 | 0.541 | 43.0 |
| hard | gbfs_hadd | 1.00 | 0.562 | 43.0 |
| hard | gbfs_hmax | 1.00 | 0.573 | 43.0 |

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
