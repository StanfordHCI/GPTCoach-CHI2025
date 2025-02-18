# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

from gpt.openai_client import OpenAIClient
openai_client = OpenAIClient()
from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageToolCall

class StateClassifier:
    def __init__(self, classification_prompt, class_transitions):
        self.classification_prompt = classification_prompt
        self.class_transitions = class_transitions
        self.probe_frequency = 0

    def get_message_history_for_gpt(self, messages: list):
        # Converts annotated messages to messages for gpt
        dialogue_history = []
        for annotated_response in messages:
            message_dict = {"role": annotated_response.role, "content": annotated_response.response}
            if annotated_response.tool_calls:
                message_dict["tool_calls"] = annotated_response.tool_calls
            if annotated_response.role == "tool":
                message_dict["tool_call_id"] = annotated_response.tool_call_dict['tool_call_id']
                message_dict["name"] = annotated_response.tool_call_dict['name']
            dialogue_history.append(message_dict)
        return dialogue_history        

    async def classify_state(self, dialogue_history=None):
        print("Trying to classify state by calling GPT to evaluate dialogue history")

        # formatted_dialogue = []
        # for annotated_response in dialogue_history:
        #     # Format each entry as "{Role}: {Content}"
        #     message = {"role": f"{annotated_response.role}", "content": f"{annotated_response.response}"}            
        #     formatted_dialogue.append(message)   
        formatted_dialogue = self.get_message_history_for_gpt(dialogue_history)

        messages = [{"role": "system", "content": self.classification_prompt}] + \
            formatted_dialogue + \
            [{"role": "assistant", "content": "Given this conversation history, respond only with 'continue' or 'completed' depending on whether the task has been successfully completed."}]
        
        print("STATE CLASSIFIER message being sent to GPT: ", messages)

        response = await openai_client.chat_completion(
            messages=messages
        )

        reply_message = response.choices[0].message
        print("GPT State Classifier response:", reply_message, "\n\n\n")
        
        gpt_response = reply_message.content.lower()  # 'not_consented'  # Example response        
        
        next_state_id = self.class_transitions.get(gpt_response)

        return next_state_id