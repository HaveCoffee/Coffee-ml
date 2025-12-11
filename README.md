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
*   **Vector Search:** Uses Cosine Similarity via `pgvector` to rank user compatibility based on weighted pillars (Interests, Availability, Location, Personality).
*   **Schema Management:** Automated, non-destructive database migrations using Alembic.
*   **Production Hardened:** Configured with Systemd for auto-restart, strict environment variable management, and worker optimization.

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

**Authentication**
*   Currently handled via manual JWT generation or Dev Mode bypass.
*   Header: `Authorization: Bearer <TOKEN>`

**Profiles**
*   `GET /api/profile` - Get authenticated user's profile.
*   `GET /api/users/{user_id}` - Get public profile of another user.

**Matchmaking**
*   `GET /api/matches` - Returns top 10 ranked matches based on embedding similarity.

**Onboarding**
*   `POST /chat` - Interactive chat session with AI Assistant.
    *   Payload: `{"message": "Hello", "thread_id": "optional-thread-id"}`

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