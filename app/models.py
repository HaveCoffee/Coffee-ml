from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, UniqueConstraint, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB

class SharedUser(Base):
    __tablename__ = "users"
    
    user_id = Column(String(32), primary_key=True)
    mobile_number = Column(String(20), unique=True, nullable=False)
    name = Column(String(255), nullable=True)
    createdAt = Column("createdAt", DateTime(timezone=True))
    updatedAt = Column("updatedAt", DateTime(timezone=True))
    app_user = relationship("AppUser", back_populates="shared_info", uselist=False)

class AppUser(Base):
    __tablename__ = "app_users"
    
    user_id = Column(String(32), ForeignKey("users.user_id"), primary_key=True)
    onboarding_thread_id = Column(String, nullable=True, unique=True)
    shared_info = relationship("SharedUser", back_populates="app_user")
    profile = relationship("Profile", back_populates="app_user", uselist=False, cascade="all, delete-orphan")

class Profile(Base):
    __tablename__ = "profiles"
    user_id = Column(String(32), ForeignKey("app_users.user_id"), primary_key=True)
    profile_data = Column(JSONB)     
    embedding = Column(Vector(384), nullable=True)
    app_user = relationship("AppUser", back_populates="profile")

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(32), ForeignKey("app_users.user_id"), nullable=False)
    match_id = Column(String(32), ForeignKey("app_users.user_id"), nullable=False)
    score = Column(Float, nullable=False)
    status = Column(String(20), default="suggested", nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), onupdate=func.now(), server_default=func.now())
    __table_args__ = (
        UniqueConstraint('user_id', 'match_id', name='unique_match_pair'),
    )

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False, unique=True)
    tag = Column(String, nullable=False)
    is_core_question = Column(Boolean, default=True, nullable=False)
    parent_question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)
    trigger_keyword = Column(String, nullable=True)
    parent = relationship("Question", remote_side=[id], backref="sub_questions")

class InterestTaxonomy(Base):
    __tablename__ = "interest_taxonomy"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)
