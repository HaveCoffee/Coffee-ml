from sqlalchemy.orm import Session
from . import models

def create_user(db: Session, name: str):
    """Creates a new user with the given name and returns the user object."""
    db_user = models.User(name=name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_all_questions(db: Session):
    """Returns a list of all onboarding questions."""
    return db.query(models.Question).order_by(models.Question.id).all()

def save_user_answer(db: Session, user_id: int, question_id: int, answer_text: str):
    """Saves a user's answer for a specific question."""
    db_answer = models.UserAnswer(
        user_id=user_id,
        question_id=question_id,
        answer_text=answer_text
    )
    db.add(db_answer)
    db.commit()
    return {"status": "success", "answer_id": db_answer.id}