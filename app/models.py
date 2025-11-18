from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    created_at = Column(String, server_default=func.now())

    # This relationship links a user to all their answers
    answers = relationship("UserAnswer", back_populates="user")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False, unique=True)
    # A tag to map this question to our target JSON structure
    tag = Column(String, nullable=False)

class UserAnswer(Base):
    __tablename__ = "user_answers"
    id = Column(Integer, primary_key=True, index=True)
    answer_text = Column(Text, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))

    # Relationships back to the parent tables
    user = relationship("User", back_populates="answers")
    question = relationship("Question", back_populates="answers")

# Add this to the Question model to link back to answers
Question.answers = relationship("UserAnswer", back_populates="question")