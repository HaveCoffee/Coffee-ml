import json
import os
import uuid
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path to allow imports from 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models import User, Profile
from app.crud import generate_profile_embedding
from werkzeug.security import generate_password_hash
from openai import OpenAI

# --- Configuration for the new user ---
# You can change these values to create different users
USER_NAME = "Vishal"
MOBILE_NUMBER = "+918517083728"
DEFAULT_PASSWORD = "DefaultPassword123!"

# --- AI Configuration for Profile Generation ---
MODEL_TO_USE = "gpt-3.5-turbo-0125"
SYSTEM_PROMPT = """
You are a creative persona generator for a social app called "Coffee". 
Your task is to create a realistic and consistent user profile based on a user's name.

The user profile MUST be ONLY a single, valid JSON object that strictly adheres to the following schema. 
Do not include any extra text, explanations, or markdown formatting.

**REQUIRED JSON SCHEMA:**
{
  "interests": ["string", "string", "string"],
  "availability": {"days": ["string"], "time_windows": ["string"]},
  "vibe_summary": "string",
  "meeting_style": "string",
  "social_intent": "string",
  "personality_type": "string",
  "conversation_topics": ["string", "string"],
  "preferred_locations": []
}
"""

def create_specific_user(name: str, mobile: str, password: str):
    """
    Generates a single user with specific details and an AI-generated profile,
    then inserts them into the database.
    """
    db = SessionLocal()
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    print(f"--- Starting creation for user: {name} ({mobile}) ---")

    # Check if user already exists
    existing_user = db.query(User).filter(User.mobile_number == mobile).first()
    if existing_user:
        print(f" ERROR: A user with mobile number {mobile} already exists.")
        db.close()
        return

    try:
        # Step 1: Generate the Profile Data using OpenAI
        user_prompt = f"Generate a random but realistic and interesting user profile for a person named {name}. Make them seem like a real person with coherent interests and personality."
        print("1. Generating AI profile data...")
        response = client.chat.completions.create(
            model=MODEL_TO_USE,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.9
        )
        profile_data = json.loads(response.choices[0].message.content)
        print("   -> Profile data generated successfully.")
        print(json.dumps(profile_data, indent=2))

        # Step 2: Generate the Embedding
        print("\n2. Generating profile embedding...")
        embedding_vector = generate_profile_embedding(profile_data)
        if not embedding_vector:
            raise Exception("Failed to generate profile embedding.")
        print("   -> Embedding generated successfully.")

        # Step 3: Prepare Database Records
        print("\n3. Preparing database records...")
        hashed_password = generate_password_hash(password)
        new_user_id = str(uuid.uuid4())[:32]

        new_user = User(
            user_id=new_user_id,
            name=name,
            mobile_number=mobile,
            password=hashed_password
        )
        
        new_profile = Profile(
            profile_data=profile_data,
            embedding=embedding_vector
        )
        
        new_user.profile = new_profile
        db.add(new_user)
        print("   -> Database records prepared.")

        # Step 4: Commit to Database
        print("\n4. Committing to database...")
        db.commit()
        print(f"\n SUCCESS: User '{name}' and their profile have been created.")

    except Exception as e:
        print(f"\n ERROR: An error occurred during the process: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # This block allows the script to be run from the command line.
    # It will use the default values defined at the top of the file.
    create_specific_user(name=USER_NAME, mobile=MOBILE_NUMBER, password=DEFAULT_PASSWORD)
