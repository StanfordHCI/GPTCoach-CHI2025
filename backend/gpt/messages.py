# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

from fastapi import WebSocket

from gpt.openai_client import OpenAIClient
openai_client = OpenAIClient()
from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageToolCall

from firebase_admin import firestore
from google.cloud.firestore_v1 import ArrayUnion

from datetime import datetime
import pytz

from gpt.functions import handle_function_call, get_functions_dict
from gpt.dsm.annotated_response import AnnotatedResponse
from gpt.dsm.dialogue_state_manager import DialogueStateManager
from gpt.utils import write_message_to_db

from firebase import FirebaseManager
firebase_manager = FirebaseManager()

# Load system prompts
with open("../prompts/system_prompt.txt", "r") as file:
    GPT_SYSTEM_PROMPT = file.read()
    GPT_SYSTEM_PROMPT = GPT_SYSTEM_PROMPT.replace("{DATE_STRING}", datetime.now(tz=pytz.timezone("US/Pacific")).strftime("%Y-%m-%d"))
with open("../prompts/strategies.txt", "r") as file:
    GPT_PROMPT_STRATEGIES = file.read()
with open("../prompts/predict_strategy.txt", "r") as file:
    GPT_PROMPT_PREDICT_STRATEGY = file.read()    
with open("../prompts/generate_response.txt", "r") as file:
    GPT_PROMPT_GENERATE_RESPONSE = file.read()    
with open("../prompts/few_shot_function_calls.txt", "r") as file:
    GPT_PROMPT_FEW_SHOT_FUNCTION_CALLS = file.read()        
with open("../prompts/tool_call_use.txt", "r") as file:
    GPT_PROMPT_TOOL_CALL_USE = file.read()    
with open("../prompts/predict_tool_call_use.txt", "r") as file:
    GPT_PROMPT_PREDICT_TOOL_CALL_USE = file.read()    

with open("../prompts/predict_strategy_agent.txt", "r") as file:
    AGENT_PROMPT_PREDICT_STRATEGY = file.read()
with open("../prompts/generate_response_agent.txt", "r") as file:
    AGENT_PROMPT_GENERATE_RESPONSE = file.read()
with open("../prompts/tool_call_use_agent.txt", "r") as file:
    AGENT_PROMPT_TOOL_CALL_USE = file.read()    
with open("../prompts/predict_tool_call_use_agent.txt", "r") as file:
    AGENT_PROMPT_PREDICT_TOOL_CALL_USE = file.read()    


# Helper functions -----------------------------------------------------------------------------
def fetch_message_history(user_id: str, session_id: str) -> list:
    messages_doc_ref = firebase_manager.get_user_doc(user_id).collection('gpt-messages').document(session_id)
    messages_doc = messages_doc_ref.get()

    if not messages_doc.exists:
        # Document does not exist - make an empty list
        messages_doc_ref.set({"messages": []}, merge=True)
        return []

    return messages_doc.to_dict().get("messages", [])    

# Helper functions -----------------------------------------------------------------------------
def get_annotated_message_history(messages: list):
    dialogue_history = []
    print("MESSAGES: ", messages)
    tool_call_dict = None    
    for msg in messages:
        if msg.get('rewind') or msg.get('type') == 'visualization':
            continue 
        # Each message in messages has 'role', 'response', 'start_state', 'end_state', and 'transition' fields        
        role = msg.get('role')        
        response = msg.get('response')
        start_state = msg.get('start_state', []) 
        end_state = msg.get('end_state', [])
        transition = msg.get('transition', None)
        tool_calls = msg.get('tool_calls', None)

        if role == "tool":
            tool_call_dict = {'name': msg.get('name'), 'tool_call_id': msg.get('tool_call_id')}
        # Create an AnnotatedResponse object for each message
        annotated_response = AnnotatedResponse(role, response, start_state, end_state, transition, tool_calls, tool_call_dict)
        dialogue_history.append(annotated_response)

    return dialogue_history

def get_message_history_for_gpt(messages: list):
    # Converts annotated messages to messages for gpt
    dialogue_history = []
    for msg in messages:
        if msg.get('rewind') or msg.get('type') == 'visualization':
            continue 
        message_dict = {"role": msg.get('role'), "content": msg.get('response')}
        if msg.get('tool_calls'):
            message_dict["tool_calls"] = msg.get('tool_calls')
        if msg.get('role') == "tool":
            message_dict["tool_call_id"] = msg.get('tool_call_id')
            message_dict["name"] = msg.get('name')
        dialogue_history.append(message_dict)
    return dialogue_history    


def fetch_user_summary(user_id: str) -> str:
    # Get a user's summary from firebase (assuming their document exists already)
    user_snapshot = firebase_manager.get_user_doc(user_id).get()    
    return user_snapshot.to_dict().get("gpt-summary")

def write_user_summary_to_db(user_id: str, description: str):
    # Write the user's summary to firebase (assuming their document exists already)
    firebase_manager.get_user_doc(user_id).set({"gpt-summary": description}, merge=True)    

def write_function_to_db(user_id: str, session_id: str, tool_call: ChatCompletionMessageToolCall, result, state_metadata=None):
    messages_doc_ref = firebase_manager.get_user_doc(user_id).collection('gpt-messages').document(session_id)        

    message_dict = {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_call.function.name,
                "response": result
            }
    
    if state_metadata:
        message_dict["start_state"] = state_metadata["start_state"]
        message_dict["end_state"] = state_metadata["end_state"]
        message_dict["transition"] = state_metadata["transition"]
        message_dict["strategy"] = state_metadata["strategy"]

    messages_doc_ref.update({
        "messages": ArrayUnion([message_dict])
    })

async def get_gpt_response(user_id: str, messages: list, tool_call=True, force_tool_call=False):
    # Send a list of messages to GPT and return the response
    if tool_call:
        response = await openai_client.chat_completion(
            messages=messages,
            tools=get_functions_dict(user_id),
            tool_choice={"type": "function", "function": {"name": "visualize"}} if force_tool_call else 'auto'
        )
    else:
        response = await openai_client.chat_completion(
            messages=messages        
        )
    return response

async def resume_conversation(user_id: str, session_id: str, websocket: WebSocket):
    # Resume a conversation with a user
    print("Resuming conversation")
    # Reset the frontend to clear the chat 
    message_history = fetch_message_history(user_id, session_id)
    if len(message_history) == 0:
        msg = "Hello, it's wonderful to meet you! I'm a health coaching chatbot and am excited that you're here to start this journey with me. How are you doing today?"
        intro_message = {
            "type": "message", 
            "role": "assistant",
            "state": "root",
            "strategy": "Filler",
            "content": msg
        }                
        await websocket.send_json(intro_message)   
        # Database parses text with key "response" not "content", which GPT uses, so we have to change it
        write_message_to_db(user_id, session_id, {
            "type": "message", 
            "role": "assistant",
            "end_state": "root",
            "strategy": "Filler",
            "response": msg
        })        

    else:
        reset_message = {
            "type": "reset"
        }
        await websocket.send_json(reset_message) 
        for message in message_history:
            if not message.get('rewind'):
                if (message.get('role') != "tool") and (message.get('response')):  
                    # Handle tool call messages to not be sent to the frontend          
                    if ("NO RESPONE FROM GPT" not in message.get('response')) or ("Message: None" not in message.get('response')):   
                        await websocket.send_json({
                            "type": "message",
                            "role": message.get('role'),
                            "content": message.get('response'),
                            "state": message.get('end_state'),
                            "strategy": message.get('strategy')
                        })
                if (message.get('type')=="visualization") :
                    await websocket.send_json(message)      

def update_message_from_db(user_id: str, session_id: str, message_idx, field, updated_value):
    messages_doc_ref = firebase_manager.get_user_doc(user_id).collection('gpt-messages').document(session_id) 
    messages_doc = messages_doc_ref.get()    
    messages = messages_doc.to_dict().get("messages", [])   
    
    messages[message_idx][field] = updated_value
    
    messages_doc_ref.update({
    "messages": messages
    })    
    messages_doc_ref = firebase_manager.get_user_doc(user_id).collection('gpt-messages').document(session_id) 
    messages_doc = messages_doc_ref.get()


async def rewind_conversation(user_id: str, session_id: str, websocket: WebSocket):
    # Resume a conversation with a user    
    message_history = fetch_message_history(user_id, session_id)
    
    # Update the rewind field of the last user message with rewind as False
    for i in range(len(message_history) - 1, -1, -1):
        message = message_history[i]
        if (message.get('role') == "user") and (not message.get("rewind")):                        
            user_msg_idx = i            
            update_message_from_db(user_id, session_id, user_msg_idx, "rewind", True)            
            break
    
    # Update the rewind field of all the messages after the last user message with rewind as False
    for j in range(user_msg_idx, len(message_history)):
        if not message.get("rewind"):  
            update_message_from_db(user_id, session_id, j, "rewind", True)

    # Send confirmation to the frontend to sync the rewind    
    await websocket.send_json({
        "type": "rewind_confirmation",
        "content": "success",
    })
    print("Rewind confirmation sent to frontend")


async def predict_strategy(user_id, user_message, annotated_system_prompt, message_history_for_gpt, prev_attempts=0, AGENT_PROMPT_PREDICT_STRATEGY=AGENT_PROMPT_PREDICT_STRATEGY):
    STRATEGIES = [
        "Advise with Permission", 
        "Affirm", 
        "Facilitate", 
        "Filler", 
        "Giving Information", 
        "Question", 
        "Raise Concern", 
        "Reflect", 
        "Reframe", 
        "Support", 
        "Structure"
    ]
    
    system_prompt_strategy_prediction = " \n".join([GPT_SYSTEM_PROMPT, 
                                                    annotated_system_prompt.response, 
                                                    GPT_PROMPT_PREDICT_STRATEGY, 
                                                    GPT_PROMPT_STRATEGIES])
            
    AGENT_PROMPT_PREDICT_STRATEGY = AGENT_PROMPT_PREDICT_STRATEGY.replace("{TASK}", annotated_system_prompt.response)        
    AGENT_PROMPT_PREDICT_STRATEGY = AGENT_PROMPT_PREDICT_STRATEGY.replace("{STRATEGIES}", ', '.join(STRATEGIES))        
    
    print("PREDICT STRATEGY SYSTEM PROMPT: ", system_prompt_strategy_prediction)
    print("PREDICT STRATEGY AGENT PROMPT: ", AGENT_PROMPT_PREDICT_STRATEGY)
    # Message for strategy prediction that is being sent to GPT: Concats the system prompt, message history, user message, and a prompt for the user to select a strategy        
    strategy_prediction_message = [{"role": "system", "content": system_prompt_strategy_prediction}] + \
                            message_history_for_gpt + \
                            [{"role": "user", "content": user_message}] + \
                            [{"role": "assistant", "content": AGENT_PROMPT_PREDICT_STRATEGY}]
    
    response = await get_gpt_response(user_id, strategy_prediction_message, tool_call=False)
    strategy_prediction = response.choices[0].message.content
    print("PREDICT STRATEGY MESSAGE: ", strategy_prediction)
    
    if strategy_prediction not in STRATEGIES:
        if prev_attempts < 3:
            print("Strategy prediction failed. Trying again...")
            return await predict_strategy(user_id, user_message, annotated_system_prompt, message_history_for_gpt, prev_attempts + 1)
        else:
            return "Filler" 
    return strategy_prediction 


async def should_use_tool(user_id, strategy_description, annotated_system_prompt, message_history_for_gpt, prev_attempts=0, AGENT_PROMPT_TOOL_CALL_USE=AGENT_PROMPT_TOOL_CALL_USE):
    TOOL_CALL_USE = [
        "yes", 
        "no"
    ]

    system_prompt_tool_call_use = " \n".join([GPT_SYSTEM_PROMPT, 
                                              annotated_system_prompt.response, 
                                              GPT_PROMPT_TOOL_CALL_USE,
                                              GPT_PROMPT_FEW_SHOT_FUNCTION_CALLS
                                              ])     

    AGENT_PROMPT_TOOL_CALL_USE = AGENT_PROMPT_TOOL_CALL_USE.replace("{TASK}", annotated_system_prompt.response)
    AGENT_PROMPT_TOOL_CALL_USE = AGENT_PROMPT_TOOL_CALL_USE.replace("{STRATEGY_DESCRIPTION}", strategy_description)
    # Message for strategy prediction that is being sent to GPT: Concats the system prompt, message history, user message, and a prompt for the user to select a strategy        
    
    print("SHOULD USE TOOL SYSTEM PROMPT: ", system_prompt_tool_call_use)
    print("SHOULD USE TOOL AGENT PROMPT: ", AGENT_PROMPT_TOOL_CALL_USE)

    tool_call_use_message = [{"role": "system", "content": system_prompt_tool_call_use}] + \
                            message_history_for_gpt + \
                            [{"role": "assistant", "content": AGENT_PROMPT_TOOL_CALL_USE}]
    
    response = await get_gpt_response(user_id, tool_call_use_message, tool_call=False)
    tool_call_use = response.choices[0].message.content.lower()    
    print("SHOULD USE TOOL RESPONSE: ", tool_call_use)
    
    if tool_call_use not in TOOL_CALL_USE:
        if prev_attempts < 3:
            print("TOOL CALL prediction failed. Trying again...")
            return await tool_call_use(user_id, strategy_description, annotated_system_prompt, message_history_for_gpt, prev_attempts + 1)
        else:
            return "no" 
    return "yes"
    return tool_call_use 

async def generate_tool_call(user_id, strategy_description, annotated_system_prompt, message_history_for_gpt, AGENT_PROMPT_PREDICT_TOOL_CALL_USE=AGENT_PROMPT_PREDICT_TOOL_CALL_USE):
    # Predict the tool call to use based on the strategy and the GPT response

        # Predict the response given the strategy
    system_prompt_tool_call_prediction = " \n".join([GPT_SYSTEM_PROMPT, 
                                                     annotated_system_prompt.response, 
                                                     GPT_PROMPT_PREDICT_TOOL_CALL_USE, 
                                                     GPT_PROMPT_FEW_SHOT_FUNCTION_CALLS]) 
            
    AGENT_PROMPT_PREDICT_TOOL_CALL_USE = AGENT_PROMPT_PREDICT_TOOL_CALL_USE.replace("{TASK}", annotated_system_prompt.response)                
    AGENT_PROMPT_PREDICT_TOOL_CALL_USE = AGENT_PROMPT_PREDICT_TOOL_CALL_USE.replace("{STRATEGY_DESCRIPTION}", strategy_description)                

    print("GENERATE TOOL CALL SYSTEM PROMPT: ", system_prompt_tool_call_prediction)
    print("GENERATE TOOL CALL AGENT PROMPT: ", AGENT_PROMPT_PREDICT_TOOL_CALL_USE)

    tool_call_prediction_message= [{"role": "system", "content": system_prompt_tool_call_prediction}] + \
        message_history_for_gpt + \
        [{"role": "assistant", "content": AGENT_PROMPT_PREDICT_TOOL_CALL_USE}]
        
    response = await get_gpt_response(user_id, tool_call_prediction_message, tool_call=True, force_tool_call=True)  
    print("GENERATE TOOL CALL RESPONSE:", response, "\n\n\n")    
    return response 


async def predict_gpt_response(user_id, user_message, strategy, strategy_description, system_prompt_response_prediction, annotated_system_prompt, message_history_for_gpt, AGENT_PROMPT_GENERATE_RESPONSE=AGENT_PROMPT_GENERATE_RESPONSE):        
        # Predict the response given the strategy
   
    AGENT_PROMPT_GENERATE_RESPONSE = AGENT_PROMPT_GENERATE_RESPONSE.replace("{TASK}", annotated_system_prompt.response)
    AGENT_PROMPT_GENERATE_RESPONSE = AGENT_PROMPT_GENERATE_RESPONSE.replace("{STRATEGY_DESCRIPTION}", strategy_description)
    AGENT_PROMPT_GENERATE_RESPONSE = AGENT_PROMPT_GENERATE_RESPONSE.replace("{STRATEGY}", strategy)
    response_prediction_message = [{"role": "system", "content": system_prompt_response_prediction}] + \
                        message_history_for_gpt + \
                        [{"role": "user", "content": user_message}] + \
                        [{"role": "assistant", "content": AGENT_PROMPT_GENERATE_RESPONSE}]
    
    print("GPT RESPONSE SYSTEM PROMPT: ", system_prompt_response_prediction)
    print("GPT RESPONSE AGENT PROMPT: ", AGENT_PROMPT_GENERATE_RESPONSE)

    # print("RESPONSE PREDICTION")
    # for msg in response_prediction_message:
    #     print(f"{msg['role']}: {msg['content']}")
    
    response = await get_gpt_response(user_id, response_prediction_message, tool_call=True)        
    print("GPT RESPONSE MESSAGE: ", response)
    return response     

DEMO = True
async def process_message(user_message: str, user_id: str, session_id: str, dialogue_manager: DialogueStateManager, websocket: WebSocket):
    # Send the a message (from a specific user) to GPT
    # Send all frontend-bound function calls and response message back over the web socket
    # Initialize client if not already    
    with open("../prompts/generate_response_agent.txt", "r") as file:
        AGENT_PROMPT_GENERATE_RESPONSE = file.read()    

    await websocket.send_json({
        "type": "loading",
        "content": "Processing message..."
    })

    # Create a user annotated message based on user input to frontend
    user_annotated_message = AnnotatedResponse(role='user', response=user_message)    

    # Fetch history and summary
    message_history = fetch_message_history(user_id, session_id)
    annotated_message_history = get_annotated_message_history(message_history)                
    message_history_for_gpt = get_message_history_for_gpt(message_history)
    annotated_message_history.append(user_annotated_message)
    
    # Get the next state from the dialogue state tree and the corresponding system prompt
    annotated_system_prompt = await dialogue_manager.get_next_system_prompt(annotated_message_history) 

    # Refine this because redefine the object is wasteful
    user_annotated_message = AnnotatedResponse(role='user', response=user_message, 
                                               start_state=annotated_system_prompt.start_state[:-1], 
                                               end_state=annotated_system_prompt.start_state[-1], 
                                               transition=annotated_system_prompt.end_state)    
    write_message_to_db(user_id, session_id, user_annotated_message)    
 
    # Get the strategy from the response
    strategy = await predict_strategy(user_id, user_message, annotated_system_prompt, message_history_for_gpt)

    # Get the strategy description based on the predicted strategy    
    with open(f"../prompts/strategies/{''.join('_' if c == ' ' else c for c in strategy.lower())}.txt", "r") as file:
        STRATEGY_DESCRIPTION = file.read()    

    # # Predict the response given the strategy
    # system_prompt_response_prediction = " \n".join([GPT_SYSTEM_PROMPT] + 
    #                            [annotated_system_prompt.response] + 
    #                            [GPT_PROMPT_GENERATE_RESPONSE] + 
    #                            [GPT_PROMPT_STRATEGIES] + 
    #                            [GPT_PROMPT_FEW_SHOT_FUNCTION_CALLS])
        
    # AGENT_PROMPT_GENERATE_RESPONSE = AGENT_PROMPT_GENERATE_RESPONSE.replace("{TASK}", annotated_system_prompt.response)
    # AGENT_PROMPT_GENERATE_RESPONSE = AGENT_PROMPT_GENERATE_RESPONSE.replace("{STRATEGY_DESCRIPTION}", STRATEGY_DESCRIPTION)
    # AGENT_PROMPT_GENERATE_RESPONSE = AGENT_PROMPT_GENERATE_RESPONSE.replace("{STRATEGY}", strategy)
    # response_prediction_message = [{"role": "system", "content": system_prompt_response_prediction}] + \
    #                     message_history_for_gpt + \
    #                     [{"role": "user", "content": user_message}] + \
    #                     [{"role": "assistant", "content": AGENT_PROMPT_GENERATE_RESPONSE}]
    
    # print("RESPONSE PREDICTION")
    # for msg in response_prediction_message:
    #     print(f"{msg['role']}: {msg['content']}")

    # response = await get_gpt_response(user_id, response_prediction_message, tool_call=True)
    system_prompt_response_prediction = " \n".join([GPT_SYSTEM_PROMPT, 
                                                    annotated_system_prompt.response, 
                                                    GPT_PROMPT_GENERATE_RESPONSE, 
                                                    GPT_PROMPT_STRATEGIES, 
                                                    GPT_PROMPT_FEW_SHOT_FUNCTION_CALLS])
 
    gpt_response = await predict_gpt_response(user_id, user_message, strategy, STRATEGY_DESCRIPTION, system_prompt_response_prediction, annotated_system_prompt, message_history_for_gpt)
    
    reply_message = gpt_response.choices[0].message
    print("INTERMEDIATE RESPONSE: ", reply_message)
    
    tool_call_use_response = 'no' 
    
    # If the response does not contain tool calls, manually chain-of-thought prompt to use a tool
    if not reply_message.tool_calls:    
        tool_call_use_message_history = message_history_for_gpt + [{"role": "user", "content": user_message}] + [reply_message]             
        tool_call_use_response = await should_use_tool(user_id, STRATEGY_DESCRIPTION, annotated_system_prompt, tool_call_use_message_history)    

        if tool_call_use_response == 'yes':
            predict_tool_call_use_response = await generate_tool_call(user_id, STRATEGY_DESCRIPTION, annotated_system_prompt, tool_call_use_message_history)
            print("TOOL CALL RESPONSE: ", predict_tool_call_use_response)

            reply_message = predict_tool_call_use_response.choices[0].message
            reply_json = {
                "role": reply_message.role,
                "tool_calls": reply_message.tool_calls
            }
        else:
            reply_json = {
                "role": reply_message.role,
                "content": reply_message.content
            }
    else:
        reply_json = {
            "role": reply_message.role,
            "tool_calls": reply_message.tool_calls
        }

    agent_state_metadata = {
        "start_state": annotated_system_prompt.start_state,
        "end_state": annotated_system_prompt.end_state,
        "strategy": strategy,
        "transition": None
    }

    write_message_to_db(user_id, session_id, reply_message, agent_state_metadata)    

    messages = [{"role": "system", "content": system_prompt_response_prediction}] + \
                        message_history_for_gpt + \
                        [{"role": "user", "content": user_message}] + \
                        [reply_json]
    
    tool_calls = reply_message.tool_calls

    # Call all functions
    if tool_calls:
        print("Tool calls: ", tool_calls)
        for tool_call in tool_calls:
            result = await handle_function_call(tool_call, websocket, user_id, session_id)
            # result = await handle_function_call(tool_call)

            await websocket.send_json({
                "type": "loading",
                "content": "Analyzing data..."
            })

            if result == None:
                result = "I could not fetch anything because there was no data. Please don't be mad."
            
            if len(result) > 1500:
                print("Data too long. Summarizing...")
                summarize_system_prompt = "Please summarize the following conversation between a user and an AI health coach."
                summarize_result_prompt = [{"role": "system", "content": " \n".join([summarize_system_prompt] + [result])}]
                summarized_result = await get_gpt_response(user_id, summarize_result_prompt, tool_call=False)
                result = "Summarized function call data: \n\n" + summarized_result.choices[0].message.content                

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_call.function.name,
                "content": result
            })

            write_function_to_db(user_id, session_id, tool_call, result)

        # Call response again, without ability to call functions
        second_response = await openai_client.chat_completion(
            messages=messages
        )

        reply_message = second_response.choices[0].message
        write_message_to_db(user_id, session_id, reply_message, agent_state_metadata)

    await websocket.send_json({
        "type": "message",
        "role": reply_message.role,
        # "content": f"State: {annotated_system_prompt.end_state}\n\nStrategy: {strategy}\n\n" + reply_message.content,      
        "content": reply_message.content,      
        "state": annotated_system_prompt.end_state,
        "strategy": strategy  
    })