import os
import time
import json
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from openai import OpenAI
from dotenv import load_dotenv

from . import crud
from .database import get_db

load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

ASSISTANT_ID = "asst_SDSZf4hIWjeUso6efLvRFNHm"
user_id_store = {}

class ChatRequest(BaseModel):
    thread_id: str | None = None
    message: str

@app.post("/chat")
async def handle_chat(request: ChatRequest, db: Session = Depends(get_db)):
    thread_id = request.thread_id
    if not thread_id:
        # CORRECTED: .beta is required
        thread = client.beta.threads.create()
        thread_id = thread.id

    # CORRECTED: .beta is required
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=request.message
    )

    # CORRECTED: .beta is required
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=ASSISTANT_ID
    )

    # Main Run Loop
    while True:
        # CORRECTED: .beta is required
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        if run.status in ['queued', 'in_progress']:
            time.sleep(1)
            continue

        if run.status == 'requires_action':
            tool_outputs = []
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                arguments = json.loads(tool_call.function.arguments)
                output = {}
                
                if tool_call.function.name == "create_user":
                    user_obj = crud.create_user(db, name=arguments['name'])
                    user_id_store[thread_id] = user_obj.id
                    output = {"user_id": user_obj.id, "name": user_obj.name}
                
                elif tool_call.function.name == "save_final_profile":
                    user_id = arguments.get('user_id') or user_id_store.get(thread_id)
                    if user_id:
                        output = crud.save_user_profile(
                            db,
                            user_id=user_id,
                            profile_data=arguments['profile_data']
                        )
                        del user_id_store[thread_id]
                    else:
                        output = {"status": "error", "message": "Could not find user_id for this thread."}

                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(output)
                })
            
            # CORRECTED: .beta is required
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
            continue

        if run.status == 'completed':
            # CORRECTED: .beta is required
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            assistant_message = messages.data[0].content[0].text.value
            return {"response": assistant_message, "thread_id": thread_id}

        if run.status in ['failed', 'cancelled', 'expired']:
            error_details = run.last_error
            print(f"Run ended with status: {run.status}. Error: {error_details}")
            raise HTTPException(status_code=500, detail=f"Run ended with status: {run.status}")
        
        break