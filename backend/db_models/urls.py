from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from backend.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class Urls(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("Users", back_populates="urls")