from sqlalchemy import Column, Integer, String, DateTime
from backend.database import Base
from datetime import datetime


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String, unique=False, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
