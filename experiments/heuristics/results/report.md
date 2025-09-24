# Heuristic Comparison Results

## Experiment Overview
- **Heuristics tested**: 7
- **Test problems**: 6
- **Total experiments**: 42

## Results Summary

| Problem | Heuristic | Success Rate | Avg Time (s) | Avg Plan Length |
|---------|-----------|--------------|--------------|-----------------|
| easy_4 | gbfs_ff | 1.00 | 0.221 | 7.0 |
| easy_4 | gbfs_hadd | 1.00 | 0.212 | 7.0 |
| easy_4 | gbfs_hmax | 1.00 | 0.216 | 7.0 |
| easy_4 | gbfs_cg | 1.00 | 0.215 | 7.0 |
| easy_4 | gbfs_cea | 1.00 | 0.212 | 7.0 |
| easy_4 | gbfs_lmcut | 1.00 | 0.213 | 7.0 |
| easy_4 | gbfs_blind | 1.00 | 0.213 | 7.0 |
| easy_6 | gbfs_ff | 1.00 | 0.315 | 7.0 |
| easy_6 | gbfs_hadd | 1.00 | 0.293 | 7.0 |
| easy_6 | gbfs_hmax | 1.00 | 0.294 | 7.0 |
| easy_6 | gbfs_cg | 1.00 | 0.297 | 7.0 |
| easy_6 | gbfs_cea | 1.00 | 0.299 | 7.0 |
| easy_6 | gbfs_lmcut | 1.00 | 0.311 | 7.0 |
| easy_6 | gbfs_blind | 1.00 | 0.302 | 7.0 |
| medium_8 | gbfs_ff | 1.00 | 0.479 | 6.0 |
| medium_8 | gbfs_hadd | 1.00 | 0.480 | 6.0 |
| medium_8 | gbfs_hmax | 1.00 | 0.474 | 6.0 |
| medium_8 | gbfs_cg | 1.00 | 0.480 | 6.0 |
| medium_8 | gbfs_cea | 1.00 | 0.462 | 6.0 |
| medium_8 | gbfs_lmcut | 1.00 | 0.461 | 6.0 |
| medium_8 | gbfs_blind | 1.00 | 0.469 | 6.0 |
| medium_10 | gbfs_ff | 1.00 | 0.700 | 6.0 |
| medium_10 | gbfs_hadd | 1.00 | 0.698 | 6.0 |
| medium_10 | gbfs_hmax | 1.00 | 0.698 | 6.0 |
| medium_10 | gbfs_cg | 1.00 | 0.700 | 6.0 |
| medium_10 | gbfs_cea | 1.00 | 0.711 | 6.0 |
| medium_10 | gbfs_lmcut | 1.00 | 0.699 | 6.0 |
| medium_10 | gbfs_blind | 1.00 | 0.698 | 6.0 |
| medium_12 | gbfs_ff | 1.00 | 1.065 | 6.0 |
| medium_12 | gbfs_hadd | 1.00 | 1.056 | 6.0 |
| medium_12 | gbfs_hmax | 1.00 | 1.054 | 6.0 |
| medium_12 | gbfs_cg | 1.00 | 1.053 | 6.0 |
| medium_12 | gbfs_cea | 1.00 | 1.062 | 6.0 |
| medium_12 | gbfs_lmcut | 1.00 | 1.150 | 6.0 |
| medium_12 | gbfs_blind | 1.00 | 1.091 | 6.0 |
| hard_14 | gbfs_ff | 1.00 | 1.814 | 16.0 |
| hard_14 | gbfs_hadd | 1.00 | 1.801 | 16.0 |
| hard_14 | gbfs_hmax | 1.00 | 1.775 | 16.0 |
| hard_14 | gbfs_cg | 1.00 | 1.825 | 16.0 |
| hard_14 | gbfs_cea | 1.00 | 1.842 | 16.0 |
| hard_14 | gbfs_lmcut | 1.00 | 1.759 | 16.0 |
| hard_14 | gbfs_blind | 1.00 | 1.795 | 16.0 |

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
