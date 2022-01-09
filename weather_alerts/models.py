from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from weather_alerts.database import Base

class Subscriber(Base):
    __tablename__ = 'subscribers'
    
    id = Column(Integer, primary_key = True, nullable = False)
    email = Column(String(255), nullable = False)

    subscriptions = relationship('Subscription', back_populates='subscriber')
    
    def __init__(self, email):
        self.email = email

    def __repr__(self):
        return f'Subscriber {self.email!r}>'


class Subscription(Base):
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key = True, nullable = False)
    subscriber_id = Column(Integer, ForeignKey('subscribers.id'), nullable = False)
    city = Column(String(163), nullable = False)
    min_temp = Column(Float, default = 0.0, nullable = False)
    subscription_date = Column(DateTime, nullable = False, default = datetime.utcnow)

    subscriber = relationship('Subscriber', back_populates=('subscriptions'))

    def __init__(self, subscriber_id, city, min_temp):
        self.subscriber_id = subscriber_id
        self.city = city
        self.min_temp = min_temp

    def __repr__(self):
        return f'Subscription {self.email!r}>'        