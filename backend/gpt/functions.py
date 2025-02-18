# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

from async_lru import alru_cache
from data.fetch import fetch_aggregated_data
from data.data_sources import get_user_data_sources
from data.visualize import generate_vizualization
from fastapi import WebSocket

import json
import traceback
from firebase import FirebaseManager
firebase_manager = FirebaseManager()

from data.fetch import fetch_aggregated_data
from openai.types.chat import ChatCompletionMessageToolCall
from gpt.utils import write_message_to_db

async def handle_function_call(tool_call: ChatCompletionMessageToolCall, web_socket: WebSocket, user_id: str, session_id: str):
    try:
        function_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        args["user_id"] = user_id
        args["web_socket"] = web_socket
        args["session_id"] = session_id

        args['data_source_name'] = "health.stepcount"
        args['granularity'] = "month"
        args['date'] = '2024-09-16'

        print(f"Calling function {function_name} with args: {args}")
        if function_name == "describe":
            fn = describe
        elif function_name == "visualize":
            fn = visualize
        elif function_name == "finish":
            fn = finish
        else:
            print(f"=> ERROR: {function_name} does not exist!")
            return f"{function_name} does not exist"
        
        result = await fn(**args)
        print(f" => {result}")

        return result
    except Exception as error:
        print(f" => ERROR: {error}")
        traceback.print_exc()
        return f"An error occured: {error.with_traceback(None)}"


# Function callbacks ----------------------------------------------------------------
@alru_cache(maxsize=128)
async def visualize(web_socket: WebSocket, user_id, session_id, data_source_name, date="", granularity=""):
    # Send a json descripton over the web socket
    # Send a text description back to GPT
    await web_socket.send_json({
        "type": "loading",
        "content": "Fetching data..."
    })
    viz_text, viz_json = await generate_vizualization(user_id, data_source_name, date, granularity)

    if viz_json:
        await web_socket.send_json(viz_json)
        write_message_to_db(user_id, session_id, viz_json)

    return viz_text

async def finish(description, user_id):
    # Completed the interview process
    firebase_manager.get_user_doc(user_id).set({"gpt-summary": description}, merge=True)
    return "You have completed the user interview! End the conversation."

@alru_cache(maxsize=128)
async def describe(web_socket: WebSocket, user_id, session_id, data_source_name, start, end, granularity):
    # Get the descriptive statistics for the data source
    await web_socket.send_json({
        "type": "loading",
        "content": "Fetching data..."
    })
    aggregated_data, description_string = await fetch_aggregated_data(user_id, data_source_name, start, end, granularity)
    return description_string

# -----------------------------------------------------------------------------------

# TODO: move this to separate files
describe_description = '''
This function returns a summary of descriptive statistics for a given data source over a given time period and granularity. 

This function fetches all data within the [start, end] time period (inclusive) for the given data source and aggregates the data into buckets based on the granularity. The appropriate aggregation function (sum, mean) is used based on the data type of the data source (count, rate) and the granularity.

DO NOT PERFORM ANY ARITHMETIC TO THE OUTPUT OF THE FUNCTION. YOU SHOULD ALWAYS REPORT THE NUMBERS EXACTLY AS OUTPUTTED BY THE FUNCTION. 
If the output of the function does not match your expected query, make another function call with the appropriate arguments. 
'''

def get_functions_dict(user_id: str):
    # Normal functions
    return [
        # `describe` function ------------------------------------------------------------
        {
            "type": "function",
            "function": { 
                "name": "describe",
                "description": f"{describe_description}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data_source_name": {
                            "type": "string",
                            "enum": get_user_data_sources(user_id),
                            "description": "The name of the data source to fetch data for.",
                        },
                        "start": {
                            "type": "string",
                            "description": "The date to fetch data for, in YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS format. If no time is specified, the function will fetch data for the entire day."
                        },
                        "end": {
                            "type": "string",
                            "description": "The date to fetch data for, in YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS format. If no time is specified, the function will fetch data for the entire day."
                        },
                        "granularity": {
                            "type": "string",
                            "enum": ["15min", "hour", "day", "week", "month"],
                            "description": "The granularity of the time buckets to aggregate the data into. For example, if the granularity is 'hour', the function will return the data aggregated into hourly buckets. If the granularity is 'week', the function will return the data aggregated into weekly buckets. Note that a week is defined as starting on Sunday and ending on Saturday."
                        }
                    },
                    "required": ["data_source_name", "start", "end", "granularity"]
                }
            }
        },
        # `visualize` function ------------------------------------------------------------
        {
            "type": "function",
            "function": { 
                "name": "visualize",
                "description": "This function shows the user a graph of their data in the specified time period. It will also return some summary statistics, that you can use to anaylze the user's data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data_source_name": {
                            "type": "string",
                            "enum": [s for s in get_user_data_sources(user_id) if s != "health.workout"],
                            "description": "The name of the data source to visualize. Workouts are not supported for visualization and you should call describe on health.workout instead.",
                        },
                        "date": {
                            "type": "string",
                            "description": "The date around which to base the visualizaition, in YYYY-MM-DD format"
                        },
                        "granularity": {
                            "type": "string",
                            "enum": ["day", "week", "month"],
                            "description": "The time period to visualize over (day, week, month)"
                        }
                    },
                    "required": ["data_source_name", "date_string", "granularity"]
                }
            }
        }
    ]