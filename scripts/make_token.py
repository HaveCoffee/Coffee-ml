import os
import sys
from datetime import datetime, timedelta
from jose import jwt
from dotenv import load_dotenv

# Load env vars
load_dotenv()

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")

# Use the ID of the synthetic user we used earlier (or any valid UUID in your DB)
# This ID must exist in the 'users' table!
TEST_USER_ID = "6b2198a66b5a4c02973835ebab98b68c"

if not SECRET_KEY:
    print("Error: JWT_SECRET_KEY not found in .env")
    sys.exit(1)

to_encode = {"user_id": TEST_USER_ID, "exp": datetime.utcnow() + timedelta(hours=1)}
encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

print("\n--- YOUR ACCESS TOKEN ---")
print(encoded_jwt)
print("-------------------------\n")
