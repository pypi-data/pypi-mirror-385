#!/usr/bin/env python3
"""
Test script to reproduce the segmentation fault bug when reinitializing SPHORB.

Bug description:
- Create a SPHORB object
- Don't properly delete it
- Create another SPHORB object
- Call detectAndCompute -> segmentation fault
"""
import cv2
import pysphorb
import numpy as np
import gc

def test_reinitialization_bug():
    """Test case that should trigger the segmentation fault"""
    print("Testing SPHORB reinitialization bug...")

    # Create a simple test image
    test_image = np.random.randint(0, 255, (500, 1000, 3), dtype=np.uint8)

    print("1. Creating first SPHORB instance...")
    sorb1 = pysphorb.SPHORB()

    print("2. Running detectAndCompute with first instance...")
    kp1, desc1 = sorb1.detectAndCompute(test_image)
    print(f"   Found {len(kp1)} keypoints")

    print("3. Creating second SPHORB instance (without explicitly deleting first)...")
    sorb2 = pysphorb.SPHORB()

    print("4. Running detectAndCompute with second instance...")
    print("   This should trigger segmentation fault if bug exists...")
    kp2, desc2 = sorb2.detectAndCompute(test_image)
    print(f"   Found {len(kp2)} keypoints")

    print("5. Test passed! No segmentation fault occurred.")

    # Clean up
    del sorb1
    del sorb2

    print("6. Cleanup completed.")

def test_multiple_instances():
    """Test creating multiple SPHORB instances sequentially"""
    print("\nTesting multiple SPHORB instances...")

    test_image = np.random.randint(0, 255, (500, 1000, 3), dtype=np.uint8)

    for i in range(3):
        print(f"\nIteration {i+1}:")
        sorb = pysphorb.SPHORB()
        kp, desc = sorb.detectAndCompute(test_image)
        print(f"  Found {len(kp)} keypoints")
        del sorb

    print("\nMultiple instances test passed!")

def test_concurrent_instances():
    """Test having multiple SPHORB instances at the same time"""
    print("\nTesting concurrent SPHORB instances...")

    test_image = np.random.randint(0, 255, (500, 1000, 3), dtype=np.uint8)

    print("Creating 3 instances simultaneously...")
    sorb1 = pysphorb.SPHORB()
    sorb2 = pysphorb.SPHORB()
    sorb3 = pysphorb.SPHORB()

    print("Running detectAndCompute on instance 1...")
    kp1, desc1 = sorb1.detectAndCompute(test_image)
    print(f"  Found {len(kp1)} keypoints")

    print("Running detectAndCompute on instance 2...")
    kp2, desc2 = sorb2.detectAndCompute(test_image)
    print(f"  Found {len(kp2)} keypoints")

    print("Running detectAndCompute on instance 3...")
    kp3, desc3 = sorb3.detectAndCompute(test_image)
    print(f"  Found {len(kp3)} keypoints")

    print("Cleaning up instances...")
    del sorb1, sorb2, sorb3
    gc.collect()

    print("Concurrent instances test passed!")

def test_reassignment():
    """Test reassigning the same variable without explicit deletion"""
    print("\nTesting variable reassignment (simulating 'improper deletion')...")

    test_image = np.random.randint(0, 255, (500, 1000, 3), dtype=np.uint8)

    print("Creating first SPHORB instance...")
    sorb = pysphorb.SPHORB()
    kp1, desc1 = sorb.detectAndCompute(test_image)
    print(f"  Found {len(kp1)} keypoints")

    print("Reassigning same variable to new SPHORB (old instance should be auto-deleted)...")
    sorb = pysphorb.SPHORB()  # Reassignment without explicit del

    print("Running detectAndCompute on new instance...")
    kp2, desc2 = sorb.detectAndCompute(test_image)
    print(f"  Found {len(kp2)} keypoints")

    print("Reassignment test passed!")

if __name__ == "__main__":
    try:
        test_reinitialization_bug()
        test_multiple_instances()
        test_concurrent_instances()
        test_reassignment()
        print("\n✓ All tests passed successfully!")
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        raise
