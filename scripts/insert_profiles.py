import json
import os
import sys
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()
from app.database import SessionLocal
from app.models import SharedUser, AppUser, Profile
from app.crud import generate_profile_embedding, load_embedding_model
INPUT_FILE = "synthetic_profiles.json"
def insert_synthetic_profiles():
    """
    Finds existing users in the 'users' table who do not have a profile yet,
    and creates an AppUser and a Profile (with embedding) for them using
    pre-generated synthetic data.
    """
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: The file '{INPUT_FILE}' was not found.")
        print("Please run 'python -m scripts.generate_profiles' first.")
        return
    try:
        with open(INPUT_FILE, "r") as f:
            profiles_to_insert = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return
    print("Loading SBERT model for script...")
    load_embedding_model()
    print("Model loaded.")
    db = SessionLocal()
    print("--- Starting Synthetic Profile Insertion ---")
    print("Finding existing shared users without a profile in our system...")
    all_shared_users = db.query(SharedUser).all()
    existing_profile_user_ids = {p.user_id for p in db.query(Profile).all()}
    users_to_profile = [u for u in all_shared_users if u.user_id not in existing_profile_user_ids]
    if not users_to_profile:
        print("All existing users already have a profile. Nothing to do.")
        db.close()
        return
    print(f"Found {len(users_to_profile)} users to profile. Using {len(profiles_to_insert)} available synthetic profiles.")
    num_to_create = min(len(users_to_profile), len(profiles_to_insert))
    if num_to_create == 0:
        print("No new profiles to create.")
        db.close()
        return
    print(f"Will now create profiles for the first {num_to_create} users...")
    success_count = 0
    failure_count = 0
    try:
        for i in range(num_to_create):
            user = users_to_profile[i]
            profile_data = profiles_to_insert[i]
            print(f"  ({i + 1}/{num_to_create}) Processing for user: {user.name} ({user.user_id})")
            try:
                app_user = db.query(AppUser).filter(AppUser.user_id == user.user_id).first()
                if not app_user:
                    app_user = AppUser(user_id=user.user_id)
                    db.add(app_user)
                embedding_vector = generate_profile_embedding(profile_data)
                new_profile = Profile(
                    user_id=user.user_id,
                    profile_data=profile_data,
                    embedding=embedding_vector
                )
                db.add(new_profile)
                db.commit()
                success_count += 1
            except Exception as e:
                db.rollback()
                failure_count += 1
                print(f"    [ERROR] Failed to insert profile for user {user.user_id}: {e}")
                continue
    finally:
        db.close()
        print(f"\n--- DONE ---")
        print(f"Successfully inserted: {success_count}")
        print(f"Failed: {failure_count}")
if __name__ == "__main__":
    insert_synthetic_profiles()
