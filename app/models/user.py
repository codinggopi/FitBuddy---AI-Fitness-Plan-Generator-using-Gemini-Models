from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    height = Column(Float, nullable=True, default=175.0)
    gender = Column(String(20), nullable=True, default="other")  # male, female, other
    goal = Column(String(100), nullable=False)
    intensity = Column(String(50), nullable=False)
    equipment = Column(String(100), nullable=True, default="Full Commercial Gym")
    dietary_preference = Column(String(100), nullable=True, default="Standard / Balanced")
    injuries = Column(String(255), nullable=True, default="None")
    created_at = Column(DateTime, default=datetime.utcnow)

    plans = relationship("WorkoutPlan", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} name='{self.name}' goal='{self.goal}'>"
