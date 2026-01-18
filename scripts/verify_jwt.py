from jose import jwt, JWTError
from pprint import pprint

# --- PASTE THE JWT FROM YOUR TEAMMATE HERE ---
YOUR_JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjk2ODRkN2FiZWRhYzY0ZjljZDY0MTdkZGJiMDU2NTYiLCJtb2JpbGVOdW1iZXIiOiIrOTE5NTg5MDc0OTg5IiwiaWF0IjoxNzY0MTkyNDM2LCJleHAiOjE3NjQxOTYwMzZ9.RrorIMOPwlZnVmDJ_nmtha7jqpG-QN8FW4rXX-7HP2w"


# --- Option A: Decode the payload WITHOUT verifying the signature ---
# This is useful just to see what's inside the token.
print("--- Decoding Payload (Ignoring Signature) ---")
try:
    # We pass a special option to skip the signature check
    payload_without_verification = jwt.decode(
        YOUR_JWT_TOKEN,
        "any_key", # Key doesn't matter when not verifying
        options={"verify_signature": False}
    )
    print("Successfully decoded payload:")
    print(payload_without_verification)
except Exception as e:
    print(f"Failed to decode token: {e}")


print("\n" + "="*50 + "\n")


# --- Option B: Fully VERIFY the token with the secret key ---
# This is what your FastAPI app does. This will only work if you have the correct secret key.
print("--- Verifying Full Token (with Signature) ---")

# --- PASTE THE SECRET KEY AND ALGORITHM FROM YOUR .env FILE HERE ---
SECRET_KEY = "SUPER_SECRET_KEY_FOR_JWT_SIGNING"
ALGORITHM = "HS256"

if SECRET_KEY == "the_secret_key_from_your_teammate":
    print("WARNING: You must replace SECRET_KEY in this script to verify the signature.\n")
else:
    try:
        # This will fail if the secret key is wrong or the token is expired
        payload_with_verification = jwt.decode(
            YOUR_JWT_TOKEN,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        print("✅ SUCCESS: Token signature and claims are valid!")
        print("Decoded payload:")
        pprint(payload_with_verification)
    except JWTError as e:
        print(f"❌ FAILED: Token is invalid. Error: {e}")