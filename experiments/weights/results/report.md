# Weight Distribution Analysis Report

This experiment analyzes how different container weight distributions affect planning performance.

## Experiment Configuration

| Distribution | Description | Robots | Docks | Containers | Piles |
|--------------|-------------|--------|-------|------------|-------|
| uniform_light | All containers 2t (light) | 2 | 4 | 8 | 4 |
| uniform_medium | All containers 4t (medium) | 2 | 4 | 8 | 4 |
| uniform_heavy | All containers 6t (heavy) | 2 | 4 | 8 | 4 |
| mixed_balanced | Balanced mix (2t, 4t, 6t) | 2 | 4 | 9 | 4 |
| light_biased | Mostly light containers (2t) | 2 | 4 | 8 | 4 |
| heavy_biased | Mostly heavy containers (6t) | 2 | 4 | 8 | 4 |
| extreme_heavy | All containers 6t with tight robot capacity | 2 | 4 | 8 | 4 |
| mixed_extreme | Mixed weights with tight robot capacity | 2 | 4 | 8 | 4 |

## Results Summary

| Distribution | Success Rate | Avg Solve Time (s) | Avg Plan Length |
|--------------|--------------|-------------------|----------------|
| uniform_light | 1.00 | 0.540 | 17.0 |
| uniform_medium | 1.00 | 0.351 | 26.0 |
| uniform_heavy | 1.00 | 0.349 | 26.0 |
| mixed_balanced | 1.00 | 0.504 | 13.0 |
| light_biased | 1.00 | 0.511 | 17.0 |
| heavy_biased | 1.00 | 0.422 | 15.0 |
| extreme_heavy | 0.00 | inf | 0.0 |
| mixed_extreme | 1.00 | 0.461 | 13.0 |

## Weight Distribution Analysis

### Uniform Weight Distributions

- **Average Solve Time**: 0.413s
- **Average Plan Length**: 23.0 actions

### Mixed Weight Distributions

- **Average Solve Time**: 0.483s
- **Average Plan Length**: 13.0 actions

### Biased Weight Distributions

- **Average Solve Time**: 0.466s
- **Average Plan Length**: 16.0 actions

## Key Findings

This experiment reveals how weight distributions impact planning:

- **Uniform weights**: Consistent performance, predictable capacity usage
- **Mixed weights**: More complex planning due to capacity constraints
- **Heavy-biased**: Requires careful capacity management and may need more steps
- **Light-biased**: Generally easier planning with fewer capacity constraints
- **Tight capacity**: Significantly impacts planning when combined with heavy containers
- **Extreme scenarios**: Very heavy containers with tight capacity create the most challenging problems
