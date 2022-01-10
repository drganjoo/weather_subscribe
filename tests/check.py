import os
import sys

# add the parent folder to the python path
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(script_dir)

import weather_alerts
