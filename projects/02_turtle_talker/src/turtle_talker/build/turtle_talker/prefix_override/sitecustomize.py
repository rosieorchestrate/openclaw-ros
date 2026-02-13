import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/opencw/.openclaw/openclaw-ros/projects/02_turtle_talker/src/turtle_talker/install/turtle_talker'
