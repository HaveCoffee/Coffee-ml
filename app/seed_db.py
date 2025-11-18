from .database import SessionLocal, engine
from . import models

def seed_questions():
    models.Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(models.Question).count() == 0:
            questions_to_add = [
                models.Question(question_text="In one line, how would you introduce yourself?", tag="vibe_summary"),
                models.Question(question_text="What are your top 3 topics or interests you love talking about?", tag="interests"),
                models.Question(question_text="How do you prefer to meet — in-person, virtual, or either?", tag="meeting_style"),
                models.Question(question_text="What's your general availability like? (e.g., 'weekday evenings', 'weekend afternoons')", tag="availability"),
                models.Question(question_text="What's your current goal: friendship, mentorship, collaboration, or casual chat?", tag="social_intent")
            ]
            db.add_all(questions_to_add)
            db.commit()
            print("Database seeded with 5 questions.")
        else:
            print("Questions already exist in the database.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_questions()