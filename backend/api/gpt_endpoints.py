# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

# This file defines the endpoints for sending GPT messages

from fastapi import APIRouter, WebSocket, HTTPException, WebSocketDisconnect
from datetime import datetime, timedelta
import openai
import pytz
from websockets.exceptions import ConnectionClosed
from gpt.messages import process_message, fetch_user_summary, resume_conversation, rewind_conversation
from gpt.dsm.dialogue_state_manager import DialogueStateManager
from gpt.openai_client import OpenAIClient
openai_client = OpenAIClient()

router = APIRouter(prefix="/gpt")

from firebase import FirebaseManager
firebase_manager = FirebaseManager()

def get_most_recent_session_id(user_id):
    collection_ref =  firebase_manager.get_user_doc(user_id).collection('gpt-messages')
    session_ids = []
    for doc in collection_ref.stream():
        session_ids.append(doc.id)

    # Function to extract and parse timestamps from filenames
    def extract_timestamp(filename):
        # Extract timestamp part from the filename
        timestamp_str = filename.split('session-')[-1]
        # Ignore timezone for parsing since all times are in UTC
        timestamp_str = timestamp_str[:-6]  # Remove the timezone offset "+00:00"
        # Parse the timestamp string into a datetime object
        timestamp_format = "%Y-%m-%dT%H:%M:%S.%f"
        timestamp = datetime.strptime(timestamp_str, timestamp_format)
        return timestamp
    
    current_time = datetime.utcnow()
    current_time_iso = datetime.now(tz=pytz.utc).isoformat()
    
    if len(session_ids) != 0:
        most_recent_session_id = max(session_ids, key=lambda fn: extract_timestamp(fn))
        time_diff = current_time - extract_timestamp(most_recent_session_id)
        print("Most recent session time diff: ", time_diff)
        # Check if the most recent timestamp is within the last 5 minutes
        if time_diff > timedelta(minutes=60):
            print("Most recent session has been active for longer than 5 minutes. Getting new session id...")
            most_recent_session_id = f"session-{current_time_iso}"        
    else:
        most_recent_session_id = f"session-{current_time_iso}"        

    return most_recent_session_id 
        

# API endpoints -------------------------------------------------------------------------
@router.websocket("/ws/{user_id}/")
async def websocket_endpoint(user_id: str, websocket: WebSocket):
    print("Initializing websocket endpoint for user_id", user_id, websocket)
    # Connect a websocket to the frontend
    if not firebase_manager.is_valid_user_id(user_id):
        print("invalid user id!")
        raise HTTPException(status_code=401, detail="Invalid user id!")
    
    await websocket.accept()
    dialogue_manager = DialogueStateManager(base_directory='../prompts/dialogue/states')

    try:
        # Fetch summary from gpt
        user_summary = fetch_user_summary(user_id)

        # Find the most recent session_id. If it doesn't exist, create a new one
        session_id = get_most_recent_session_id(user_id)            
        print("SESSION ID: ", session_id)

        await resume_conversation(user_id, session_id, websocket)

        while True:
            # Receive a message from the frontend
            data = await websocket.receive_json()
            if data["type"] == "message":  
                print(f"Received chat message {data}\n")

                prompt = data["prompt"]
                user_id = data["user_id"]
            
                try:
                    await process_message(prompt, user_id=user_id, session_id=session_id, dialogue_manager=dialogue_manager, websocket=websocket)
                except openai.BadRequestError as e:
                    if e.code == 'context_length_exceeded':
                        print("Context length exceeded. Updating model to GPT-4 Turbo...")
                        openai_client.update_model('gpt-4-turbo')
                    else:
                        print(f"Unhandled OpenAI error: {e}")
                        return
                    
                    await process_message(prompt, user_id=user_id, session_id=session_id, dialogue_manager=dialogue_manager, websocket=websocket)

            elif data["type"] == "rewind":
                print("Rewinding conversation...")
                await rewind_conversation(user_id, session_id, websocket)

    except ConnectionClosed as e:
        print("Connection closed:", e)
        return
    except Exception as e:
        print("Exception occurred:", e)
        return