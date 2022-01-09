import typing as t
from psycopg2.errors import NotNullViolation, UniqueViolation
from flask import Flask,Blueprint, request
from sqlalchemy.exc import IntegrityError
from .database import db_session
from .commontypes import FormField
from .common import get_fields
from .models import Subscription, Subscriber
from .exceptions import AlreadyExistsException, ApiException, StorageException
from .logger import Logger

bp = Blueprint('weather', __name__, url_prefix='/weather')
log = Logger(__name__)

# list of valid_cities that we have seen in the past, in case of
# a new city we will first check with the downstreeam service
# to make sure the city is valid
city_cache = []

@bp.route('/register', methods=['POST'])
def register():
    email, city, temperature = get_fields(request, [
        FormField('email', 'email', True),
        FormField('city', 'city', True),
        FormField('maxTemperature', 'maximum temperature', True),
        ])

    if city not in city_cache:
        # todo: lookup from the weather api and make sure city exists
        city_cache.append(city)

    # get the subscriber ID for this email if one exists or create a new
    # subscriber otherwise
    subscriber = Subscriber.query.filter(Subscriber.email == email).first()
    if not subscriber:
        #subscriber = Subscriber(email)
        db_session.add(subscriber := Subscriber(email))

    subscription = Subscription(subscriber.id, city, temperature)
    db_session.add(subscription)
    try:
        db_session.commit()
        return {
            "subscriberId": subscriber.id,
            "subscriptionId" : subscription.id
        }
    except IntegrityError as e:
        if e.orig == UniqueViolation:
            log.warn(str(e))
            raise AlreadyExistsException(f"Subscriber {email} is already registered for {city}")
        else:
            support_id = log.error(str(e))
            raise StorageException(support_id)

def register_routes(app: Flask):
    app.register_blueprint(bp)