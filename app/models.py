from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
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
    is_core_question = Column(Boolean, default=True)
    parent_question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)
    trigger_keyword = Column(String, nullable=True)
    parent = relationship("Question", remote_side=[id], backref="sub_questions")

class Profile(Base):
    __tablename__ = "profiles"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    profile_data = Column(JSONB)     
    user = relationship("User", back_populates="profile")