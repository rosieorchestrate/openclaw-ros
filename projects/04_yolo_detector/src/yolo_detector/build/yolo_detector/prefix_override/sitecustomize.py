import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/opencw/.openclaw/openclaw-ros/projects/04_yolo_detector/src/yolo_detector/install/yolo_detector'
