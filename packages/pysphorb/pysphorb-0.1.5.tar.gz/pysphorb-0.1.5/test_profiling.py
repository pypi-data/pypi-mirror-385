#!/usr/bin/env python3
"""Test script to see profiling output from C++ code"""
import sys
# Remove source directory from path to avoid importing from source
sys.path = [p for p in sys.path if 'pysphorb' not in p or 'site-packages' in p]

import os
import pysphorb
import cv2

print("Loading image...")
img = cv2.imread('/home/sehyuncha/workspace/pysphorb/images/frame_000000.png')
print(f"Image shape: {img.shape}")

print("\nCreating SPHORB detector...")
sorb = pysphorb.SPHORB()

print("\nRunning detectAndCompute...")
kp, desc = sorb.detectAndCompute(img)
print(f"Found {len(kp)} keypoints")

print("\n=== Profiling Files ===")
os.system("cat /tmp/sphorb_detectAndCompute_called.txt 2>/dev/null || echo 'No diagnostic file'")
os.system("cat /tmp/pysphorb_profile.log 2>/dev/null || echo 'No profile log'")
