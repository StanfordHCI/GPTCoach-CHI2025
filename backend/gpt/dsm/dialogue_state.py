# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

import yaml
from gpt.dsm.state_classifier import StateClassifier
from gpt.dsm.custom_transition_function import CustomTransitionFunctions

class DialogueState:
    def __init__(self, data):

        self.id = data['id']
        self.prompt = data.get('prompt', '')
        self.children = data.get('children', [])

        self.initial_child_state = None
        self.final_child_state = None

        if self.children:
            self.initial_child_state = self.children[0]
            self.final_child_state = self.children[-1]

        self.function_calls = data['function_calls']

        # Initialize transition attributes
        self.transition = None
        self.transition_type = None
        self.custom_transition_function = None
        
        transition_data = data.get('transition')
        if transition_data:            
            # Check if both 'prompt' and 'classification_prompt' exist in the data
            if 'prompt' in data and 'transition' in data and 'classification_prompt' in transition_data:
                # Replace {prompt} in the classification_prompt with the actual prompt value
                data['transition']['classification_prompt'] = data['transition']['classification_prompt'].format(prompt=self.prompt)

            if transition_data.get('type') == 'id':
                self.transition = transition_data.get('state')
                self.transition_type = 'id'
            elif transition_data.get('type') == 'StateClassifier':
                self.transition = StateClassifier(
                    classification_prompt=transition_data['classification_prompt'],
                    class_transitions=transition_data['class_transitions']
                )
                self.transition_type = 'StateClassifier'       
            elif transition_data.get('type') == 'custom':
                self.transition = transition_data.get('state')                            
                self.transition_type = 'custom'                
                self.custom_transition_function = getattr(CustomTransitionFunctions, transition_data['function'], None)