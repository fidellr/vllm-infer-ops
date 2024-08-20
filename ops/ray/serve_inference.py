from openai import OpenAI
from typing import List, Optional
from vllm import AsyncEngineArgs, AsyncLLMEngine
from vllm.entrypoints.openai.serving_engine import LoRAModulePath


class InferenceServe:
    def __init__(
        self,
        engine_args: AsyncEngineArgs,
        response_role: str,
        lora_modules: Optional[List[LoRAModulePath]] = None,
        chat_template: Optional[str] = None,
    ) -> None:
        self.openai_serving_chat = None
        self.engine_args = engine_args
        self.response_role = response_role
        self.lora_modules = lora_modules
        self.chat_template = chat_template
        self.engine = AsyncLLMEngine.from_engine_args(engine_args)

    def chat_completions(self, messages):
        # Note: Ray Serve doesn't support all OpenAI client arguments and may ignore some.
        client = OpenAI(
            # Replace the URL if deploying your app remotely
            # (e.g., on Anyscale or KubeRay).
            base_url="http://localhost:8000/v1",
            api_key="NOT A REAL KEY",
        )
        chat_completion = client.chat.completions.create(
            model="NousResearch/Meta-Llama-3-8B-Instruct",
            messages=messages
            or [
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": "What are some highly rated restaurants in San Francisco?'",
                },
            ],
            temperature=0.01,
            stream=True,
        )
        for chat in chat_completion:
            if chat.choices[0].delta.content is not None:
                print(chat.choices[0].delta.content, end="")


if __name__ == "__main__":
    inference_engine = InferenceServe()
