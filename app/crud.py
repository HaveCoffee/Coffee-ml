from typing import List
from sqlalchemy.orm import Session
from . import models
from sentence_transformers import SentenceTransformer
from . import matching

print("Loading SBERT embedding model...")
EMBEDDING_MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME) 
print("SBERT model loaded successfully.")

def get_interest_taxonomy(db: Session):
    """Fetches the official list of canonical interests from the database."""
    interests = db.query(models.InterestTaxonomy).order_by(models.InterestTaxonomy.id).all()
    return [interest.name for interest in interests]

def generate_profile_embedding(profile_data: dict) -> list[float]:
    """
    Generates a representative embedding for a user profile.
    MODIFIED FOR DEBUGGING: This will now raise exceptions instead of returning None.
    """
    print("\n--- [DEBUG] Inside generate_profile_embedding ---")
    try:
        vibe = profile_data.get('vibe_summary', '')
        interests = ", ".join(profile_data.get('interests', []))
        goal = profile_data.get('social_intent', '')
        personality = profile_data.get('personality_type', '')
        combined_text = f"This person is {personality}. Their goal is {goal}. They are interested in {interests}. In their own words: {vibe}"
        print(f"[DEBUG] Combined text: '{combined_text}'")
        embedding = embedding_model.encode(combined_text)
        print("[DEBUG] Embedding generated successfully.")
        return embedding.tolist()
    except Exception as e:
        print(f" [DEBUG] FATAL ERROR during embedding generation. Re-raising exception.")
        raise e

def get_user(db: Session, user_id: str):
    """Finds a user by their primary key ID."""
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_user_by_thread_id(db: Session, thread_id: str):
    """Finds a user by their associated onboarding thread ID."""
    return db.query(models.User).filter(models.User.onboarding_thread_id == thread_id).first()

def link_thread_to_user(db: Session, user_id: str, thread_id: str):
    """Saves the thread_id to the user's record in the database."""
    user = get_user(db, user_id)
    if user:
        user.onboarding_thread_id = thread_id
        db.commit()
        return user
    return None

def get_user_by_mobile(db: Session, mobile_number: str):
    """Finds a user by their mobile number (for authentication)."""
    return db.query(models.User).filter(models.User.mobile_number == mobile_number).first()

def get_user_profile(db: Session, user_id: str):
    """
    Retrieves the profile for a given user_id.
    """
    return db.query(models.Profile).filter(models.Profile.user_id == user_id).first()

def save_user_profile(db: Session, user_id: str, profile_data: dict):
    """Creates or updates a user's profile with the final JSON data."""
    db_profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()

    if db_profile:
        db_profile.profile_data = profile_data
    else:
        db_profile = models.Profile(user_id=user_id, profile_data=profile_data)
        db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    print("Generating profile embedding...")
    profile_embedding = generate_profile_embedding(profile_data)
    if profile_embedding:
        db_profile.embedding = profile_embedding
        db.commit()
        print("  -> Successfully generated and saved profile embedding.")
    try:
        refresh_user_matches(db, user_id)
    except Exception as e:
        print(f"Error refreshing matches: {e}")
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

def get_match_candidates(db: Session, current_user_id: str):
    """
    Fetches all other users who have a completed profile to be considered as
    potential matches.
    """
    # Find all profiles that are not the current user's and have an embedding
    candidates = db.query(models.Profile).filter(
        models.Profile.user_id != current_user_id,
        models.Profile.embedding.is_not(None)
    ).all()
    return candidates

def refresh_user_matches(db: Session, user_id:str):
    user_profile= get_user_profile(db, user_id)
    if not user_profile or not user_profile.embedding is None:
        print(f"Cannot refresh matches for user {user_id}: profile or embedding missing.")
        return {"status": "failed", "reason": "Profile or embedding missing."}

    candidates= get_match_candidates(db, current_user_id=user_id)
    scored_candidates = []
    for candidate in candidates:
        score=matching.calculate_final_match_score(user_profile, candidate)
        scored_candidates.append((candidate.user_id, score))
    scored_candidates.sort(key=lambda x:x[1], reverse=True)
    top_10= scored_candidates[:10]

    existing_records= db.query(models.Match).filter(models.Match.user_id==user_id).all()
    existing_map={m.matched_id:m for m in existing_records}
    top_10_ids=[x[0] for x in top_10]
    for match_id, score in top_10:
        if match_id in existing_map:
            record= existing_map[match_id]
            record.score= score
        else:
            new_match = models.Match(
                user_id=user_id,
                match_id=match_id,
                score=score,
                status="suggested"
            )
            db.add(new_match)
    for match_id, record in existing_map.items():
        if match_id not in top_10_ids:
            if record.status == "suggested":
                db.delete(record)
    db.commit()
    