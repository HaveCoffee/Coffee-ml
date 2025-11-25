import os
import json
import random
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

NUM_PROFILES_TO_GENERATE = 50
OUTPUT_FILE = "synthetic_profiles.json"
MODEL_TO_USE = "gpt-3.5-turbo-0125"

INTEREST_CATEGORIES = ["Technology", "Arts & Culture", "Sports & Fitness", "Travel", "Food & Drink", "Reading", "Gaming", "Music", "Outdoor Activities"]
PERSONALITY_TRAITS = ["Introverted", "Extroverted", "Analytical", "Creative", "Spontaneous", "Organized", "Adventurous", "Homebody", "Humorous", "Serious"]
SOCIAL_GOALS = ["Mentorship", "Friendship", "Professional Networking", "Finding a collaborator", "Casual chats"]


SYSTEM_PROMPT = """
You are a creative persona generator for a social app called "Coffee". Your task is to create a realistic and consistent user profile based on a few seed characteristics.

The user profile MUST be ONLY a single, valid JSON object that strictly adheres to the following schema. Do not include any extra text, explanations, or markdown formatting.

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

**RULES:**
- The `vibe_summary` must be a short, first-person sentence that reflects the user's personality and interests.
- The `conversation_topics` should be directly related to the `interests`.
- `meeting_style` should be one of "in-person", "virtual", or "either".
- Keep `preferred_locations` as an empty array `[]`.
"""

def generate_synthetic_profiles():
    """
    Generates a specified number of synthetic user profiles using an LLM
    and saves them to a file.
    """
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    generated_profiles = []
    print(f"Starting generation of {NUM_PROFILES_TO_GENERATE} profiles...")
    for i in range(NUM_PROFILES_TO_GENERATE):
        seed_trait = random.choice(PERSONALITY_TRAITS)
        seed_goal = random.choice(SOCIAL_GOALS)
        seed_interests = random.sample(INTEREST_CATEGORIES, 3)
        user_message = (
            f"Generate a user profile for a person who is {seed_trait}, "
            f"is primarily looking for {seed_goal}, "
            f"and is interested in {seed_interests[0]}, {seed_interests[1]}, and {seed_interests[2]}."
        )
        try:
            response = client.chat.completions.create(
                model=MODEL_TO_USE,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"},
                temperature=0.8
            )
            profile_json_str = response.choices[0].message.content
            profile_data = json.loads(profile_json_str)
            generated_profiles.append(profile_data)
            print(f"  Successfully generated profile {i + 1}/{NUM_PROFILES_TO_GENERATE}")

        except Exception as e:
            print(f"  ERROR generating profile {i + 1}: {e}")
            continue
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(generated_profiles, f, indent=2)

    print(f"\n Generation complete. {len(generated_profiles)} profiles saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_synthetic_profiles()