from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql.schema import ForeignKey
from weather_alerts.database import Base

class Subscription(Base):
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True)
    subscriber_id = Column(Integer, ForeignKey('subscribers.id'))
    city = Column(String(163))
    min_temp = Column(Float, default = 0.0)

    def __repr__(self):
        return f'Subscription {self.email!r}>'