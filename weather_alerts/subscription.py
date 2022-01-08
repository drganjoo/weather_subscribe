from sqlalchemy import Column, Integer, String, Float
from weather_alerts.database import Base

class Subscription(Base):
    __tablename__ = 'subscription'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    city = Column(String(163))
    max_temp = Column(Float, default = 0.0)

    def __init__(self, id, email, city, max_temp):
        self.id = id
        self.email = email
        self.city = city
        self.max_temp = max_temp

    def __repr__(self):
        return f'Subscription {self.email!r}>'