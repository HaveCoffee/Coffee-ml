import json
import uuid
import sys
from dotenv import load_dotenv
load_dotenv()
import os
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import User, Profile
from app.crud import generate_profile_embedding
from faker import Faker
from werkzeug.security import generate_password_hash

INPUT_FILE = "synthetic_profiles.json"

def insert_synthetic_profiles():
    """
    Reads profiles, creates full synthetic users, generates an embedding for
    each profile, and inserts them into the database safely.
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

    db = SessionLocal()
    fake = Faker()
    
    print(f"Found {len(profiles_to_insert)} profiles. Starting insertion...")
    
    success_count = 0
    failure_count = 0

    for i, profile_data in enumerate(profiles_to_insert):
        try:
            user_name = fake.name()
            mobile_number = f"+1555000{i:04d}" 
            hashed_password = generate_password_hash("DefaultPassword123!")
            new_user_id = str(uuid.uuid4())[:32]

            new_user = User(
                user_id=new_user_id,
                name=user_name,
                mobile_number=mobile_number,
                password=hashed_password
            )

            print(f"  ({i + 1}/{len(profiles_to_insert)}) Processing {user_name}...")
            embedding_vector = generate_profile_embedding(profile_data)
            
            new_profile = Profile(
                user_id=new_user_id, 
                profile_data=profile_data,
                embedding=embedding_vector
            )
            
            new_user.profile = new_profile

            db.add(new_user)
            db.add(new_profile) 
            
            db.commit()
            success_count += 1
            
        except Exception as e:
            db.rollback()
            failure_count += 1
            print(f"    [ERROR] Failed to insert user {i+1}: {e}")
            continue

    db.close()
    print(f"\n--- DONE ---")
    print(f"Successfully inserted: {success_count}")
    print(f"Failed: {failure_count}")

if __name__ == "__main__":
    insert_synthetic_profiles()