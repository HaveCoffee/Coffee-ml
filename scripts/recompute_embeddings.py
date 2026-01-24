import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()
from app.database import SessionLocal
from app.models import SharedUser, Profile
from app.crud import generate_profile_embedding
from sqlalchemy.orm import Session

def recompute_embeddings_for_null_profiles():
    """
    Finds all profiles with a NULL embedding and generates a new one for them.
    This is safe to run multiple times.
    """
    db: Session = SessionLocal()
    
    print("--- Starting Embedding Re-computation Script ---")

    try:
        # 1. Find all profiles that are missing an embedding
        profiles_to_update = db.query(Profile).filter(Profile.embedding.is_(None)).all()

        if not profiles_to_update:
            print(" No profiles found with missing embeddings. Database is up-to-date.")
            return

        print(f"Found {len(profiles_to_update)} profiles to process.")

        updated_count = 0
        for i, profile in enumerate(profiles_to_update):
            print(f"  ({i + 1}/{len(profiles_to_update)}) Processing profile for user_id: {profile.user_id}...")

            # 2. Check if profile_data exists
            if not profile.profile_data:
                print(f"    -> SKIPPING: No profile_data found for this user.")
                continue

            # 3. Generate the new embedding
            new_embedding = generate_profile_embedding(profile.profile_data)

            # 4. Update the profile record if the embedding was generated successfully
            if new_embedding:
                profile.embedding = new_embedding
                updated_count += 1
                print("    -> SUCCESS: Embedding generated.")
            else:
                print("    -> FAILED: Embedding generation returned None.")
        
        # 5. Commit all the changes to the database
        if updated_count > 0:
            print(f"\nCommitting {updated_count} updated profiles to the database...")
            db.commit()
            print(" Commit successful.")
        else:
            print("\nNo profiles were updated.")

    except Exception as e:
        print(f"\n An error occurred: {e}")
        db.rollback()
    finally:
        db.close()
        print("\n--- Script finished ---")

if __name__ == "__main__":
    recompute_embeddings_for_null_profiles()