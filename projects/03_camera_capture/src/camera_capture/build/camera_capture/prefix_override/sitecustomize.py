import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/opencw/.openclaw/openclaw-ros/projects/03_camera_capture/src/camera_capture/install/camera_capture'
