from sqlalchemy.orm import Session
from . import models

def create_user(db: Session, name: str):
    """Creates a new user with the given name and returns the user object."""
    db_user = models.User(name=name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def save_user_profile(db: Session, user_id: int, profile_data: dict):
    """Creates or updates a user's profile with the final JSON data."""
    db_profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()

    if db_profile:
        db_profile.profile_data = profile_data
    else:
        db_profile = models.Profile(user_id=user_id, profile_data=profile_data)
        db.add(db_profile)
    
    db.commit()
    return {"status": "success", "user_id": user_id}


def get_all_questions(db: Session):
    """
    Fetches all questions from the database, including their relationships,
    so the assistant knows which are core questions and which are follow-ups.
    """
    questions = db.query(models.Question).order_by(models.Question.id).all()
    question_data = []
    for q in questions:
        question_data.append({
            "id": q.id,
            "text": q.question_text,
            "tag": q.tag,
            "is_core": q.is_core_question,
            "parent_id": q.parent_question_id,
            "trigger": q.trigger_keyword
        })
    return question_data