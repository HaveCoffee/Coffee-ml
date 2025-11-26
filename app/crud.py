from sqlalchemy.orm import Session
from . import models

def get_user(db: Session, user_id: int):
    """Finds a user by their primary key ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_thread_id(db: Session, thread_id: str):
    """Finds a user by their associated onboarding thread ID."""
    return db.query(models.User).filter(models.User.onboarding_thread_id == thread_id).first()

def link_thread_to_user(db: Session, user_id: int, thread_id: str):
    """Saves the thread_id to the user's record in the database."""
    user = get_user(db, user_id)
    if user:
        user.onboarding_thread_id = thread_id
        db.commit()
        return user
    return None

def get_user_profile(db: Session, user_id: int):
    """
    Retrieves the profile for a given user_id.
    """
    return db.query(models.Profile).filter(models.Profile.user_id == user_id).first()

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