import json
import uuid
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from app.database import SessionLocal
from app.models import User, Profile
from app.crud import generate_profile_embedding # <-- NEW: Import the embedding function
from faker import Faker
from werkzeug.security import generate_password_hash

INPUT_FILE = "synthetic_profiles.json"

def insert_synthetic_profiles():
    """
    Reads profiles, creates full synthetic users, generates an embedding for
    each profile, and inserts them into the database.
    """
    try:
        with open(INPUT_FILE, "r") as f:
            profiles_to_insert = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: The file '{INPUT_FILE}' was not found.")
        print("Please run 'python -m scripts.generate_profiles' first.")
        return

    db = SessionLocal()
    fake = Faker()
    
    print(f"Found {len(profiles_to_insert)} profiles. Starting insertion and embedding generation...")

    try:
        for i, profile_data in enumerate(profiles_to_insert):
            # 1. Generate realistic User data
            user_name = fake.name()
            mobile_number = f"+999999{i:04d}"
            hashed_password = generate_password_hash("DefaultPassword123!")
            new_user_id = str(uuid.uuid4())[:32]

            # 2. Create the User object
            new_user = User(
                user_id=new_user_id,
                name=user_name,
                mobile_number=mobile_number,
                password=hashed_password
            )
            
            # --- NEW STEP: Generate the embedding ---
            print(f"  ({i + 1}/{len(profiles_to_insert)}) Generating embedding for {user_name}...")
            embedding_vector = generate_profile_embedding(profile_data)
            
            # 3. Create the Profile object, now including the embedding
            new_profile = Profile(
                profile_data=profile_data,
                embedding=embedding_vector # <-- Add the generated vector
            )
            
            # 4. Associate the profile with the user
            new_user.profile = new_profile
            
            db.add(new_user)
        
        # 5. Commit all changes
        print("\nCommitting all users and profiles to the database...")
        db.commit()
        print(f"\n✅ Success! All {len(profiles_to_insert)} synthetic users and profiles have been inserted.")

    except Exception as e:
        print(f"\n❌ ERROR during database insertion: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    insert_synthetic_profiles()