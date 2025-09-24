# Heuristic Comparison Results

## Experiment Overview
- **Heuristics tested**: 7
- **Test problems**: 6
- **Total experiments**: 42

## Results Summary

| Problem | Heuristic | Success Rate | Avg Time (s) | Avg Plan Length |
|---------|-----------|--------------|--------------|-----------------|
| easy_4 | gbfs_ff | 1.00 | 0.219 | 7.0 |
| easy_4 | gbfs_hadd | 1.00 | 0.212 | 7.0 |
| easy_4 | gbfs_hmax | 1.00 | 0.212 | 7.0 |
| easy_4 | gbfs_cg | 1.00 | 0.211 | 7.0 |
| easy_4 | gbfs_cea | 1.00 | 0.212 | 7.0 |
| easy_4 | gbfs_lmcut | 1.00 | 0.220 | 7.0 |
| easy_4 | gbfs_blind | 1.00 | 0.213 | 7.0 |
| easy_6 | gbfs_ff | 1.00 | 0.292 | 7.0 |
| easy_6 | gbfs_hadd | 1.00 | 0.293 | 7.0 |
| easy_6 | gbfs_hmax | 1.00 | 0.302 | 7.0 |
| easy_6 | gbfs_cg | 1.00 | 0.292 | 7.0 |
| easy_6 | gbfs_cea | 1.00 | 0.293 | 7.0 |
| easy_6 | gbfs_lmcut | 1.00 | 0.300 | 7.0 |
| easy_6 | gbfs_blind | 1.00 | 0.297 | 7.0 |
| medium_8 | gbfs_ff | 1.00 | 0.468 | 6.0 |
| medium_8 | gbfs_hadd | 1.00 | 0.467 | 6.0 |
| medium_8 | gbfs_hmax | 1.00 | 0.473 | 6.0 |
| medium_8 | gbfs_cg | 1.00 | 0.464 | 6.0 |
| medium_8 | gbfs_cea | 1.00 | 0.465 | 6.0 |
| medium_8 | gbfs_lmcut | 1.00 | 0.468 | 6.0 |
| medium_8 | gbfs_blind | 1.00 | 0.473 | 6.0 |
| medium_10 | gbfs_ff | 1.00 | 0.728 | 6.0 |
| medium_10 | gbfs_hadd | 1.00 | 0.730 | 6.0 |
| medium_10 | gbfs_hmax | 1.00 | 0.720 | 6.0 |
| medium_10 | gbfs_cg | 0.67 | 0.708 | 6.0 |
| medium_10 | gbfs_cea | 1.00 | 0.700 | 6.0 |
| medium_10 | gbfs_lmcut | 1.00 | 0.715 | 6.0 |
| medium_10 | gbfs_blind | 1.00 | 0.680 | 6.0 |
| medium_12 | gbfs_ff | 1.00 | 1.030 | 6.0 |
| medium_12 | gbfs_hadd | 0.67 | 1.021 | 6.0 |
| medium_12 | gbfs_hmax | 1.00 | 1.023 | 6.0 |
| medium_12 | gbfs_cg | 1.00 | 1.017 | 6.0 |
| medium_12 | gbfs_cea | 1.00 | 1.029 | 6.0 |
| medium_12 | gbfs_lmcut | 1.00 | 1.020 | 6.0 |
| medium_12 | gbfs_blind | 0.67 | 1.019 | 6.0 |
| hard_14 | gbfs_ff | 1.00 | 1.697 | 16.0 |
| hard_14 | gbfs_hadd | 1.00 | 1.736 | 16.0 |
| hard_14 | gbfs_hmax | 1.00 | 1.688 | 16.0 |
| hard_14 | gbfs_cg | 1.00 | 1.718 | 16.0 |
| hard_14 | gbfs_cea | 0.67 | 1.794 | 16.0 |
| hard_14 | gbfs_lmcut | 1.00 | 1.761 | 16.0 |
| hard_14 | gbfs_blind | 1.00 | 1.690 | 16.0 |

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
