import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/opencw/.openclaw/openclaw-ros/projects/05_surveillance_pro/src/surveillance_logic/install/surveillance_logic'
