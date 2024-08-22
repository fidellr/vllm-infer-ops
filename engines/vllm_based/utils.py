from typing import Dict

from vllm.entrypoints.openai.cli_args import make_arg_parser
from vllm.utils import FlexibleArgumentParser

arg_parser = FlexibleArgumentParser(
    description="vLLM OpenAI-Compatible RESTful API server."
)
parser = make_arg_parser(arg_parser)


def parse_vllm_args(cli_args: Dict[str, str]):
    """Parses vLLM args based on CLI inputs.

    Currently uses argparse because vLLM doesn't expose Python models for all of the
    config options we want to support.
    """

    arg_strings = []
    for key, value in cli_args.items():
        arg_strings.extend([f"--{key}", str(value)])
    # logger.info(arg_strings)
    parsed_args = parser.parse_args(args=arg_strings)
    return parsed_args


def get_cli_args():

    # parser.add_argument(
    #     "--model", action="store_true", help="Model Repo ID"
    # )
    # parser.add_argument(
    #     "--worker-use-ray", action="store_true", help="Use Ray for worker processes"
    # )
    # parser.add_argument(
    #     "--enforce-eager", action="store_true", help="Enforce eager execution"
    # )
    # Add other arguments as needed based on your VLLM and AsyncEngineArgs requirements

    return parser
