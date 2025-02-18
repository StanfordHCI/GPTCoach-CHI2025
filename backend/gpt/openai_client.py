# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

import openai

API_KEY = ''
BASE_MODEL = 'gpt-4'

class OpenAIClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenAIClient, cls).__new__(cls)
            cls._instance.model = BASE_MODEL
            cls._instance.client = openai.AsyncClient(api_key=API_KEY)
        return cls._instance

    async def chat_completion(self, **kwargs):
        return await self._instance.client.chat.completions.create(model=self._instance.model, **kwargs)

    def update_model(self, new_model):
        self._instance.model = new_model