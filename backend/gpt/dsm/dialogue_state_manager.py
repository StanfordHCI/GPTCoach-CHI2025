# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

import os
import yaml
from gpt.dsm.dialogue_state import DialogueState
from gpt.dsm.annotated_response import AnnotatedResponse
from typing import Tuple, Union, List, Optional
from collections import OrderedDict

class DialogueStateManager:
    def __init__(self, base_directory):
        self.base_directory = base_directory
        # Assumes states are stored in memory or loaded once and accessible throughout the class
        self.states = {}  # Placeholder for states loaded from YAML
        self.parent_map = {}  # Maps state ID to its parent's state ID
        # self.load_states()
    
    def load_states(self):
        """Load states from YAML files into the self.states dictionary."""
        for root, dirs, files in os.walk(self.base_directory):
            for file in files:
                if file.endswith(".yml"):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        data = yaml.safe_load(f)
                        state_id = data.get('id', '')
                        # Assuming the state ID uniquely identifies each state
                        self.states[state_id] = DialogueState(data)
                        # Build parent map
                        for child_id in data.get('children', []):
                            self.parent_map[child_id] = state_id


    def get_state(self, state_id):
        """Retrieve a state object by its ID."""
        self.load_states()
        return self.states.get(state_id)


    def is_leaf_node(self, state_id):
        """Check if a state is a leaf node."""
        state = self.get_state(state_id)
        return not state.children

    def list_visited_states(self, annotated_response: AnnotatedResponse) -> List[DialogueState]:
        # Concatenating all parent states (start_state) and the current state (end_state)
        if annotated_response:
            visited_states = annotated_response.start_state + [annotated_response.end_state]
            return visited_states
        else:
            return []

    def get_most_recent_responses(self, annotated_responses: List[AnnotatedResponse]) -> Tuple[Optional[str], Optional[str]]:
        user_response, agent_response = None, None

        # Iterate from the end to the beginning
        for i in range(len(annotated_responses) - 1, -1, -1):
            response = annotated_responses[i]
            if response.role == "user" and user_response is None:
                user_response = response
            elif response.role == "assistant" and agent_response is None:
                agent_response = response
            
            # Break early if both responses are found
            if user_response and agent_response:
                break

        return user_response, agent_response    


    async def handle_transition(self, current_state, dialogue_history: List[AnnotatedResponse]=None):                
        next_state_name = None  
        # Check the transition type and determine the next state
        if current_state.transition_type == 'StateClassifier':            
            next_state_name = await current_state.transition.classify_state(dialogue_history)
        elif current_state.transition_type == 'id':
            next_state_name = current_state.transition
        elif current_state.transition_type == 'custom':
            next_state_name = current_state.transition          

        print("Transitions: next state is: ", next_state_name)                     
        if next_state_name:                   
            # self.mark_skipped_states(from_state, next_state_name)
            return next_state_name

    def ordered_set(self,iterable):
        if iterable:
            d = OrderedDict.fromkeys(iterable)
            return list(d.keys())
        return {}

    async def traverse(self, dialogue_history: List[AnnotatedResponse]):
        user_response, agent_response = self.get_most_recent_responses(dialogue_history) 
        # visited_states = set(self.list_visited_states(agent_response))
        
        visited_states = self.ordered_set(self.list_visited_states(agent_response))
        # current_state = visited_states[-1]
        print("Visited States: ", self.list_visited_states(agent_response))

        if len(visited_states) == 0 or visited_states[-1] == 'root': 
            # If the conversation has just started or the system has sent the first intro message
            return self.get_state('onboarding'), ['root']

        # current_state_id = stack[-1]  # Look at the last state without popping it        
        current_state_id = self.list_visited_states(agent_response)[-1]
        current_state = self.get_state(current_state_id)
        print(f"Handling state: {current_state_id}, prompt: {current_state.prompt}")
        next_state_id = await self.handle_transition(current_state, dialogue_history)                                  
        print(f"Next state is {next_state_id}")
        return self.get_state(next_state_id), visited_states
        
    async def get_next_system_prompt(self, dialogue_history: List[AnnotatedResponse]):
        # It will break if next state is None
        next_state, parent_states = await self.traverse(dialogue_history)
        if next_state:
            print(f"Returning system prompt for next state {next_state.id}")
            return AnnotatedResponse(role='system', 
            response=next_state.prompt, start_state=parent_states,
            end_state=next_state.id, transition=None)
            # return next_state.prompt
        return None