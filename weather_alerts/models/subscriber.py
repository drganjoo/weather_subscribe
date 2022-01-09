from sqlalchemy import Column, Integer, String
from weather_alerts.database import Base

class Subscriber(Base):
    __tablename__ = 'subscribers'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255))
    
    def __repr__(self):
        return f'Subscriber {self.email!r}>'