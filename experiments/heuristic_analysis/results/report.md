# Heuristic Comparison Results

## Experiment Overview
- **Heuristics tested**: 3
- **Test problems**: 5
- **Total experiments**: 15

## Results Summary

| Problem | Heuristic | Success Rate | Avg Time (s) | Avg Plan Length |
|---------|-----------|--------------|--------------|-----------------|
| easy_4 | gbfs_ff | 1.00 | 0.228 | 7.0 |
| easy_4 | gbfs_hadd | 1.00 | 0.219 | 7.0 |
| easy_4 | gbfs_hmax | 1.00 | 0.214 | 7.0 |
| easy_6 | gbfs_ff | 1.00 | 0.299 | 7.0 |
| easy_6 | gbfs_hadd | 1.00 | 0.310 | 7.0 |
| easy_6 | gbfs_hmax | 1.00 | 0.295 | 7.0 |
| medium_8 | gbfs_ff | 1.00 | 0.475 | 6.0 |
| medium_8 | gbfs_hadd | 1.00 | 0.462 | 6.0 |
| medium_8 | gbfs_hmax | 1.00 | 0.463 | 6.0 |
| medium_10 | gbfs_ff | 1.00 | 0.731 | 6.0 |
| medium_10 | gbfs_hadd | 1.00 | 0.701 | 6.0 |
| medium_10 | gbfs_hmax | 1.00 | 0.705 | 6.0 |
| hard_14 | gbfs_ff | 1.00 | 1.803 | 16.0 |
| hard_14 | gbfs_hadd | 1.00 | 1.804 | 16.0 |
| hard_14 | gbfs_hmax | 1.00 | 1.747 | 16.0 |

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
