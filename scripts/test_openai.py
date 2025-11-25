import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

print("Attempting to connect to OpenAI...")

try:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    models = client.models.list()
    print("Successfully connected to OpenAI!")
    print("First 3 available models:")
    for model in list(models)[:3]:
        print(f"- {model.id}")
except Exception as e:
    print(f"\n--- CONNECTION FAILED ---")
    print(f"An error occurred: {e}")
    print("\n--- DEBUGGING TIPS ---")
    print("1. Is your OPENAI_API_KEY correct in the .env file?")
    print("2. Do you have an active internet connection?")
    print("3. Do you have billing set up on your OpenAI account? (Free trial credits often don't work for this API)")