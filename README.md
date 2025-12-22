# Coffee-ml API

A production-ready FastAPI backend designed for social matchmaking using vector embeddings and AI-driven onboarding.

## Tech Stack

*   **Framework:** FastAPI, Uvicorn
*   **Database:** PostgreSQL (AWS RDS) with `pgvector` extension
*   **ORM:** SQLAlchemy + Alembic (Migrations)
*   **ML:** `sentence-transformers` (Local inference for embeddings)
*   **AI:** OpenAI Assistants API (Chatbot)
*   **Auth:** JWT (OAuth2 Password Bearer)
*   **Infrastructure:** AWS EC2 (Ubuntu), Systemd

## Features

*   **Hybrid AI Architecture:** Runs SBERT locally for embeddings/ranking and calls OpenAI for conversational onboarding.
*   **Stateful Matching Engine:** Matches are persisted in the database with specific states (`suggested`, 'active', `passed`, `blocked`). The AI manages suggestions, while users control active chats.
*   **Vector Search:** Uses Cosine Similarity via `pgvector` to rank user compatibility based on weighted pillars (Interests, Availability, and Personality).
*   **Schema Management:** Automated, non-destructive database migrations using Alembic.
*   **Production Hardened:** Systemd, JWT Auth, and Hex-UUID standardization.

## Environment Variables (`.env`)

| Variable | Description |
| :--- | :--- |
| `DATABASE_URL` | `postgresql://user:pass@host:5432/db_name` |
| `OPENAI_API_KEY` | OpenAI API Key for Chatbot |
| `JWT_SECRET_KEY` | 32-byte hex string for signing tokens |
| `JWT_ALGORITHM` | `HS256` |
| `DEV_MODE` | `true` or `false` (Bypasses Auth if true) |
| `DEV_USER_ID` | UUID of the admin user for Dev Mode |

## Local Development (Docker)

```bash
# 1. Start Database
docker compose up -d

# 2. Seed Initial Data (Taxonomy & Questions)
python -m app.seed_db

# 3. Generate & Insert Synthetic Profiles (Optional)
python -m scripts.generate_profiles
python -m scripts.insert_profiles

# 4. Run Server
uvicorn app.main:app --reload
```

## Production Deployment (AWS EC2 + RDS)

**1. Setup & Install**
```bash
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
```

**2. Database Migrations**
```bash
# Apply schema changes to RDS
alembic upgrade head
```

**3. Systemd Service**
File: `/etc/systemd/system/coffee-ml.service`
```ini
[Unit]
Description=Coffee-ml FastAPI Service
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/Coffee-ml
EnvironmentFile=/home/ubuntu/Coffee-ml/.env
Environment="PYTHONUNBUFFERED=1"
ExecStart=/home/ubuntu/Coffee-ml/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
Restart=always

[Install]
WantedBy=multi-user.target
```

**4. Management Commands**
```bash
sudo systemctl restart coffee-ml
sudo journalctl -u coffee-ml -f  # View logs
```

## API Endpoints


All endpoints require the following header for authentication (unless `DEV_MODE=true`):
*   **Header:** `Authorization`
*   **Value:** `Bearer <your_jwt_token>`

### 1. Get Own Profile
Retrieves the profile data for the currently authenticated user.

*   **Endpoint:** `GET /api/profile`
*   **Parameters:** None
*   **Response:**
    ```json
    {
      "user_id": "uuid-string",
      "profile_data": {
        "vibe_summary": "string",
        "interests": ["string"],
        "social_intent": "string",
        "personality_type": "string"
      }
    }
    ```

### 2. Get Public Profile
Retrieves the public-facing details of a specific user.

*   **Endpoint:** `GET /api/users/{user_id}`
*   **Path Parameters:**
    *   `user_id` (string, required): The UUID of the target user.
*   **Response:**
    ```json
    {
      "user_id": "target-uuid",
      "profile_data": { ... }
    }
    ```

### 3. Matchmaking & Interactions

**1. Get Suggested Matches (Screen 1)**
Returns the AI-recommended users that the current user has not interacted with yet.
*   **Endpoint:** `GET /api/matches/suggested`
*   **Response:**
    ```json
    {
      "matches": [
        {
          "user_id": "hex-uuid",
          "score": 0.95,
          "profile_data": { ... }
        }
      ]
    }
    ```

**2. Get Active Chats (Screen 2)**
Returns users with whom a chat/connection has been started. These are protected from AI deletion.
*   **Endpoint:** `GET /api/matches/active`
*   **Response:**
    ```json
    {
      "matches": [
        {
          "user_id": "hex-uuid",
          "score": 0.88,
          "last_active": "timestamp",
          "profile_data": { ... }
        }
      ]
    }
    ```

**3. Match Actions**
Perform actions on a specific match.

*   **Start Chat:** Moves a user from 'suggested' to 'active'.
    *   `POST /api/matches/start-chat`
    *   Body: `{"match_id": "target-uuid"}`

*   **Pass:** Hides a user from suggestions permanently.
    *   `POST /api/matches/pass`
    *   Body: `{"match_id": "target-uuid"}`

*   **Block:** Blocks a user completely (prevents future matching).
    *   `POST /api/matches/block`
    *   Body: `{"match_id": "target-uuid"}`

### 4. Onboarding Chat
Initiates or continues a conversation with the AI assistant to build a user profile.

*   **Endpoint:** `POST /chat`
*   **Headers:** `Content-Type: application/json`
*   **Body Parameters:**
    *   `message` (string, required): The user's input text.
    *   `thread_id` (string, optional): The OpenAI Thread ID returned from the previous response. Omit this for the first message to start a new conversation.
*   **Example Body:**
    ```json
    {
      "message": "I enjoy hiking and sci-fi books.",
      "thread_id": "thread_abc123..." 
    }
    ```
*   **Response:**
    ```json
    {
      "response": "That's great! What is your favorite sci-fi book?",
      "thread_id": "thread_abc123..."
    }
    ```



## Database Management (Alembic)

**Generate Migration (after model changes):**
```bash
alembic revision --autogenerate -m "Description of change"
```

**Apply Migration:**
```bash
alembic upgrade head
```

**Revert Last Migration:**
```bash
alembic downgrade -1
```