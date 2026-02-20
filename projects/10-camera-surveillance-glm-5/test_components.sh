#!/bin/bash
# Test individual components of the surveillance system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "Testing Surveillance System Components"
echo "========================================"
echo ""

# Test 1: Camera Capture
echo "📷 TEST 1: Camera Capture"
echo "--------------------------"
python3 src/camera_capture.py
if [ $? -eq 0 ]; then
    echo "✅ Camera capture: PASSED"
else
    echo "❌ Camera capture: FAILED"
fi
echo ""

# Test 2: Person Detection (create a test image first)
echo "🔍 TEST 2: Person Detection"
echo "---------------------------"
if [ -f "test_capture.jpg" ]; then
    python3 src/person_detector.py test_capture.jpg
    if [ $? -eq 0 ]; then
        echo "✅ Person detection: PASSED"
    else
        echo "❌ Person detection: FAILED"
    fi
else
    echo "⚠️  No test image available (run camera test first)"
fi
echo ""

# Test 3: Notification Handler
echo "📧 TEST 3: Notification Handler"
echo "-------------------------------"
python3 src/notification_handler.py
if [ $? -eq 0 ]; then
    echo "✅ Notification handler: PASSED"
else
    echo "❌ Notification handler: FAILED"
fi
echo ""

# Summary
echo "========================================"
echo "Test Complete"
echo "========================================"
ls -la logs/ 2>/dev/null && echo ""
ls -la captures/ 2>/dev/null && echo ""