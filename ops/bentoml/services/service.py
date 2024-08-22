import uuid
from typing import AsyncGenerator

import bentoml
from annotated_types import Ge, Le
from typing_extensions import Annotated

from services.utils import openai_endpoints

MAX_TOKENS = 8192
PROMPT_TEMPLATE = """<s>[INST]
You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.

{user_prompt} [/INST] """

MODEL_ID = "thesven/microsoft_WizardLM-2-7B-GPTQ"


@openai_endpoints(model_id=MODEL_ID)
@bentoml.service(
    name="wizardlm-2-7b-gptq-service",
    traffic={
        "timeout": 300,
        "concurrency": 256,  # Matches the default max_num_seqs in the VLLM engine
    },
    resources={"gpu": 1, "cpu": 2},
)
class VLLM:
    def __init__(self) -> None:
        from vllm import AsyncEngineArgs, AsyncLLMEngine, EngineArgs
        from vllm.engine.llm_engine import LLMEngine

        ASYN_ENGINE_ARGS = AsyncEngineArgs(
            model=MODEL_ID,
            max_model_len=MAX_TOKENS,
            enable_prefix_caching=True,
            quantization="gptq",
        )
        BASE_ENGINE_ARGS = EngineArgs(
            model=MODEL_ID,
            max_model_len=MAX_TOKENS,
            enable_prefix_caching=True,
            quantization="gptq",
        )

        self.async_engine = AsyncLLMEngine.from_engine_args(ASYN_ENGINE_ARGS)
        self.base_engine = LLMEngine.from_engine_args(BASE_ENGINE_ARGS)

    @bentoml.api
    async def generate(
        self,
        prompt: str = "Explain superconductors like I'm five years old",
        max_tokens: Annotated[int, Ge(128), Le(MAX_TOKENS)] = MAX_TOKENS,
    ) -> AsyncGenerator[str, None]:
        from vllm import SamplingParams

        SAMPLING_PARAM = SamplingParams(max_tokens=max_tokens)
        prompt = PROMPT_TEMPLATE.format(user_prompt=prompt)
        stream = await self.async_engine.add_request(
            uuid.uuid4().hex, prompt, SAMPLING_PARAM
        )

        cursor = 0
        async for request_output in stream:
            text = request_output.outputs[0].text
            yield text[cursor:]
            cursor = len(text)

    @bentoml.api
    async def completions(
        self,
        prompt: str = "Explain superconductors like I'm five years old",
        max_tokens: Annotated[int, Ge(128), Le(MAX_TOKENS)] = MAX_TOKENS,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        from vllm import SamplingParams

        SAMPLING_PARAM = SamplingParams(max_tokens=max_tokens, **kwargs)
        prompt = PROMPT_TEMPLATE.format(user_prompt=prompt)

        # stream = await self.base_engine.add_request(
        #     uuid.uuid4().hex, inputs=[], params=SAMPLING_PARAM
        # )

        # cursor = 0
        # async for request_output in stream:
        #     text = request_output.outputs[0].text
        #     yield text[cursor:]
        #     cursor = len(text)
