import os
import time
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from openai import OpenAI
from dotenv import load_dotenv
from . import crud, security, models, matching
from .database import get_db
from .models import User

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This function runs once at application startup to pre-load heavy models,
    preventing timeouts on the first user request.
    """
    print("Application startup: Pre-loading ML models...")
    crud.load_embedding_model()
    yield
    print("Application shutdown.")

app = FastAPI(lifespan=lifespan)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
ASSISTANT_ID = "asst_SDSZf4hIWjeUso6efLvRFNHm"

IS_DEV_MODE = os.environ.get("DEV_MODE", "false").lower() == "true"
if IS_DEV_MODE:
    print("--- WARNING: RUNNING IN DEV MODE - AUTHENTICATION IS BYPASSED ---")
    auth_dependency = security.get_current_user_override
else:
    auth_dependency = security.get_current_user

class ChatRequest(BaseModel):
    thread_id: str | None = None
    message: str

class PublicProfileResponse(BaseModel):
    user_id: str
    class ProfileDataSubset(BaseModel):
        vibe_summary: str | None = None
        interests: list | None = None 
        social_intent: str | None = None
        personality_type: str | None = None
    profile_data: ProfileDataSubset | None = None
    class Config:
        from_attributes = True

class MatchActionRequest(BaseModel):
    match_id: str

# === 4. Onboarding Chat (AI) ===
@app.post("/chat")
async def handle_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_dependency)
):
    thread_id = request.thread_id
    
    if not thread_id:
        thread = client.beta.threads.create()
        thread_id = thread.id
        crud.link_thread_to_user(db, user_id=current_user.user_id, thread_id=thread_id)
        initial_message = f"Hi {current_user.name}! Let's get your profile set up. {request.message}"
        client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=initial_message
        )
    else:
        client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=request.message
        )

    run = client.beta.threads.runs.create(
        thread_id=thread_id, assistant_id=ASSISTANT_ID
    )

    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        if run.status in ['queued', 'in_progress']:
            time.sleep(1)
            continue

        if run.status == 'requires_action':
            tool_outputs = []
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                arguments = json.loads(tool_call.function.arguments)
                output = {}
                
                if tool_call.function.name == "get_all_questions":
                    output = crud.get_all_questions(db)
                
                elif tool_call.function.name == "get_interest_taxonomy":
                    output = crud.get_interest_taxonomy(db)

                elif tool_call.function.name == "save_final_profile":
                    if 'profile_data' in arguments:
                        user = crud.get_user_by_thread_id(db, thread_id=thread_id)
                        if user:
                            output = crud.save_user_profile(
                                db, user_id=user.user_id, profile_data=arguments['profile_data']
                            )
                        else:
                            output = {"status": "error", "message": "Could not find a user for this thread."}
                    else:
                        output = {"status": "error", "message": "The 'profile_data' argument was missing."}

                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(output)
                })
            
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id, run_id=run.id, tool_outputs=tool_outputs
            )
            continue

        if run.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            assistant_message = messages.data[0].content[0].text.value
            return {"response": assistant_message, "thread_id": thread_id}

        if run.status in ['failed', 'cancelled', 'expired']:
            error_details = run.last_error
            print(f"Run ended with status: {run.status}. Error: {error_details}")
            raise HTTPException(status_code=500, detail=f"Run ended with status: {run.status}")
        
        break
    return {"detail": "An unexpected error occurred in the run loop."} # Safeguard

# === 1. User Profiles ===
@app.get("/api/profile", response_model=PublicProfileResponse)
async def get_own_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_dependency)
):
    profile = crud.get_user_profile(db, user_id=current_user.user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Please complete the onboarding chat first.")
    return profile

@app.get("/api/users/{user_id}", response_model=PublicProfileResponse)
async def get_user_profile_by_id(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_dependency)
):
    profile = crud.get_user_profile(db, user_id=user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

# === 2. Matchmaking (Screens) ===
@app.get("/api/matches/suggested")
async def get_suggested_matches(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_dependency)
):
    matches = db.query(models.Match).filter(
        models.Match.user_id == current_user.user_id,
        models.Match.status == "suggested"
    ).order_by(models.Match.score.desc()).limit(10).all()
    
    result = []
    for m in matches:
        profile = crud.get_user_profile(db, m.match_id)
        if profile:
            result.append({
                "user_id": m.match_id,
                "score": m.score,
                "profile_data": profile.profile_data
            })
    return {"matches": result}

@app.get("/api/matches/active")
async def get_active_matches(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_dependency)
):
    matches = db.query(models.Match).filter(
        models.Match.user_id == current_user.user_id,
        models.Match.status == "active"
    ).order_by(models.Match.updated_at.desc()).all()
    
    result = []
    for m in matches:
        profile = crud.get_user_profile(db, m.match_id)
        if profile:
            result.append({
                "user_id": m.match_id,
                "score": m.score,
                "last_active": m.updated_at,
                "profile_data": profile.profile_data
            })
    return {"matches": result}

# === 3. Match Actions ===
@app.post("/api/matches/start-chat")
async def start_chat(
    request: MatchActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_dependency)
):
    match_record = crud.update_match_status(db, user_id=current_user.user_id, match_id=request.match_id, new_status="active")
    if not match_record:
        raise HTTPException(status_code=404, detail="Match not found or cannot be activated.")
    return {"status": "success", "message": "Moved to active chats"}

@app.post("/api/matches/pass")
async def pass_user(
    request: MatchActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_dependency)
):
    crud.update_match_status(db, user_id=current_user.user_id, match_id=request.match_id, new_status="passed")
    return {"status": "success", "message": "User passed"}

@app.post("/api/matches/block")
async def block_user(
    request: MatchActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_dependency)
):
    crud.update_match_status(db, user_id=current_user.user_id, match_id=request.match_id, new_status="blocked")
    return {"status": "success", "message": "User blocked"}