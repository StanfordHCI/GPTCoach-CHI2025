# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageToolCall
from gpt.dsm.annotated_response import AnnotatedResponse
from firebase_admin import firestore
from google.cloud.firestore_v1 import ArrayUnion

from firebase import FirebaseManager
firebase_manager = FirebaseManager()


def write_message_to_db(user_id: str, session_id: str, message: dict | ChatCompletionMessage | AnnotatedResponse, state_metadata=None):
    messages_doc_ref = firebase_manager.get_user_doc(user_id).collection('gpt-messages').document(session_id)        

    if isinstance(message, ChatCompletionMessage):
        if message.content or message.content != "None":
            message_dict = {"role": message.role, "response": message.content}        
        else:
            message_dict = {"role": message.role, "response": "NO RESPONE FROM GPT"}        
        if message.tool_calls:
            message_dict["tool_calls"] = [call.model_dump() for call in message.tool_calls]
        if state_metadata:
            message_dict["start_state"] = state_metadata["start_state"]
            message_dict["end_state"] = state_metadata["end_state"]
            message_dict["transition"] = state_metadata["transition"]
            message_dict["strategy"] = state_metadata["strategy"]
            message_dict["rewind"] = False            
    elif isinstance(message, AnnotatedResponse):
        # Convert AnnotatedResponse to a dictionary format suitable for Firebase
        message_dict = message.__dict__
    else:
        # Assume the message is already a dictionary
        message_dict = message
        if not message_dict.get('rewind'):
            message_dict['rewind'] = False

    # Update the document with the new message
    messages_doc_ref.update({"messages": ArrayUnion([message_dict])})

