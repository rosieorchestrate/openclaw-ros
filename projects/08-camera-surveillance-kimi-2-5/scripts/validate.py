#!/usr/bin/env python3
"""
Quick validation test for camera surveillance system.
Run this after setup to verify all components work.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and report result."""
    print(f"\n🧪 Testing: {description}")
    print(f"   Command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"   ✅ PASS")
            return True
        else:
            print(f"   ❌ FAIL: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False


def main():
    print("=" * 60)
    print("🔍 Camera Surveillance System - Validation Test")
    print("=" * 60)
    
    project_dir = Path(__file__).parent.parent
    results = []
    
    # Test 1: Check directory structure
    print("\n📁 Checking directory structure...")
    required_dirs = ['src', 'logs', 'captures', 'models', 'scripts']
    for d in required_dirs:
        path = project_dir / d
        if path.exists():
            print(f"   ✅ {d}/")
        else:
            print(f"   ❌ {d}/ (missing)")
            results.append(False)
    
    # Test 2: Verify camera access
    results.append(run_command(
        ['cam', '--list'],
        "Camera detection"
    ))
    
    # Test 3: Check ROS2
    results.append(run_command(
        ['bash', '-c', 'source /opt/ros/kilted/local_setup.bash && ros2 --help'],
        "ROS2 availability"
    ))
    
    # Test 4: Check executables
    install_dir = project_dir / 'install'
    if install_dir.exists():
        print("\n📦 Checking executables...")
        for exe in ['camera_node', 'detector_node', 'email_node']:
            exe_path = install_dir / 'camera_surveillance' / 'bin' / exe
            if exe_path.exists():
                print(f"   ✅ {exe}")
            else:
                print(f"   ❌ {exe} (missing - run spinup.sh)")
                results.append(False)
    else:
        print("\n⚠️  Install directory not found. Run ./scripts/spinup.sh first.")
        results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    passed = results.count(True)
    total = len(results)
    
    if passed == total:
        print(f"✅ All tests passed! ({passed}/{total})")
        print("\n🚀 Ready to launch:")
        print("   cd ~/.openclaw/openclaw-ros/projects/08-camera-surveillance-kimi-2-5")
        print("   source install/local_setup.bash")
        print("   ros2 launch camera_surveillance surveillance.launch.py")
        return 0
    else:
        print(f"⚠️  Some tests failed: {passed}/{total} passed")
        print("\n🔧 Run setup:")
        print("   ./scripts/spinup.sh")
        return 1


if __name__ == '__main__':
    sys.exit(main())
