# Coffee App 

This repository contains the Agentic service for the Coffee social app's user onboarding experience. It features an intelligent, conversational agent powered by the OpenAI Assistants API that conducts a dynamic, multi-layered interview to build a rich user profile.

The system is built with FastAPI and connects to a PostgreSQL database.



## Tech Stack

-   **Backend:** FastAPI
-   **AI:** OpenAI Assistants API
-   **Database:** PostgreSQL
-   **ORM:** SQLAlchemy
-   **Infrastructure:** Docker (for local development)

## Project Structure

```
/
├── app/                  # Main application package
│   ├── main.py           # FastAPI app, chat endpoint, and Assistant lifecycle management
│   ├── crud.py           # Database interaction functions (the "tools" for the agent)
│   ├── models.py         # SQLAlchemy ORM models (DB schema)
│   ├── database.py       # Database connection setup
│   └── seed_db.py        # Script to create and seed the database with the question bank
│
├── .env                  # Stores secrets and environment variables (not in git)
├── docker-compose.yml    # Defines the local PostgreSQL service
└── requirements.txt      # Python dependencies
```

## Setup and Installation

### Prerequisites

-   Python 3.10+
-   Docker and Docker Compose
-   An OpenAI API key with billing enabled.

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd <your-repo-name>
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root. Copy the contents of `.env.example` (if you have one) or use the template below.

```.env
# --- OpenAI Configuration ---
OPENAI_API_KEY="sk-..."

# --- Local Development Database (uses docker-compose.yml) ---
# DATABASE_URL="postgresql://coffee_user:coffee_pass@localhost/coffee_db"

# --- Production/Staging Database (e.g., AWS RDS) ---
# DATABASE_URL="postgresql://USER:PASSWORD@HOST:PORT/DB_NAME"
```

### 3. Build and Run the Local Database

Start the PostgreSQL container in the background.

```bash
docker compose up -d
```

### 4. Install Dependencies

Create and activate a virtual environment, then install the required packages.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 5. Initialize the Database

Run the seeder script. This will create all necessary tables and populate the `questions` table with the full, multi-layered interview script.

```bash
python -m app.seed_db
```

## Running the Application

With the database running and initialized, start the FastAPI server.

```bash
uvicorn app.main:app --reload
```

The application will be running on `http://127.0.0.1:8000`.

## API Endpoint

The entire conversational flow is handled by a single endpoint.

-   **Endpoint:** `/chat`
-   **Method:** `POST`
-   **Request Body (First Turn):**
    ```json
    {
        "message": "Hi"
    }
    ```
-   **Request Body (Subsequent Turns):**
    ```json
    {
        "thread_id": "thread_...",
        "message": "My response"
    }
    ```
-   **Success Response:**
    ```json
    {
        "response": "The assistant's next question or final message.",
        "thread_id": "thread_..."
    }
    ```
