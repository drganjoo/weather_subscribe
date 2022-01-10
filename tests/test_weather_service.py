import typing as t
import os
import sys
import pytest
from sqlalchemy.log import echo_property

# add the parent folder to the python path
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(script_dir)

from weather_alerts.exceptions import NotFoundException
from weather_alerts.services.weatherservice import WeatherService, WeatherServiceCache
import requests as r

service = WeatherServiceCache()
show_output = False

def test_api():
    try:
        city = 'London'
        res = service.get_weather(city)
        assert res != None, "City weather could not be retrieved"

        if show_output:
            print(f'Weather id {city} is {res}')
    except Exception as e:
        pytest.fail(f'api call failed {e}')

def test_update():
    try:
        updated = service.update_all()

        if show_output:
            print(updated)
    except Exception as e:
        pytest.fail(f'update_all failed')

if __name__ == "__main__":
    show_output = True
    test_api()
    test_update()
