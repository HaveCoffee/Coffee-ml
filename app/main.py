# app/main.py
import os
from fastapi import FastAPI, Depends, HTTPException, Security, Request
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from sqlalchemy.orm import Session
from openai import OpenAI
from dotenv import load_dotenv

from . import crud, models
from .database import get_db

load_dotenv()

app = FastAPI()
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

API_KEY = os.eKEYnviron["TOOL_API_KEY"]
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

@app.post("/api/chatkit/session")
async def create_chatkit_session(request: Request):
    session = openai_client.chatkit.sessions.create()
    return {"client_secret": session.client_secret}



class UserCreateRequest(BaseModel):
    name: str

class AnswerSaveRequest(BaseModel):
    user_id: int
    question_id: int
    answer_text: str

@app.post("/tools/create_user", dependencies=[Depends(get_api_key)])
def tool_create_user(request: UserCreateRequest, db: Session = Depends(get_db)):
    user = crud.create_user(db=db, name=request.name)
    return {"user_id": user.id, "name": user.name}

@app.post("/tools/get_all_questions", dependencies=[Depends(get_api_key)])
def tool_get_questions(db: Session = Depends(get_db)):
    questions = crud.get_all_questions(db=db)
    return [{"id": q.id, "question_text": q.question_text, "tag": q.tag} for q in questions]

@app.post("/tools/save_answer", dependencies=[Depends(get_api_key)])
def tool_save_answer(request: AnswerSaveRequest, db: Session = Depends(get_db)):
    return crud.save_user_answer(
        db=db,
        user_id=request.user_id,
        question_id=request.question_id,
        answer_text=request.answer_text
    )