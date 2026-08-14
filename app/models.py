from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String

from app.database import Base


class PredictionLog(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    input_data = Column(JSON)
    prediction = Column(String)
    confidence = Column(Float)
    latency_ms = Column(Float)
    model_version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
