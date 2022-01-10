from re import sub
import typing as t
from sqlalchemy.sql.sqltypes import Boolean
from werkzeug.exceptions import NotFound
from weather_alerts.models import Subscription
from psycopg2.errors import NotNullViolation, UniqueViolation
from sqlalchemy.exc import IntegrityError
from ..database import db_session
from ..models import Subscription, Subscriber
from ..logger import Logger
from ..exceptions import AlreadyExistsException, ApiException, NotFoundException, StorageException

log = Logger(__name__)

class RegisterResult(t.NamedTuple):
    """When a subscriber is added to the database, this is returned"""
    subscriber_id : int
    subscription_id : int

class CityAlert(t.NamedTuple):
    """Represents an alert that has been set for a particular city"""
    subscription_id : int
    city: str
    min_temperature : float

    def to_json(self):
        # todo: this has to go into a seperate serializer but to keep 
        # things simple it has been defined here
        return {
            'subscriptionId' : self.subscription_id,
            'city': self.city,
            'minTemperature': self.min_temperature
        }

class ActiveSubscription(t.NamedTuple):
    """All subscriptions of a given email address are represented by this"""
    subscriber_id: int
    email: str
    subscriptions: t.List[CityAlert]

    def to_json(self):
        return {
            'subscriberId' : self.subscriber_id,
            'email' : self.email,
            'subscriptions': [s.to_json() for s in self.subscriptions]
        }

SubscriptionList = t.List[Subscription]

class SubscriptionService:
    """ScubscriptionService allows adding, updating, deleting and quering city weather
    related alerts.
    
    Usually you create a :class:`SubscriptionService` instance to carry out the functionality"""

    def add(self, email: str, city: str, min_temperature: float) -> RegisterResult:
        """Adds a given subcriber email address to the given city"""
        # find subscriber ID for this emmail
        subscriber : Subscriber = Subscriber.query.filter(Subscriber.email == email).first()

        try:
            # register a new subscriber in case it was not already found in the system
            if not subscriber:
                subscriber = Subscriber(email)
                db_session.add(subscriber)
                # flush to the database so that we can get the subscriber ID
                db_session.flush()

            # add a new subscription for this subscriber
            subscription :Subscription = Subscription(subscriber.id, city, min_temperature)
            db_session.add(subscription)
            db_session.commit()

            return RegisterResult(subscriber_id = subscriber.id, subscription_id = subscription.id)
        except IntegrityError as e:
            # it is ok to have a unique voilation in the system so we handle that separately
            # but if there are other database related errors, then those need to be dealt
            # with separately
            if isinstance(e.orig, UniqueViolation):
                log.warn(str(e))
                raise AlreadyExistsException(f"Subscriber {email} is already registered for {city}")
            else:
                raise e

    def delete(self, email: str, city: str) -> None:
        """Adds a given subcriber email address to the given city"""

        subscriber = Subscriber.query.filter(Subscriber.email == email).first()
        if not subscriber:
            raise NotFoundException('{email} addreess is not registered')

        result = db_session.query(Subscription).filter(Subscription.city == city, 
            Subscription.subscriber_id == subscriber.id).delete()
        if result == 0:
            raise NotFoundException(f'A subscription to {city} not found for {email}')

        db_session.commit()


    def update(self, email: str, city: str, min_temperature : float) -> RegisterResult:
        """Change subscription criteria for the given email and city"""
        subscriber = db_session.query(Subscriber).filter(Subscriber.email == email).first()
        if not subscriber:
            raise NotFoundException('{email} addreess is not registered')

        subscription = db_session.query(Subscription).filter(Subscription.city == city, 
            Subscription.subscriber_id == subscriber.id).first()
        if not subscription:
            raise NotFoundException(f'A subscription to {city} not found for {email}')

        subscription.min_temperature = min_temperature
        db_session.commit()

        return RegisterResult(subscriber_id = subscriber.id, subscription_id = subscription.id)


    def get_subscriptions(self, email): #-> t.Tuple(int, t.List(CityAlert)):
        subscriber = db_session.query(Subscriber).filter(Subscriber.email == email).first()
        if not subscriber:
            raise NotFoundException(f'{email} address is not registered')

        rows = db_session.query(Subscription).filter(Subscription.subscriber_id == subscriber.id).all()
        return subscriber.id, [CityAlert(r.id, r.city, r.min_temperature) for r in rows]
        
    def get_cities(self) -> t.List[str]:
        """returns distinct cities in the database"""
        return [r.city for r in db_session.query(Subscription.city).distinct()]

    def get_subscriber_id(self, email: str) -> int: 
        subscriber : Subscriber = Subscriber.query.filter(Subscriber.email == email).first()
        if not subscriber:
            raise NotFoundException('{email} addreess is not registered')
        return subscriber.id

    def get_all(self) -> t.List[ActiveSubscription]:
        """Returns all of the active subcriptions that exist in the system"""
        # get all active subcribers that have a subscription in the system
        subscriptions_query = db_session.query(Subscriber).join(
            Subscription, Subscriber.subscriptions
            ).order_by(Subscriber.email)

        subscribers = subscriptions_query.all()
        active_subscribers : t.List[ActiveSubscription]= []

        # go over all subscribers and get their subscriptions
        for s in subscribers:
            subscriptions = []
            # convert all subscriptions into CityAlert object
            for c in s.subscriptions:
                subscriptions.append(CityAlert(
                    city = c.city,
                    subscription_id = c.id,
                    min_temperature = c.min_temperature))
        
            active_subscribers.append(ActiveSubscription(
                subscriber_id = s.id,
                email = s.email,
                subscriptions = subscriptions
                ))
                
        return active_subscribers

    def delete_subscriber(self, email: str):
        """Delete all subscriber and all of the subscriptions that have been added"""
        subscriber : Subscriber = Subscriber.query.filter(Subscriber.email == email).first()
        if not subscriber:
            raise NotFoundException('{email} addreess is not registered')

        Subscription.query.filter(Subscription.subscriber_id == subscriber.id).delete()
        db_session.delete(subscriber)
        db_session.commit()
                            
