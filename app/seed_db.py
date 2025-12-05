from .database import SessionLocal, engine, Base
from .models import Question, InterestTaxonomy
from sqlalchemy import text

def seed_database():
    
    db = SessionLocal()
    try:
        if db.query(InterestTaxonomy).count() == 0:
            print("Seeding new interest taxonomy...")
            
            canonical_interests = [
                InterestTaxonomy(id=1, name="Technology"),
                InterestTaxonomy(id=2, name="Artificial Intelligence"),
                InterestTaxonomy(id=3, name="Sports"),
                InterestTaxonomy(id=4, name="Formula 1"),
                InterestTaxonomy(id=5, name="Reading"),
                InterestTaxonomy(id=6, name="Books"),
                InterestTaxonomy(id=7, name="Movies & TV"),
                InterestTaxonomy(id=8, name="Hiking"),
                InterestTaxonomy(id=9, name="Travel"),
                InterestTaxonomy(id=10, name="Food & Drink"),
                InterestTaxonomy(id=11, name="Music"),
                InterestTaxonomy(id=12, name="Gaming"),
                InterestTaxonomy(id=13, name="Photography"),
                InterestTaxonomy(id=14, name="Arts & Culture"),
                # ... add any other categories you want ...
            ]
            db.add_all(canonical_interests)
            db.commit()
            print("Interest taxonomy seeded.")
        if db.query(Question).count() > 0:
            print("Questions already exist.")
            return

        print("Seeding new question bank...")
        # L0 - Core Questions (IDs 1-10)
        core_questions = [
            Question(id=1, question_text="Beyond your work, what's one thing you're genuinely passionate about?", tag="bio_long", is_core_question=True),
            Question(id=2, question_text="If you had a free weekend, what activity would you be most excited to do? (e.g., read a book, watch a movie, play a sport)", tag="interest_ids", is_core_question=True),
            Question(id=3, question_text="What's the most interesting challenge you're working on right now?", tag="user_goals", is_core_question=True),
            Question(id=4, question_text="How do you prefer to meet new people: in-person or virtual?", tag="meet_type", is_core_question=True),
            Question(id=5, question_text="What does your ideal weekend availability look like for catching up?", tag="availability_slots", is_core_question=True),
            Question(id=6, question_text="Are you more of a planner or a spontaneous person for social events?", tag="personality_type", is_core_question=True),
            Question(id=7, question_text="What kind of connection are you hoping to find here? (e.g., friendship, mentorship)", tag="goal_id", is_core_question=True),
            Question(id=8, question_text="What topic are you curious about and would love to learn from someone?", tag="user_goals.learn", is_core_question=True),
            Question(id=9, question_text="Do you prefer a quiet coffee chat or a more active setting like a walk?", tag="venue_types", is_core_question=True),
            Question(id=10, question_text="How do you feel about reconnecting with friends vs. meeting new people?", tag="audience_filter", is_core_question=True)
        ]

        # L1 - Follow-up Questions (IDs 11+)
        l1_follow_ups = [
            Question(id=11, question_text="You mentioned books. What genre do you usually find yourself reading?", tag="subcategory.book", is_core_question=False, parent_question_id=2, trigger_keyword="book"),
            Question(id=12, question_text="You mentioned movies. What kind of movies or shows do you enjoy?", tag="subcategory.movie", is_core_question=False, parent_question_id=2, trigger_keyword="movie"),
            Question(id=13, question_text="You mentioned sports. Which sport do you enjoy the most?", tag="subcategory.sport", is_core_question=False, parent_question_id=2, trigger_keyword="sport"),
            Question(id=14, question_text="You mentioned work/a project. Do you prefer collaborating or working independently?", tag="profile_attributes.work", is_core_question=False, parent_question_id=3, trigger_keyword="work,project,job"),
            Question(id=15, question_text="Great! What city or neighborhood would you prefer to meet in?", tag="preferred_locations", is_core_question=False, parent_question_id=4, trigger_keyword="in-person,either"),
        ]

        # L2 - Deeper Follow-up Questions (IDs 15+)
        l2_deeper_follow_ups = [
            Question(id=15, question_text="Fantasy is a great genre! Any favorite authors or series?", tag="profile_attributes.book.fantasy", is_core_question=False, parent_question_id=11, trigger_keyword="fantasy"),
            Question(id=16, question_text="Do you prefer playing or watching?", tag="profile_attributes.sport.preference", is_core_question=False, parent_question_id=13, trigger_keyword="cricket,football,basketball,soccer,tennis,badminton"),
        ]

        db.add_all(core_questions)
        db.add_all(l1_follow_ups)
        db.add_all(l2_deeper_follow_ups)
        
        db.commit()

        print("Database successfully seeded with a diverse, multi-layered question bank.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()