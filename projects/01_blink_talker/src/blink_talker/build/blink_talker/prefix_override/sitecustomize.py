import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/opencw/.openclaw/openclaw-ros/projects/01_blink_talker/src/blink_talker/install/blink_talker'
