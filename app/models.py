from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from sqlalchemy.dialects.postgresql import JSONB

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    created_at = Column(String, server_default=func.now())
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False, unique=True)
    tag = Column(String, nullable=False)

class Profile(Base):
    __tablename__ = "profiles"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    profile_data = Column(JSONB)    # This column will store the entire structured JSON from the agent
    user = relationship("User", back_populates="profile")