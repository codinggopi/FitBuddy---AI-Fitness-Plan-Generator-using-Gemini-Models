from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_json = Column(Text, nullable=False)
    nutrition_tip = Column(Text, nullable=True)
    nutrition_json = Column(Text, nullable=True)  # Store calculated macros
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="plans")

    def __repr__(self):
        return f"<WorkoutPlan id={self.id} user_id={self.user_id}>"
