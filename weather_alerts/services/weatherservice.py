import requests
import typing as t
import datetime
from weather_alerts.app import app
from weather_alerts.services.subscriptionservice import SubscriptionService

class WeatherException(Exception):
    def __init__(self, status_code, error):
        super().__init__()
        self.status_code = status_code
        self.error = error

class WeatherService:
    """A REST based service that can fetch the current weather of a given city"""

    base_url : str = 'https://api.openweathermap.org/data/2.5'
    #api_key : str = '5b77b80f14e25b799dbd2f4ea8616a62'
    api_key : str = app.config['API_KEY']

    def __init__(self):
        pass

    def get_url(self, query : str):
        return f'{WeatherService.base_url}/weather?{query}'
        
    def get_weather(self, city) -> float:
        """Gets the current weather for a city from the Weather API"""
        url = self.get_url(f'q={city}&appid={self.api_key}&units=metric')
        r = requests.get(url)

        if r.status_code == 200:
            data = r.json()
            city_weather = data['main']
            assert(city_weather != None)

            return city_weather['temp']
        else:
            raise WeatherException(r.status_code, "City {city} is not a valid city")


class CityWeather(t.NamedTuple):
    city: str
    temperature: float
    last_fetched: datetime.datetime

class WeatherServiceCache:
    """A caching service for the weather API. This class has a configurable time period
    after which the cache is declared as stale and the Weather API can be used to update the
    weather for all cities that have a subscription"""
    # todo: this needs to come from the config later on
    stale_time = datetime.timedelta(minutes=5)
    weather_service : WeatherService = WeatherService()

    def __init__(self):
        self.clear_cache()

    def clear_cache(self):
        self.city_cache = {}

    def is_stale(self, city) -> bool:
        """Returns whether the cache has stale information about a city"""
        if city not in self.city_cache:
            # any city that we do not have in the cache is stale by default
            return True

        # has the time of last fetch larger than the allowed time?
        city_weather = self.city_cache[city]
        return city_weather.last_fetched - datetime.datetime.now() > WeatherServiceCache.stale_time

    def get_weather(self, city) -> t.Optional[CityWeather]:
        """It can rturn None in case the city is not in the list,"""
        try: 
            return self.city_cache[city]
        except KeyError:
            try:
                # maybe this city has never been seen before, so lets
                # get it from the downstream service
                return self.update_weather(city)
            except WeatherException:
                # we do not deal in this city so can't get the weather for this
                return None

    def update_weather(self, city) -> CityWeather:
        """Can raise WeatherException in case the city is not in the valid cities
        that the downstream WebService deals in"""
        city_temperature = WeatherServiceCache.weather_service.get_weather(city)
        city_weather = CityWeather(city, city_temperature, datetime.datetime.now())
        self.city_cache[city] = city_weather

        return city_weather

    def update_all(self) -> t.List[CityWeather]:
        """Updates all cities weather in the cache"""
        self.clear_cache()
        # get all distinct cities
        sub_service = SubscriptionService()
        # for all cities, get the weather and update the cache
        weather : t.List[CityWeather] = []
        cities = sub_service.get_cities()
        for c in cities:
            try:
                res : CityWeather = self.update_weather(c)
                weather.append(res)
            except WeatherException:
                pass

        return weather
