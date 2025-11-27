import json
from dotenv import load_dotenv
load_dotenv()
from app.database import SessionLocal
from app.models import User, Profile
from faker import Faker
from werkzeug.security import generate_password_hash
import uuid

INPUT_FILE = "synthetic_profiles.json"

def insert_synthetic_profiles():
    """
    Reads generated profiles, creates full synthetic users with hashed passwords,
    and inserts them into the database.
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
    print(f"Found {len(profiles_to_insert)} profiles to insert. Starting insertion...")
    try:
        for i, profile_data in enumerate(profiles_to_insert):
            user_name = fake.name()
            mobile_number = f"+999999{i:04d}" 
            hashed_password = generate_password_hash("DefaultPassword123!")
            new_user_id = str(uuid.uuid4())[:32]
            new_user = User(
                user_id=new_user_id,
                name=user_name,
                mobile_number=mobile_number,
                password=hashed_password
            )            
            new_profile = Profile(profile_data=profile_data)
            new_user.profile = new_profile
            
            db.add(new_user)
            print(f"  Prepared user '{user_name}' ({mobile_number})")
        db.commit()
        print(f"\n Success! All {len(profiles_to_insert)} synthetic users and profiles have been inserted.")
    except Exception as e:
        print(f"\n ERROR during database insertion: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    insert_synthetic_profiles()