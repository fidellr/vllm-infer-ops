# import asyncio
import os
from typing import List, Optional

from openai import OpenAI
from openai.types.chat.chat_completion_message import ChatCompletionMessage

# from vllm import AsyncEngineArgs, AsyncLLMEngine

# from vllm.entrypoints.openai.serving_engine import LoRAModulePath


class InferenceServe:
    def __init__(
        self,
        # engine_args: AsyncEngineArgs,
        response_role: str,
        openai_client: Optional[OpenAI] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = "sk-xxxx",
        base_model: Optional[str] = "thesven/microsoft_wizardlm-2-7b-gptq",
        chat_template: Optional[str] = None,
    ) -> None:
        self.base_url = os.getenv("OPENAI_BASE_URL") or base_url
        self.api_key = os.getenv("OPENAI_API_KEY") or api_key
        self.base_model = os.getenv("OPENAI_BASE_MODEL") or base_model

        self.openai_serving_chat = openai_client or OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )
        self.response_role = response_role
        self.chat_template = chat_template

    def chat_completions(self, messages: Optional[List[ChatCompletionMessage]] = None):
        messages = messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "What are some highly rated restaurants in San Francisco?'",
            },
        ]

        try:
            # Note: Ray Serve doesn't support all OpenAI client arguments and may ignore some.
            chat_completion = self.openai_serving_chat.chat.completions.create(
                model=self.base_model,
                messages=messages,
                temperature=0.02,
                stream=True,
            )

            results = ""
            for chat in chat_completion:
                if chat.choices[0].delta.content is not None:
                    results += " ".join(chat.choices[0].delta.content)
                    print(chat.choices[0].delta.content, end="")
        except Exception as e:
            print(f"ERROR::> {e}")
            raise e


if __name__ == "__main__":
    inference_engine = InferenceServe(response_role="assistant")
    inference_engine.chat_completions()
