import weather_alerts.services.subscriptionservice as subscription
import requests as r

email : str = 'fahadzubair@gmail.com'

def exists(email: str):
    response = r.get(f'http://localhost:5000/weather/list?email={email}')
    print(response)

def test_add():
    pass

def test_all_subscriptions():
    # create a subscription to make sure add works
    r.get('http://localhost:5000/weather/list?email=')

    service = subscription.SubscriptionService()
    subscriptions = service.get_all()
    assert list(subscription) > 0, "There should be one subscription at least"

    for s in subscription:
        print(s)


if __name__ == "__main__":
    exists(email)