# SPHORB Optimization Strategy

**Date**: 2025-10-18
**Based on**: Detailed profiling analysis

## Critical Finding: resize_and_split Breakdown

Detailed profiling reveals the composition of the `resize_and_split` bottleneck (50.8ms total):

| Component | Time (ms) | Percentage | Description |
|-----------|-----------|------------|-------------|
| **cv::resize()** | 25.4 | 50.1% | OpenCV image resizing with INTER_AREA |
| **splitSphere2()** | 21.1 | 41.5% | Spherical → Geodesic grid transformation |
| **extendEdge()** | 4.3 | 8.4% | Boundary handling between parts |

## Key Insights

### 1. resize vs split are EQUALLY important
- **resize**: 25.4ms (50%) - OpenCV function, already optimized
- **split**: 21.1ms (41%) - Custom geometric transformation
- Both contribute significantly to the bottleneck

### 2. Comparison with OpenCV ORB

**OpenCV ORB Code (Fast Detection Section)**:
```cpp
// From OpenCV's orb.cpp
// Build pyramid
for (int level = 0; level < nlevels; ++level) {
    cv::resize(image, imagePyramid[level], Size(), 1.0/getScale(level), 1.0/getScale(level), INTER_LINEAR);
    // Then directly runs FAST on imagePyramid[level]
    // NO geometric transformation needed
}
```

**SPHORB Code**:
```cpp
// For each level:
resize(temp, image, sz, 0, 0, cv::INTER_AREA);  // 25.4ms total
splitSphere2(image, subImg[i], ...);            // 21.1ms total
extendEdge(subImg[0], ...);                     // 4.3ms total
// THEN runs FAST on 5 separate subImg parts
```

**The Difference**: ORB works on planar images, SPHORB must transform spherical → geodesic grid

### 3. Why Other Sections Are Already Optimal

Comparing with ORB implementation:

**fast_detection** (20.4ms, 23.7%):
- SPHORB: Custom FAST on 5 geodesic parts
- ORB: OpenCV cv::FAST() on 1 planar image
- **Conclusion**: Similar algorithm, SPHORB just processes 5 parts vs 1 image
- **Code-level difference**: Minimal - both use FAST algorithm

**orientation** (0.9ms, 1.0%):
- Both: IC_Angle (Intensity Centroid)
- **Conclusion**: Already negligible, no optimization needed

**gaussian_filter** (9.2ms, 10.7%):
- SPHORB: cv::filter2D() with 7x7 hexagonal kernel on 5 parts
- ORB: cv::GaussianBlur() or skipped entirely
- **Conclusion**: Minor difference, low priority

**descriptor_computation** (0.7ms, 0.8%):
- Both: Identical ORB descriptor algorithm
- **Conclusion**: Already optimal

## Optimization Priorities

### Priority 1: Optimize splitSphere2() (Target: 50% reduction = ~10ms gain)

**Current**: 21.1ms (41.5% of resize_and_split)

**Analysis needed**:
1. Profile splitSphere2() internally - what's slow?
   - Coordinate transformation calculations?
   - Memory access patterns?
   - Interpolation?

**Potential optimizations**:
- SIMD vectorization for coordinate calculations
- Optimize memory access patterns (cache-friendly)
- Pre-compute lookup tables if applicable
- Use faster interpolation if quality allows

**Expected gain**: 10-15ms reduction

### Priority 2: Replace INTER_AREA with INTER_LINEAR (Target: 30% reduction = ~8ms gain)

**Current**: 25.4ms using INTER_AREA

**Rationale**:
- INTER_AREA: High quality, slow (computes area average)
- INTER_LINEAR: Good quality, fast (bilinear interpolation)
- OpenCV ORB uses INTER_LINEAR

**Risk**: Slight quality degradation
**Expected gain**: 7-10ms reduction

**Test approach**:
```cpp
// Change from:
resize(temp, image, sz, 0, 0, cv::INTER_AREA);
// To:
resize(temp, image, sz, 0, 0, cv::INTER_LINEAR);
```

### Priority 3: Optimize extendEdge() if needed (Target: 50% = ~2ms gain)

**Current**: 4.3ms (8.4% of resize_and_split)

**Low priority** - only pursue if Priorities 1-2 don't achieve goal

## Projected Performance After Optimization

| Scenario | resize | split | extend | Total Time | vs Baseline |
|----------|--------|-------|--------|------------|-------------|
| **Current** | 25.4 | 21.1 | 4.3 | 85.9ms | 1.0x |
| **After Priority 2** (INTER_LINEAR) | 18.0 | 21.1 | 4.3 | 78.4ms | 1.1x faster |
| **After Priority 1** (optimize split) | 25.4 | 10.5 | 4.3 | 75.2ms | 1.14x faster |
| **After Both** | 18.0 | 10.5 | 4.3 | 67.8ms | 1.27x faster |
| **Target** (3x speedup) | - | - | - | 26.2ms | 3.27x faster |

**Gap**: Even with both optimizations, we get ~68ms (1.27x) vs target of 26ms (3.3x)

## Reality Check

**Current situation**:
- Total time: 85.9ms
- resize_and_split: 50.8ms (59%)
- Even if we ELIMINATE resize_and_split entirely → 35ms (still above 26ms target)

**Conclusion**:
The 3x speedup target (26ms) is **extremely challenging** because:
1. SPHORB's fundamental overhead is the spherical→geodesic transformation
2. Even with perfect optimization of resize_and_split, remaining 35ms > 26ms target
3. Would need to optimize EVERYTHING, not just resize_and_split

## Recommended Action Plan

### Phase 1: Quick Wins (Expected: 1.2-1.3x speedup → ~65-70ms)
1. Test INTER_LINEAR vs INTER_AREA (~8ms gain)
2. Profile and optimize splitSphere2() (~10ms gain)

### Phase 2: Additional Optimization if Needed
1. Optimize fast_detection (20ms → potential 5-10ms gain)
2. Consider skipping or optimizing gaussian_filter (9ms → potential 2-4ms gain)

### Phase 3: If Still Not Enough
1. Algorithmic changes (reduce pyramid levels, reduce parts, etc.)
2. Accept that SPHORB's spherical design has fundamental overhead vs planar ORB

## Next Steps

1. ✅ Document profiling results
2. ✅ Compare with OpenCV ORB implementation
3. **TODO**: Inspect splitSphere2() source code
4. **TODO**: Profile splitSphere2() internally
5. **TODO**: Prototype INTER_LINEAR optimization
6. **TODO**: Benchmark and compare quality vs speed tradeoff
