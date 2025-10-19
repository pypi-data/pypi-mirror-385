#!/usr/bin/env python3
"""
Compare benchmark results before and after optimization
"""
import json
import sys
from pathlib import Path

def load_benchmark(filepath):
    """Load benchmark JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def print_separator(char='=', length=70):
    print(char * length)

def compare_benchmarks(before_file, after_file):
    """Compare two benchmark results"""

    before = load_benchmark(before_file)
    after = load_benchmark(after_file)

    print_separator()
    print("BENCHMARK COMPARISON")
    print_separator()

    print(f"\nBefore: {before_file}")
    print(f"  Date: {before.get('benchmark_date', 'N/A')}")
    print(f"  Images: {before.get('total_images', 'N/A')}")

    print(f"\nAfter:  {after_file}")
    print(f"  Date: {after.get('benchmark_date', 'N/A')}")
    print(f"  Images: {after.get('total_images', 'N/A')}")

    # SPHORB comparison
    print(f"\n{'-'*70}")
    print("SPHORB Performance")
    print(f"{'-'*70}")

    before_sphorb = before['SPHORB']
    after_sphorb = after['SPHORB']

    before_time = before_sphorb['avg_time_ms']
    after_time = after_sphorb['avg_time_ms']
    speedup = before_time / after_time

    print(f"\nExecution Time:")
    print(f"  Before: {before_time:.2f} ± {before_sphorb['std_time_ms']:.2f} ms")
    print(f"  After:  {after_time:.2f} ± {after_sphorb['std_time_ms']:.2f} ms")
    print(f"  Speedup: {speedup:.2f}x {'faster' if speedup > 1 else 'slower'}")
    print(f"  Improvement: {(speedup - 1) * 100:.1f}%")

    print(f"\nKeypoints:")
    print(f"  Before: {before_sphorb['avg_keypoints']:.1f} ± {before_sphorb['std_keypoints']:.1f}")
    print(f"  After:  {after_sphorb['avg_keypoints']:.1f} ± {after_sphorb['std_keypoints']:.1f}")
    kp_diff = after_sphorb['avg_keypoints'] - before_sphorb['avg_keypoints']
    kp_diff_pct = (kp_diff / before_sphorb['avg_keypoints']) * 100
    print(f"  Difference: {kp_diff:+.1f} ({kp_diff_pct:+.1f}%)")

    # OpenCV ORB comparison (sanity check)
    print(f"\n{'-'*70}")
    print("OpenCV ORB (Reference)")
    print(f"{'-'*70}")

    before_orb = before['OpenCV_ORB']
    after_orb = after['OpenCV_ORB']

    print(f"\nExecution Time:")
    print(f"  Before: {before_orb['avg_time_ms']:.2f} ms")
    print(f"  After:  {after_orb['avg_time_ms']:.2f} ms")
    print(f"  (Should be similar - used as reference)")

    # Overall comparison
    print(f"\n{'-'*70}")
    print("Overall Comparison vs OpenCV ORB")
    print(f"{'-'*70}")

    before_ratio = before['comparison']['speedup_ratio']
    after_ratio = after_sphorb['avg_time_ms'] / after_orb['avg_time_ms']

    print(f"\nSPHORB vs ORB Speed Ratio:")
    print(f"  Before: {before_ratio:.2f}x slower")
    print(f"  After:  {after_ratio:.2f}x {'slower' if after_ratio > 1 else 'faster'}")
    print(f"  Improvement: {before_ratio - after_ratio:.2f}x")

    # Goal progress
    print(f"\n{'-'*70}")
    print("Optimization Goal Progress")
    print(f"{'-'*70}")

    target_speedup = before['comparison']['target_speedup']
    achieved_speedup = speedup
    progress = (achieved_speedup / target_speedup) * 100

    print(f"\nTarget: {target_speedup:.1f}x speedup")
    print(f"Achieved: {achieved_speedup:.2f}x speedup")
    print(f"Progress: {progress:.1f}%")

    if achieved_speedup >= target_speedup:
        print(f"\n🎉 GOAL ACHIEVED! ({achieved_speedup:.2f}x >= {target_speedup:.1f}x)")
    else:
        remaining = target_speedup / achieved_speedup
        print(f"\n📊 Additional {remaining:.2f}x speedup needed to reach goal")

    print_separator()

    # Summary table
    print("\nSUMMARY TABLE")
    print_separator()
    print(f"{'Metric':<30} {'Before':<15} {'After':<15} {'Change':<15}")
    print_separator('-')
    print(f"{'SPHORB time (ms)':<30} {before_time:<15.2f} {after_time:<15.2f} {speedup:<15.2f}x")
    print(f"{'SPHORB keypoints':<30} {before_sphorb['avg_keypoints']:<15.1f} {after_sphorb['avg_keypoints']:<15.1f} {kp_diff:+<15.1f}")
    print(f"{'vs ORB ratio':<30} {before_ratio:<15.2f}x {after_ratio:<15.2f}x {before_ratio-after_ratio:+<15.2f}")
    print_separator()

def main():
    if len(sys.argv) < 3:
        print("Usage: python compare_benchmarks.py <before.json> <after.json>")
        print("\nExample:")
        print("  python compare_benchmarks.py \\")
        print("    benchmarks/baseline_before_optimization.json \\")
        print("    benchmarks/phase1_after_optimization.json")
        sys.exit(1)

    before_file = Path(sys.argv[1])
    after_file = Path(sys.argv[2])

    if not before_file.exists():
        print(f"Error: {before_file} not found")
        sys.exit(1)

    if not after_file.exists():
        print(f"Error: {after_file} not found")
        sys.exit(1)

    compare_benchmarks(before_file, after_file)

if __name__ == "__main__":
    main()
