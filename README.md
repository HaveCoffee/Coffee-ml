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
| `JWT_SECRET_KEY` | 32-byte hex string (Must match Auth Service key) |
| `JWT_ALGORITHM` | `HS256` |
| `DEV_MODE` | `true` or `false` (Bypasses Auth if true) |
| `DEV_USER_ID` | UUID of the admin user for Dev Mode |

## Integration Standards

**User IDs:**
This service strictly enforces **32-character Hex UUIDs** (e.g., `5719256cbd62...`) to match the Auth Service format.
*   `5719256c-bd62-...` (Hyphenated UUIDs will cause 404s/Foreign Key errors).
*   `5719256cbd62...` (Stripped Hex UUIDs are required).

**Authentication:**
All protected endpoints require the HTTP Header:
`Authorization: Bearer <your_jwt_token>`

## API Endpoints

### 1. User Profiles

#### Get Own Profile
Retrieves the profile data for the authenticated user.

*   **Method:** `GET`
*   **URL:** `/api/profile`
*   **Success Response (200 OK):**
    ```json
    {
      "user_id": "hex-uuid-string",
      "profile_data": {
        "vibe_summary": "string",
        "interests": ["Technology", "Hiking"],
        "social_intent": "Friendship",
        "personality_type": "Introvert",
        "availability": {"days": ["Mon"], "time": ["Evening"]}
      }
    }
    ```
*   **Errors:** `404 Not Found` (Profile incomplete), `401 Unauthorized`.

#### Get Public Profile
Retrieves public details of a specific target user.

*   **Method:** `GET`
*   **URL:** `/api/users/{user_id}`
*   **Path Params:** `user_id` (Hex UUID)
*   **Success Response (200 OK):**
    ```json
    {
      "user_id": "target-hex-uuid",
      "profile_data": { ...subset of profile data... }
    }
    ```

---

### 2. Matchmaking (Screens)

#### Screen 1: Suggested Matches
Returns AI-recommended users.
*   **Logic:** Returns top 10 users sorted by compatibility score.
*   **Filters:** Excludes users already in `active`, `passed`, or `blocked` states.

*   **Method:** `GET`
*   **URL:** `/api/matches/suggested`
*   **Success Response (200 OK):**
    ```json
    {
      "matches": [
        {
          "user_id": "hex-uuid",
          "score": 0.95,  // Float 0.0 - 1.0
          "profile_data": { "vibe_summary": "...", "interests": [...] }
        },
        ...
      ]
    }
    ```

#### Screen 2: Active Chats
Returns users with whom a connection has been established.
*   **Logic:** Returns users with `status='active'`. These are protected from AI re-ranking/deletion.
*   **Sort:** Most recently updated first.

*   **Method:** `GET`
*   **URL:** `/api/matches/active`
*   **Success Response (200 OK):**
    ```json
    {
      "matches": [
        {
          "user_id": "hex-uuid",
          "score": 0.88,
          "last_active": "2023-12-25T10:30:00",
          "profile_data": { ... }
        }
      ]
    }
    ```

---

### 3. Match Actions

#### Start Chat
Moves a user from the 'suggested' list to the 'active' list.

*   **Method:** `POST`
*   **URL:** `/api/matches/start-chat`
*   **Request Body:**
    ```json
    { "match_id": "target-hex-uuid" }
    ```
*   **Success Response (200 OK):** `{"status": "success", "message": "Moved to active chats"}`

#### Pass User
Hides a user from suggestions. They will not appear again.

*   **Method:** `POST`
*   **URL:** `/api/matches/pass`
*   **Request Body:**
    ```json
    { "match_id": "target-hex-uuid" }
    ```
*   **Success Response (200 OK):** `{"status": "success", "message": "User passed"}`

#### Block User
Blocks a user completely. Prevents them from appearing in any list.

*   **Method:** `POST`
*   **URL:** `/api/matches/block`
*   **Request Body:**
    ```json
    { "match_id": "target-hex-uuid" }
    ```
*   **Success Response (200 OK):** `{"status": "success", "message": "User blocked"}`

---

### 4. Onboarding Chat (AI)

Initiates or continues a conversation with the OpenAI Assistant to build the user profile. The backend automatically extracts entities (interests, bio) and updates the database.

*   **Method:** `POST`
*   **URL:** `/chat`
*   **Request Body:**
    ```json
    {
      "message": "I enjoy hiking and reading sci-fi.",
      "thread_id": "thread_abc123" // Optional. Omit for first message.
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
      "response": "That's cool! Who is your favorite sci-fi author?",
      "thread_id": "thread_abc123" // Store this to maintain context
    }
    ```

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