# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

class AnnotatedResponse:
    def __init__(self, role, response, start_state=None, end_state=None, transition=None, tool_calls=None, tool_call_dict=None, strategy=None, rewind=False):
        self.role = role
        self.response = response
        self.start_state = start_state
        self.end_state = end_state
        self.tool_calls = tool_calls
        self.tool_call_dict = tool_call_dict
        self.strategy = strategy
        self.rewind = rewind
        
        if self.role == "agent":
            self.transition = None
        else:
            self.transition = transition
