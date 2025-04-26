import os
from together import Together


class LLMClient:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = 'tgp_v1_cKEclmBXjEfh_0p359F19ac6fUzUCPYKWzyakaZAALk'
        self.client = Together(
            api_key=self.api_key
        )
        self.model = model or "meta-llama/Llama-3.3-70B-Instruct-Turbo"

    def query(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"
