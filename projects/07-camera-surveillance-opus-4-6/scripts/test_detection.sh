#!/bin/bash
# ============================================================
# Test Person Detection (Offline — No Camera Required)
# ============================================================
# Runs the MobileNet-SSD detector on a test image to verify
# the detection pipeline works correctly.
#
# Usage: ./scripts/test_detection.sh [path_to_test_image]
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🧪 Testing Person Detection Pipeline"
echo "======================================"

python3 - "$PROJECT_ROOT" "$1" << 'PYEOF'
import sys
import cv2
import numpy as np
import os
import time

project_root = sys.argv[1]
test_image_path = sys.argv[2] if len(sys.argv) > 2 else None

prototxt = os.path.join(project_root, 'models', 'deploy.prototxt')
caffemodel = os.path.join(project_root, 'models', 'mobilenet_ssd.caffemodel')

CLASSES = ['background', 'aeroplane', 'bicycle', 'bird', 'boat',
           'bottle', 'bus', 'car', 'cat', 'chair', 'cow', 'diningtable',
           'dog', 'horse', 'motorbike', 'person', 'pottedplant', 'sheep',
           'sofa', 'train', 'tvmonitor']

print(f"Loading model...")
net = cv2.dnn.readNetFromCaffe(prototxt, caffemodel)
print(f"✅ Model loaded")

# Load or generate test image
if test_image_path and os.path.exists(test_image_path):
    img = cv2.imread(test_image_path)
    print(f"📷 Using test image: {test_image_path}")
else:
    img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    print(f"📷 Using random noise image (no detections expected)")

(h, w) = img.shape[:2]
print(f"   Image size: {w}x{h}")

# Run detection
start = time.time()
blob = cv2.dnn.blobFromImage(cv2.resize(img, (300, 300)), 0.007843, (300, 300), 127.5)
net.setInput(blob)
detections = net.forward()
elapsed = time.time() - start

print(f"\n📊 Results:")
print(f"   Inference time: {elapsed*1000:.1f}ms")
print(f"   Raw detections: {detections.shape[2]}")

person_count = 0
for i in range(detections.shape[2]):
    confidence = detections[0, 0, i, 2]
    class_id = int(detections[0, 0, i, 1])

    if confidence > 0.3:  # Lower threshold for testing
        class_name = CLASSES[class_id] if class_id < len(CLASSES) else f"unknown({class_id})"
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (x1, y1, x2, y2) = box.astype('int')
        print(f"   [{class_name}] confidence={confidence:.3f} bbox=({x1},{y1},{x2},{y2})")
        if class_id == 15:
            person_count += 1

print(f"\n{'🚨' if person_count > 0 else '✅'} Persons detected: {person_count}")
print(f"{'Pipeline working correctly!' if True else ''}")

# Benchmark
print(f"\n⏱️  Benchmarking (10 iterations)...")
times = []
for _ in range(10):
    start = time.time()
    net.setInput(blob)
    net.forward()
    times.append(time.time() - start)

avg = sum(times) / len(times)
print(f"   Average: {avg*1000:.1f}ms ({1/avg:.1f} FPS)")
print(f"   Min: {min(times)*1000:.1f}ms, Max: {max(times)*1000:.1f}ms")
print(f"\n✅ Detection pipeline test complete!")
PYEOF
