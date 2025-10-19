# SPHORB Performance Profiling Results

**Date**: 2025-10-18
**Test Image**: `images/frame_000000.png` (2160x1080)
**Keypoints Detected**: 523
**Total Time**: 85.963 ms

## Executive Summary

Profiling identified **`resize_and_split`** as the dominant bottleneck, consuming **62.6%** of total execution time. This section performs:
1. Image resizing using OpenCV's `resize()` with `INTER_AREA`
2. Splitting spherical image into 5 geodesic grid parts using `splitSphere2()`

## Detailed Breakdown by Section

| Section | Total Time (ms) | Percentage | Priority |
|---------|-----------------|------------|----------|
| **resize_and_split** | 53.810 | 62.6% | **HIGH** |
| fast_detection | 20.389 | 23.7% | MEDIUM |
| gaussian_filter | 9.175 | 10.7% | LOW |
| orientation | 0.886 | 1.0% | IGNORE |
| descriptor_computation | 0.724 | 0.8% | IGNORE |

## Per-Level Timing Breakdown

Timing data for each of the 7 pyramid levels:

### Level 0 (Largest - 256×5 = 1280 width)
- resize_and_split: 13.293 ms
- fast_detection: 5.789 ms
- orientation: 0.211 ms
- gaussian_filter: 2.913 ms
- descriptor_computation: 0.192 ms
- **Level Total: 22.398 ms (26.1% of total)**

### Level 1 (204×5 = 1020 width)
- resize_and_split: 9.672 ms
- fast_detection: 4.413 ms
- orientation: 0.169 ms
- gaussian_filter: 1.967 ms
- descriptor_computation: 0.124 ms
- **Level Total: 16.345 ms (19.0%)**

### Level 2 (162×5 = 810 width)
- resize_and_split: 7.148 ms
- fast_detection: 3.505 ms
- orientation: 0.123 ms
- gaussian_filter: 1.299 ms
- descriptor_computation: 0.095 ms
- **Level Total: 12.170 ms (14.2%)**

### Level 3 (128×5 = 640 width)
- resize_and_split: 5.659 ms
- fast_detection: 2.865 ms
- orientation: 0.158 ms
- gaussian_filter: 1.445 ms
- descriptor_computation: 0.095 ms
- **Level Total: 10.222 ms (11.9%)**

### Level 4 (102×5 = 510 width)
- resize_and_split: 6.055 ms
- fast_detection: 1.589 ms
- orientation: 0.103 ms
- gaussian_filter: 0.589 ms
- descriptor_computation: 0.057 ms
- **Level Total: 8.393 ms (9.8%)**

### Level 5 (80×5 = 400 width)
- resize_and_split: 6.155 ms
- fast_detection: 1.596 ms
- orientation: 0.079 ms
- gaussian_filter: 0.576 ms
- descriptor_computation: 0.071 ms
- **Level Total: 8.477 ms (9.9%)**

### Level 6 (Smallest - 64×5 = 320 width)
- resize_and_split: 5.828 ms
- fast_detection: 0.632 ms
- orientation: 0.043 ms
- gaussian_filter: 0.386 ms
- descriptor_computation: 0.090 ms
- **Level Total: 6.979 ms (8.1%)**

## Key Observations

1. **Resize/Split Dominance**: The first 3 levels (largest images) account for 30.113 ms out of 53.810 ms (56%) of resize_and_split time

2. **Counterintuitive Scaling**: Levels 4-6 show relatively flat resize_and_split times (5.8-6.2 ms) despite decreasing image sizes, suggesting fixed overhead

3. **Fast Detection Scales Well**: FAST detection time correlates well with image size (5.8ms → 0.6ms from level 0 to 6)

4. **Descriptor Computation is Negligible**: Only 0.8% of total time, already highly optimized

## Why OpenMP Multi-threading Failed

Previous attempt to parallelize with OpenMP showed **no improvement** (actually 0.5% slower). Reasons:

1. **Small Task Count**: Only 7 levels - insufficient parallelism to overcome thread overhead
2. **Memory Bandwidth Bottleneck**: Image resize/copy operations are memory-bound, not CPU-bound
3. **OpenCV Already Optimized**: `cv::resize()` may already use internal multi-threading

## Optimization Priorities

### Priority 1: Optimize resize_and_split (Target: 50-70% reduction)
- Investigate `splitSphere2()` function implementation
- Consider faster interpolation methods (INTER_LINEAR instead of INTER_AREA)
- Eliminate unnecessary memory allocations/copies
- **Potential gain: 35-40 ms reduction**

### Priority 2: Optimize fast_detection if needed
- Only pursue if Priority 1 doesn't achieve 3x target
- **Potential gain: 5-10 ms reduction**

### Priority 3: Optimize gaussian_filter if still needed
- Low priority, only 10.7% of time
- **Potential gain: 2-4 ms reduction**

## Target Performance

- **Current**: 85.963 ms (SPHORB)
- **Baseline ORB**: ~36.81 ms
- **Target**: 26.23 ms (3x speedup from baseline 78.68 ms)
- **Required reduction**: 59.7 ms (69%)

**Conclusion**: Optimizing `resize_and_split` alone could potentially achieve 40-50ms reduction, bringing total time to ~40-45ms. Additional optimization of `fast_detection` would be needed to reach the 26ms target.

## Next Steps

1. Profile `resize_and_split` in more detail:
   - Separate `cv::resize()` time from `splitSphere2()` time
   - Identify memory allocation overhead

2. Compare SPHORB implementation with OpenCV ORB:
   - Analyze ORB's pyramid building strategy
   - Check if ORB avoids similar geometric transformations

3. Prototype optimizations:
   - Test INTER_LINEAR vs INTER_AREA
   - Optimize splitSphere2() implementation
   - Consider pre-allocating buffers
