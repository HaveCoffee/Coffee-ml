from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, UniqueConstraint, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB

class User(Base):
    __tablename__ = "users"
    user_id = Column(String(32), primary_key=True, index=True) 
    mobile_number = Column(String(20), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    onboarding_thread_id = Column(String, nullable=True, unique=True)
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
    user_id = Column(String(32), ForeignKey("users.user_id"), primary_key=True)
    profile_data = Column(JSONB)     
    embedding = Column(Vector(384), nullable=True)
    user = relationship("User", back_populates="profile")

class InterestTaxonomy(Base):
    __tablename__ = "interest_taxonomy"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(32), ForeignKey("users.user_id"), nullable=False)
    matched_user_id = Column(String(32), ForeignKey("users.user_id"), nullable=False)
    score = Column(Float, nullable=False)
    # Status: 'suggested' (Screen 1) or 'active' (Screen 2)
    status = Column(String(20), default="suggested", nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), onupdate=func.now(), server_default=func.now())
    # Ensure I don't have duplicate rows for the same person
    __table_args__ = (
        UniqueConstraint('user_id', 'match_id', name='unique_match_pair'),
    )