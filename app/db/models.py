from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from .engine import engine

Base = declarative_base()


class Workout(Base):
    """ Workout session model """
    __tablename__ = 'workout'

    id = Column(Integer, primary_key=True, autoincrement=True)
    barcode = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    location = Column(String, nullable=False)

    # The start time of the workout session
    time = Column(TIMESTAMP(timezone=True), nullable=False)

    # The duration of the workout session
    duration = Column(Integer, nullable=False)

    # The number of spaces still available in the workout session
    available = Column(Integer, nullable=False)

    # When the data point was collected
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    @staticmethod
    def from_dict(data: dict):
        """ Create workout record from the dictionary that was scraped """
        return Workout(
            barcode=data['id'],
            title=data['title'],
            location=data['location'],
            time=datetime.fromisoformat(data['time']),
            duration=data['duration'],
            available=data['available'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )

    def to_dict(self) -> dict:
        """ Create dict from a workout record """
        return {
            'id': self.id,
            'barcode': self.barcode,
            'title': self.title,
            'location': self.location,
            'time': self.time.isoformat(),
            'duration': self.duration,
            'available': self.available,
            'timestamp': self.timestamp.isoformat(),
        }


Base.metadata.create_all(bind=engine)