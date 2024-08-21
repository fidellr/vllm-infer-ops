# import asyncio
import os
from typing import Optional

from openai import AsyncOpenAI, OpenAI

# from vllm import AsyncEngineArgs, AsyncLLMEngine

# from vllm.entrypoints.openai.serving_engine import LoRAModulePath


class InferenceServe:
    def __init__(
        self,
        # engine_args: AsyncEngineArgs,
        response_role: str,
        base_url: Optional[str] = None,
        api_key: Optional[str] = "sk-xxxx",
        base_model: Optional[str] = "thesven/microsoft_wizardlm-2-7b-gptq",
        openai_serving_client: Optional[OpenAI | AsyncOpenAI] = None,
        chat_template: Optional[str] = None,
    ) -> None:
        self.base_url = os.getenv("OPENAI_BASE_URL") or base_url
        self.api_key = os.getenv("OPENAI_API_KEY") or api_key
        self.base_model = os.getenv("OPENAI_BASE_MODEL") or base_model

        self.openai_serving_chat = openai_serving_client or AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )
        self.response_role = response_role
        self.chat_template = chat_template

    def chat_completions(self):
        # Note: Ray Serve doesn't support all OpenAI client arguments and may ignore some.
        chat_completion = self.openai_serving_chat.chat.completions.create(
            model=self.base_model,
            # messages=messages
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": "What are some highly rated restaurants in San Francisco?'",
                },
            ],
            temperature=0.02,
            stream=True,
        )

        for chat in chat_completion:
            if chat.choices[0].delta.content is not None:
                print(chat.choices[0].delta.content, end="")


if __name__ == "__main__":
    inference_engine = InferenceServe(response_role="assistant")
    inference_engine.chat_completions()
