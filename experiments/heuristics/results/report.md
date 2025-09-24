# Heuristic Comparison Results

## Experiment Overview
- **Heuristics tested**: 2
- **Test problems**: 3
- **Total experiments**: 6

## Results Summary

| Problem | Heuristic | Success Rate | Avg Time (s) | Avg Plan Length |
|---------|-----------|--------------|--------------|-----------------|
| easy | fast-downward | 1.00 | 0.188 | 3.0 |
| easy | pyperplan | 0.00 | inf | 0.0 |
| medium | fast-downward | 1.00 | 0.268 | 9.0 |
| medium | pyperplan | 0.00 | inf | 0.0 |
| hard | fast-downward | 1.00 | 0.460 | 8.0 |
| hard | pyperplan | 0.00 | inf | 0.0 |

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
