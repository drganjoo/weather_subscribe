import typing as t
from apscheduler.schedulers.background import BackgroundScheduler
from weather_alerts.services.alertservice import AlertService
from ..services.subscriptionservice import ActiveSubscription, CityAlert, SubscriptionService
from ..services.weatherservice import CityWeather, WeatherException, WeatherServiceCache
from ..logger import Logger

log = Logger(__name__)

"""To keep things simple BackgroundScheduler is being used otherwise in production
Celery or Kafka would be preferred to do this"""

def alert_job():
    """Alert Job routinely checks all subscriptions against the current weather of the
    subscrbed city and sends out an alert (using the AlertService) if the city weather
    is below the minimum temperature"""
    log.info('Alert job running')

    service = SubscriptionService()
    cities : t.List[str] = service.get_cities()

    weather_service = WeatherServiceCache()

    # update cache for any city that has stale weather
    for city_alert in cities:
        if weather_service.is_stale(city_alert):
            try:
                weather_service.update_weather(city_alert)
            except WeatherException as e:
                log.error(f'{city_alert} is not valid. error: {e}')

    alert_service = AlertService()
    subscribers : t.List[ActiveSubscription] = service.get_all()

    # go over all subscribers' subscriptions, combine all of the 
    # alerted ones and then tell the notifier to issue notification
    for sub in subscribers:
        # cities that are alarmed for this subscriber
        alarmed : t.List[CityAlert] = []

        # go over all subscribed cities  and add them to alarmed in case
        # their temperature is < the alert temperature
        for city_alert in sub.subscriptions:
            city_weather : t.Optional[CityWeather] = weather_service.get_weather(city_alert)
            if city_weather and city_weather.temperature < city_alert.min_temperature:
                alarmed.append(city_alert)

        # send an alert in case one city is alarmed
        if len(alarmed) > 0:
            alert_service.notify(sub.email, alarmed)


sched = BackgroundScheduler(daemon=True)

def setup_jobs(interval_seconds : int = 60) -> None:
    # todo: check to make sure job is not inserted twice
    sched.add_job(alert_job, 'interval', seconds = interval_seconds)
