import typing as t
import os
import sys
import pytest
from sqlalchemy.log import echo_property

# add the parent folder to the python path
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(script_dir)

from weather_alerts.services.backgroundjobs import alert_job

def test_alert():
    try:
        alert_job()
    except Exception as e:
        pytest.fail(f'Unexpected error occured {e}')

if __name__ == "__main__":
    alert_job()

