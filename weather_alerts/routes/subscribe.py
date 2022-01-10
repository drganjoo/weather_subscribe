import typing as t
from flask import Flask,Blueprint, request, jsonify
from weather_alerts.exceptions import MissingFieldsException, NotFoundException
from weather_alerts.services.subscriptionservice import ActiveSubscription, SubscriptionService
from ..commontypes import FormField
from ..common import get_fields

"""A route to handle all subscription related APIs"""

bp = Blueprint('weather', __name__, url_prefix='/weather')

# list of valid_cities that we have seen in the past, in case of
# a new city we will first check with the downstreeam service
# to make sure the city is valid
city_cache : t.List[str] = []

subscription_service = SubscriptionService()

@bp.route('/subscribe', methods=['POST'])
def register() -> t.Dict[str, t.Any]:
    """Subscribes an email address with a city's weather. The given minimum temperature
    is saved to raise an alarm through the background service
    
    :param email: email address to send notifications to
    :param city: city whose weather is to be monitored
    :param minTemperature: the minimum temperature below which an alarm should be sent
    """
    # make sure all input fields are present. The common function will raise
    # an exception in case any mandatory field is missing
    email, city, min_temperature = get_fields(request, [
        FormField('email', 'email', True),
        FormField('city', 'city', True),
        FormField('minTemperature', 'maximum temperature', True),
        ])

    # ensure that the city is a valid city in which the weather API deals
    if city not in city_cache:
        # todo: lookup from the weather api and make sure city exists
        city_cache.append(city)

    # add the subscription using the subscription service
    result = subscription_service.add(email, city, min_temperature)
    return {
        'subscriberId': result.subscriber_id,
        'subscriptionId' : result.subscription_id
    }

@bp.route('/subscribe', methods=['DELETE'])
def delete() -> t.Dict[str, t.Any]:
    """Deletes the given subscription for the email and city"""
    email, city = get_fields(request, [
        FormField('email', 'email', True),
        FormField('city', 'city', True),
        ])

    # delete the subscription. Keep the subscriber in the database even
    # though the subscriber might have no more subscriptions
    subscription_service.delete(email, city)
    return {
        'status': f'{city} has been removed from {email}',
    }

@bp.route('/subscribe', methods=['PUT'])
def update() -> t.Dict[str, t.Any]:
    """Updates a subscription for a given email address and city"""
    email, city, min_temperature = get_fields(request, [
        FormField('email', 'email', True),
        FormField('city', 'city', True),
        FormField('minTemperature', 'maximum temperature', True),
        ])

    result = subscription_service.update(email, city, min_temperature)
    return {
        'subscriberId': result.subscriber_id,
        'subscriptionId' : result.subscription_id
    }

@bp.route('/list', methods=['GET'])
def list() -> t.Dict[str, t.Any]:
    """All subscriptons of a given email addresses are returned
    NotFoundException is raised in case the email address is not found
    MissingFieldException is raised in case email query is not found in the url
    An empty list is sent back in case email exists but no subscriptions are there"""
    email = request.args.get('email')
    if not email:
        raise MissingFieldsException([FormField('email', 'email of subscription', True)])

    subscriber_id, subscriptions = subscription_service.get_subscriptions(email)
    subscriptions_json = [{
        'subscriptionId' : r.subscription_id, 
        'city': r.city, 
        'minTemperature' : r.min_temperature
        } for r in subscriptions]

    return {
        'subscriberId' : subscriber_id,
        'subscriptions': subscriptions_json
    }

@bp.route('/subscriptions', methods=['GET'])
def all_subscriptions() -> t.Dict[str, t.Any]:
    """Returns all subscriptions in the system. This is just for internal use
    and checks  on remote IP addresses can be used later on"""
    subscribers = subscription_service.get_all()
    return [s.to_json() for s in  subscribers]
    
def register_routes(app: Flask):
    """Register the route with the given app"""
    app.register_blueprint(bp)