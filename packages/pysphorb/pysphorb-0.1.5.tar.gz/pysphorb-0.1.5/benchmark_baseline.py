#!/usr/bin/env python3
"""
Baseline Performance Benchmark for SPHORB
Measures speed and memory usage before optimization
"""
import time
import cv2
import numpy as np
import psutil
import os
import json
from pathlib import Path

def get_memory_usage_mb():
    """Get current process memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def benchmark_detector_on_images(detector_type, image_paths, runs_per_image=3):
    """
    Benchmark a detector across multiple images

    Args:
        detector_type: 'SPHORB' or 'ORB'
        image_paths: List of image paths
        runs_per_image: Number of runs per image

    Returns:
        Aggregated statistics across all images
    """
    all_times = []
    all_keypoint_counts = []
    total_images = len(image_paths)

    print(f"\n{'='*70}")
    print(f"Benchmarking {detector_type} on {total_images} images...")
    print(f"{'='*70}")

    for idx, img_path in enumerate(image_paths):
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"  [SKIP] Could not load: {img_path.name}")
            continue

        if idx % 20 == 0:
            print(f"  Progress: {idx}/{total_images} images processed...")

        # Run detector multiple times on this image
        for run in range(runs_per_image):
            if detector_type == 'SPHORB':
                import pysphorb
                detector = pysphorb.SPHORB(nfeatures=500, nlevels=7)

                start = time.perf_counter()
                kp, desc = detector.detectAndCompute(img)
                elapsed = time.perf_counter() - start

                del detector

            elif detector_type == 'ORB':
                detector = cv2.ORB_create(nfeatures=500, nlevels=8, scaleFactor=1.2)

                start = time.perf_counter()
                kp, desc = detector.detectAndCompute(img, None)
                elapsed = time.perf_counter() - start

                del detector

            all_times.append(elapsed * 1000)  # Convert to ms
            all_keypoint_counts.append(len(kp))

    # Calculate aggregated statistics
    times_array = np.array(all_times)
    kp_array = np.array(all_keypoint_counts)

    stats = {
        'detector': detector_type,
        'total_images': total_images,
        'total_runs': len(all_times),
        'runs_per_image': runs_per_image,

        # Time statistics
        'avg_time_ms': float(np.mean(times_array)),
        'std_time_ms': float(np.std(times_array)),
        'min_time_ms': float(np.min(times_array)),
        'max_time_ms': float(np.max(times_array)),
        'median_time_ms': float(np.median(times_array)),

        # Keypoint statistics
        'avg_keypoints': float(np.mean(kp_array)),
        'std_keypoints': float(np.std(kp_array)),
        'min_keypoints': int(np.min(kp_array)),
        'max_keypoints': int(np.max(kp_array)),
        'median_keypoints': float(np.median(kp_array)),
    }

    print(f"\n{detector_type} Results:")
    print(f"  Images processed: {total_images}")
    print(f"  Total runs: {stats['total_runs']}")
    print(f"  Time: {stats['avg_time_ms']:.2f} ± {stats['std_time_ms']:.2f} ms")
    print(f"    (min={stats['min_time_ms']:.2f}, median={stats['median_time_ms']:.2f}, max={stats['max_time_ms']:.2f})")
    print(f"  Keypoints: {stats['avg_keypoints']:.1f} ± {stats['std_keypoints']:.1f}")
    print(f"    (min={stats['min_keypoints']}, median={stats['median_keypoints']:.0f}, max={stats['max_keypoints']})")

    return stats

def main(output_name="benchmark_results"):
    """
    Run benchmark and save results

    Args:
        output_name: Base name for output file (without .json extension)
    """
    print("=" * 70)
    print("SPHORB Performance Benchmark")
    print("=" * 70)

    # Find test images
    image_dir = Path("images")
    if not image_dir.exists():
        print(f"Error: {image_dir} directory not found!")
        print("Please ensure test images are available.")
        return

    image_files = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png"))
    if not image_files:
        print(f"Error: No images found in {image_dir}")
        return

    print(f"\nFound {len(image_files)} test images")

    # Benchmark SPHORB
    print("\n" + "=" * 70)
    print("Phase 1: Benchmarking SPHORB")
    print("=" * 70)
    sphorb_stats = benchmark_detector_on_images('SPHORB', image_files, runs_per_image=3)

    # Benchmark OpenCV ORB
    print("\n" + "=" * 70)
    print("Phase 2: Benchmarking OpenCV ORB")
    print("=" * 70)
    orb_stats = benchmark_detector_on_images('ORB', image_files, runs_per_image=3)

    # Comparison
    print("\n" + "=" * 70)
    print("COMPARISON")
    print("=" * 70)

    speedup_ratio = sphorb_stats['avg_time_ms'] / orb_stats['avg_time_ms']

    print(f"\nSPHORB vs OpenCV ORB:")
    print(f"  SPHORB avg time: {sphorb_stats['avg_time_ms']:.2f} ms")
    print(f"  ORB avg time:    {orb_stats['avg_time_ms']:.2f} ms")
    print(f"  Speed ratio:     {speedup_ratio:.2f}x {'slower' if speedup_ratio > 1 else 'faster'}")

    print(f"\nOptimization Target:")
    target_time = sphorb_stats['avg_time_ms'] / 3.0
    print(f"  Current SPHORB:  {sphorb_stats['avg_time_ms']:.2f} ms")
    print(f"  Target (3x):     {target_time:.2f} ms")
    print(f"  Required:        {3.0:.1f}x speedup")

    # Save results
    results = {
        'benchmark_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'image_directory': str(image_dir),
        'total_images': len(image_files),
        'SPHORB': sphorb_stats,
        'OpenCV_ORB': orb_stats,
        'comparison': {
            'speedup_ratio': float(speedup_ratio),
            'target_speedup': 3.0,
            'target_time_ms': float(target_time)
        }
    }

    output_file = f"{output_name}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*70}")
    print(f"Results saved to {output_file}")
    print(f"{'='*70}")

    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main(output_name=sys.argv[1])
    else:
        main(output_name="benchmark_baseline_results")
