from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from weather_alerts.database import Base

"""Database related model classes are defined here"""
class Subscriber(Base):
    """Represents a subscriber in the system"""
    __tablename__ = 'subscribers'
    
    id = Column(Integer, primary_key = True, nullable = False)
    email = Column(String(255), nullable = False)

    subscriptions = relationship('Subscription', back_populates='subscriber')
    
    def __init__(self, email: str):
        self.email = email

    def __repr__(self):
        return f'Subscriber {self.id}, {self.email!r}>'


class Subscription(Base):
    """Represents a subscription to a city's weather by a subscriber"""
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key = True, nullable = False)
    subscriber_id = Column(Integer, ForeignKey('subscribers.id'), nullable = False)
    city = Column(String(163), nullable = False)
    min_temperature = Column(Float, default = 0.0, nullable = False)
    subscription_date = Column(DateTime, nullable = False, default = datetime.utcnow)

    __table_args__ = (UniqueConstraint(subscriber_id, city), {})

    subscriber = relationship('Subscriber', back_populates=('subscriptions'))

    def __init__(self, subscriber_id : int, city: str, min_temperature: float):
        self.subscriber_id = subscriber_id
        self.city = city
        self.min_temperature = min_temperature

    def __repr__(self):
        return f'Subscription {self.id}, subscriber_id={self.subscriber_id}, city={self.city}, \
            min_temp={self.min_temperature}'