# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

from pydantic import BaseModel

class GPTMessage(BaseModel):
    # Base model class for a gpt message (role is "user" or "assistant", content is the actual message)
    role: str
    content: str


class GPTFunctionCall(BaseModel):
    # Base model class for a GPT function call (function name, and agumants as a dict)
    name: str
    args: dict


class GPTResponse(BaseModel):
    # Class representing a response from GPT - contains a message and a list of functions to call
    message: GPTMessage
    functions: list[GPTFunctionCall]

