from .database import SessionLocal, engine, Base
from .models import Question

def seed_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(Question).count() == 0:
            q_intro = Question(id=1, question_text="In one line, how would you introduce yourself?", tag="bio_short", is_core_question=True)
            q_age = Question(id=2, question_text="Which age band fits you?", tag="age_band", is_core_question=True)
            q_gender = Question(id=3, question_text="How should we note your gender, or should we skip it?", tag="gender", is_core_question=True)
            q_location = Question(id=4, question_text="What city or pincode would you like to meet in?", tag="city", is_core_question=True)
            q_meet_type = Question(id=5, question_text="How do you prefer to meet — in-person, virtual, or either?", tag="meet_type", is_core_question=True)
            q_topics = Question(id=6, question_text="Pick your top 3 topics you love talking about. Some examples are books, movies, sports, tech, or travel.", tag="interest_ids", is_core_question=True)
            q_goal = Question(id=7, question_text="What's your current goal: friendship, mentorship, collaboration, or casual chat?", tag="goal_id", is_core_question=True)
            q_preferences = Question(id=8, question_text="Any age/gender preferences for who you meet?", tag="preferred_age_min_max", is_core_question=True)
            q_availability = Question(id=9, question_text="When are you usually free?", tag="time_buckets", is_core_question=True)
            q_spots = Question(id=10, question_text="What are some of your favorite meet spots near you?", tag="venue_types", is_core_question=True)

            db.add_all([q_intro, q_age, q_gender, q_location, q_meet_type, q_topics, q_goal, q_preferences, q_availability, q_spots])
            db.commit()

            follow_up_books = Question(question_text="You mentioned books! Do you read regularly? Any favorite genres?", tag="subcategory", is_core_question=False, parent_question_id=q_topics.id, trigger_keyword="book")
            follow_up_movies = Question(question_text="You mentioned movies! What kind of movies or shows do you vibe with?", tag="subcategory", is_core_question=False, parent_question_id=q_topics.id, trigger_keyword="movie")
            follow_up_sports = Question(question_text="You mentioned sports! What sports or activities do you play or watch?", tag="subcategory", is_core_question=False, parent_question_id=q_topics.id, trigger_keyword="sport")

            db.add_all([follow_up_books, follow_up_movies, follow_up_sports])
            db.commit()
            print("Database seeded with full question set.")
        else:
            print("Questions already exist in the database.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()