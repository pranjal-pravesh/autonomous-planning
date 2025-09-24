# Scaling Analysis Results

## Experiment Overview
- **Total configurations**: 9
- **Runs per configuration**: 5
- **Total runs**: 45

## Results Summary

| Configuration | Robots | Docks | Containers | Piles | Success Rate | Avg Time (s) | Avg Plan Length |
|---------------|--------|-------|------------|-------|--------------|--------------|-----------------|
| small_1 | 1 | 2 | 3 | 2 | 1.00 | 0.185 | 3.0 |
| small_2 | 1 | 3 | 4 | 3 | 1.00 | 0.209 | 4.0 |
| small_3 | 2 | 3 | 5 | 3 | 1.00 | 0.299 | 4.0 |
| medium_1 | 2 | 4 | 6 | 4 | 1.00 | 0.367 | 5.0 |
| medium_2 | 3 | 4 | 8 | 4 | 1.00 | 0.637 | 6.0 |
| medium_3 | 3 | 5 | 10 | 5 | 1.00 | 1.027 | 7.0 |
| large_1 | 3 | 6 | 12 | 6 | 1.00 | 1.620 | 8.0 |
| large_2 | 4 | 6 | 15 | 6 | 1.00 | 3.040 | 8.0 |
| large_3 | 4 | 8 | 18 | 8 | 1.00 | 5.867 | 10.0 |

## Key Findings

1. **Scaling Behavior**: Planning time generally increases with problem size
2. **Success Rate**: All small and medium problems solved successfully
3. **Plan Length**: Increases with number of containers
4. **Bottlenecks**: Large problems may hit time/memory limits

## Files Generated
- `raw_results.json`: Complete experimental data
- `summary.csv`: Summary statistics
- `scaling_analysis.png`: Visualization plots
- `report.md`: This report

## Next Steps
- Analyze scaling curves for exponential vs polynomial growth
- Test with different heuristics
- Investigate failure modes for large problems
