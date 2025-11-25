import json
from app.database import SessionLocal
from app.models import User, Profile

INPUT_FILE = "synthetic_profiles.json"
def insert_synthetic_profiles():
    """
    Reads the generated profiles from the JSON file and inserts them
    into the database.
    """
    try:
        with open(INPUT_FILE, "r") as f:
            profiles_to_insert = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: The file '{INPUT_FILE}' was not found.")
        print("Please run 'python generate_profiles.py' first.")
        return
    db = SessionLocal()
    print(f"Found {len(profiles_to_insert)} profiles to insert. Starting insertion...")
    try:
        for i, profile_data in enumerate(profiles_to_insert):
            new_user = User(name=f"Synthetic User {i + 1}")
            new_profile = Profile(profile_data=profile_data)
            new_user.profile = new_profile
            db.add(new_user)
            print(f"  Prepared user {i + 1}/{len(profiles_to_insert)}")
        db.commit()
        print("\n Success! All synthetic users and profiles have been inserted into the database.")
    except Exception as e:
        print(f"\n ERROR during database insertion: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    insert_synthetic_profiles()