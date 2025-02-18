# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

from gpt.openai_client import OpenAIClient
openai_client = OpenAIClient()
from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageToolCall

class CustomTransitionFunctions:
    # Custom function execution with deterministic state transition
    def __init__(self):
        self.summarize_prompt = "Please summarize the following conversation between a user and an AI health coach."       
            
    async def summarize(self, dialogue_history=None):
        # Call GPT to summarize, write to gpt-summary, and then return the next state        
        # return next(iter(self.function_input.values()), None)

        formatted_dialogue = []
        for annotated_response in dialogue_history:
            # Format each entry as "{Role}: {Content}"
            message = f"{annotated_response.role}: {annotated_response.response}"            
            formatted_dialogue.append(message)

        # Join all entries into one string, separated by newlines
        system_prompt = " \n".join([self.summarize_prompt] + formatted_dialogue)        
                
        messages = [{"role": "system", "content": system_prompt}]
        print("Message being sent for summarizing conversation to GPT: ", messages)

        response = await openai_client.chat_completion(
            messages=messages
        )

        reply_message = response.choices[0].message
        print("GPT Conversation Summary:", reply_message, "\n\n\n")

        return reply_message.content
        # return self.next_state_id