import typing as t
import os
import sys
import pytest
from sqlalchemy.log import echo_property

# add the parent folder to the python path
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(script_dir)

from weather_alerts.exceptions import NotFoundException
from weather_alerts.services.subscriptionservice import SubscriptionService
import requests as r

service = SubscriptionService()
email = 'fahadzubair@gmail.com'
city  = 'London'

def exists(email : str):
    try:
        service.get_subscriber_id(email)
        return True
    except NotFoundException:
        return False
    
def delete(email : str):
    try:
        service.delete_subscriber(email)
    except NotFoundException:
        pass

def test_add():
    try:
        if exists(email):
            delete(email)

        service.add(email, city, 10.0)
    except Exception as e:
        pytest.fail(f'Unexpected error occured {e}')

def test_all_subscriptions():
    try:
        subscriptions = service.get_all()
    except Exception as e:
        pytest.fail(f'Unexpected error occured on test_all_subscriptions {e}')

if __name__ == "__main__":
    email = 'fahadzubair@gmail.com'
    test_add()
    email = 'dosra@gmail.com'
    test_add()
    test_all_subscriptions()