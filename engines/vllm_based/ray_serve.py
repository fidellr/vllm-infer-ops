import logging
from typing import Dict, List, Optional

import ray
from fastapi import FastAPI
from ray import serve
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.entrypoints.openai.protocol import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ErrorResponse,
)
from vllm.entrypoints.openai.serving_chat import OpenAIServingChat
from vllm.entrypoints.openai.serving_engine import LoRAModulePath

from engines.vllm_based.utils import get_cli_args, parse_vllm_args

# from engines.vllm_based.utils import get_cli_args, parse_vllm_args


logger = logging.getLogger("ray.serve")

app = FastAPI()


@serve.deployment(
    autoscaling_config={
        "min_replicas": 1,
        "max_replicas": 2,
        "target_ongoing_requests": 3,
    },
    max_ongoing_requests=3,
)
@serve.ingress(app)
class VLLMDeployment:
    def __init__(
        self,
        engine_args: AsyncEngineArgs,
        response_role: Optional[str] = "assistant",
        lora_modules: Optional[List[LoRAModulePath]] = None,
        chat_template: Optional[str] = None,
    ):
        logger.info(f"Starting with engine args: {engine_args}")
        self.openai_serving = None
        self.engine_args = engine_args
        self.response_role = response_role
        self.lora_modules = lora_modules
        self.chat_template = chat_template
        self.engine = AsyncLLMEngine.from_engine_args(engine_args)

    @app.post("/v1/chat/completions")
    async def create_chat_completion(
        self, request: ChatCompletionRequest, raw_request: Request
    ):
        """OpenAI-compatible HTTP endpoint.

        API reference:
            - https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html
        """
        if not self.openai_serving:
            model_config = self.engine.get_model_config()
            # Determine the name of the served model for the OpenAI client.
            if self.engine_args.served_model_name is not None:
                served_model_names = self.engine_args.served_model_name
            else:
                served_model_names = [self.engine_args.model]
            self.openai_serving = OpenAIServingChat(
                self.engine,
                model_config,
                served_model_names,
                self.response_role,
                self.lora_modules,
                self.chat_template,
            )

        logger.info(f"Request: {request}")
        generator = await self.openai_serving.create_chat_completion(
            request,
            raw_request,
        )

        if isinstance(generator, ErrorResponse):
            return JSONResponse(
                content=generator.model_dump(), status_code=generator.code
            )
        if request.stream:
            return StreamingResponse(content=generator, media_type="text/event-stream")
        else:
            # trunk-ignore(bandit/B101)
            assert isinstance(generator, ChatCompletionResponse)
            return JSONResponse(content=generator.model_dump())

    @app.get("/v1/models")
    async def get_model_list(self):
        """OpenAI-compatible HTTP endpoint.

        API reference:
            - https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html
        """
        if not self.openai_serving:
            model_config = self.engine.get_model_config()
            # Determine the name of the served model for the OpenAI client.
            if self.engine_args.served_model_name is not None:
                served_model_names = self.engine_args.served_model_name
            else:
                served_model_names = [self.engine_args.model]
            self.openai_serving = OpenAIServingChat(
                self.engine,
                model_config,
                served_model_names,
                self.response_role,
                self.lora_modules,
                self.chat_template,
            )

        # logger.info(f"Request:")
        generator = await self.openai_serving.show_available_models()
        if isinstance(generator, ErrorResponse):
            return JSONResponse(
                content=generator.model_dump(), status_code=generator.code
            )

        return generator


def build_app(args: Dict[str, str]):
    """Builds the Serve app based on CLI arguments.

    See https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html#command-line-arguments-for-the-server
    for the complete set of arguments.

    Supported engine arguments: https://docs.vllm.ai/en/latest/models/engine_args.html.
    """  # noqa: E501
    print("ARGSL:::>", args)
    # engine_args.engine_use_ray = True
    engine_args.worker_use_ray = True
    engine_args.enforce_eager = True

    tp = engine_args.tensor_parallel_size
    logger.info(f"Tensor parallelism = {tp}")
    pg_resources = []
    pg_resources.append({"CPU": 1})  # for the deployment replica
    for i in range(tp):
        pg_resources.append({"CPU": 1, "GPU": 1})  # for the vLLM actors
        print(f"ITER: {i}\n")

    # We use the "STRICT_PACK" strategy below to ensure all vLLM actors are placed on
    # the same Ray node.
    return VLLMDeployment.options(
        placement_group_bundles=pg_resources, placement_group_strategy="STRICT_PACK"
    ).bind(
        engine_args,
        parsed_args.response_role,
        parsed_args.lora_modules,
        parsed_args.chat_template,
    )


# if __name__ == "__main__":
cli_args = get_cli_args()
print("CLI_ARGS::>", cli_args)
parsed_args = parse_vllm_args(cli_args)
engine_args = AsyncEngineArgs.from_cli_args(parsed_args)
# engine_args.engine_use_ray = True
engine_args.worker_use_ray = True
engine_args.enforce_eager = True

app = build_app()
ctx = ray.init()
print(ctx)
print(ctx.dashboard_url)

# build_cli_args = os.getenv("BUILD_CLI_ARGS")
# build_cli_args: Optional[EngineArgs] = json.loads(build_cli_args)
# print("BUILD_CLIARGS:::>", build_cli_args, sep="\n")
# build_cli_args = json.loads(build_cli_args)
# print("BUILD_CLIARGS:::>", json.dumps(build_cli_args, indent=2), sep="\n")
# app = VLLMDeployment.bind(build_app(cli_args=build_cli_args))
