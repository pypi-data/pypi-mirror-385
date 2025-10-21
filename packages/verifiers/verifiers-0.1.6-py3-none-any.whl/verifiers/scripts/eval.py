import argparse
import asyncio
import json
import logging
from typing import Dict

from verifiers import setup_logging
from verifiers.types import ClientConfig, EvalConfig
from verifiers.utils.eval_utils import load_endpoints, run_evaluation

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "env_id", type=str, default="gsm8k", help="Environment module name"
    )
    parser.add_argument(
        "--env-args",
        "-a",
        type=json.loads,
        default={},
        help='Environment module arguments as JSON object (e.g., \'{"key": "value", "num": 42}\')',
    )
    parser.add_argument(
        "--env-dir-path",
        "-p",
        type=str,
        default="./environments",
        help="Path to environments directory",
    )
    parser.add_argument(
        "--endpoints-path",
        "-e",
        type=str,
        default="./configs/endpoints.py",
        help="Path to API endpoints registry",
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default="gpt-4.1-mini",
        help="Name of model to evaluate",
    )
    parser.add_argument(
        "--api-key-var",
        "-k",
        type=str,
        default="OPENAI_API_KEY",
        help="Environment variable name for API key",
    )
    parser.add_argument(
        "--api-base-url",
        "-b",
        type=str,
        default="https://api.openai.com/v1",
        help="Base URL for API",
    )
    parser.add_argument(
        "--header",
        action="append",
        default=None,
        help="Extra HTTP header to pass to inference API. 'Name: Value'. Repeatable.",
    )
    parser.add_argument(
        "--num-examples",
        "-n",
        type=int,
        default=5,
        help="Number of examples to evaluate",
    )
    parser.add_argument(
        "--rollouts-per-example",
        "-r",
        type=int,
        default=3,
        help="Number of rollouts per example",
    )
    parser.add_argument(
        "--max-concurrent",
        "-c",
        type=int,
        default=32,
        help="Maximum number of concurrent requests",
    )
    parser.add_argument(
        "--max-concurrent-generation",
        type=int,
        default=None,
        help="Maximum number of concurrent generation requests",
    )
    parser.add_argument(
        "--max-concurrent-scoring",
        type=int,
        default=None,
        help="Maximum number of concurrent scoring requests",
    )
    parser.add_argument(
        "--max-tokens",
        "-t",
        type=int,
        default=None,
        help="Maximum number of tokens to generate (unset to use model default)",
    )
    parser.add_argument(
        "--temperature", "-T", type=float, default=None, help="Temperature for sampling"
    )
    parser.add_argument(
        "--sampling-args",
        "-S",
        type=json.loads,
        default=None,
        help=(
            "Sampling arguments as JSON object. Keys here override --max-tokens/--temperature. "
            'Example: \'{"enable_thinking": false, "max_tokens": 256}\''
        ),
    )
    parser.add_argument(
        "--verbose", "-v", default=False, action="store_true", help="Verbose output"
    )
    parser.add_argument(
        "--no-interleave-scoring",
        "-N",
        default=False,
        action="store_true",
        help="Disable interleaving of scoring",
    )
    parser.add_argument(
        "--state-columns",
        "-C",
        type=list[str],
        default=[],
        help="List of state columns to save",
    )
    parser.add_argument(
        "--save-results",
        "-s",
        default=False,
        action="store_true",
        help="Save results to disk",
    )
    # save every n rollouts
    parser.add_argument(
        "--save-every",
        "-f",
        type=int,
        default=-1,
        help="Save dataset every n rollouts",
    )
    parser.add_argument(
        "--save-to-hf-hub",
        "-H",
        default=False,
        action="store_true",
        help="Save dataset to Hugging Face Hub",
    )
    parser.add_argument(
        "--hf-hub-dataset-name",
        "-D",
        type=str,
        default="",
        help="Name of dataset to save to Hugging Face Hub",
    )
    args = parser.parse_args()

    setup_logging("DEBUG" if args.verbose else "INFO")

    # load endpoints and get model config
    endpoints = load_endpoints(args.endpoints_path)
    if args.model in endpoints:
        api_key_var = endpoints[args.model]["key"]
        api_base_url = endpoints[args.model]["url"]
        args.model = endpoints[args.model]["model"]
        logger.debug(
            f"Using endpoint configuration for model '{args.model}' from registry"
        )
    else:
        logger.debug(
            f"Model '{args.model}' not found in endpoint registry, using command-line arguments"
        )
        api_key_var = args.api_key_var
        api_base_url = args.api_base_url

    # merge sampling args with precedence to JSON payload over explicit flags
    merged_sampling_args: dict = {}
    if args.sampling_args is not None:
        merged_sampling_args.update(args.sampling_args)
    if "max_tokens" not in merged_sampling_args:
        merged_sampling_args["max_tokens"] = args.max_tokens
    if args.temperature is not None and "temperature" not in merged_sampling_args:
        merged_sampling_args["temperature"] = args.temperature

    # Build headers from repeated --header flags
    merged_headers: Dict[str, str] = {}
    for h in args.header or []:
        if ":" not in h:
            raise ValueError(f"--header must be 'Name: Value', got: {h!r}")
        k, v = h.split(":", 1)
        k, v = k.strip(), v.strip()
        if not k:
            raise ValueError("--header name cannot be empty")
        merged_headers[k] = v

    client_config = ClientConfig(
        api_key_var=api_key_var,
        api_base_url=api_base_url,
        extra_headers=merged_headers,
    )

    # run evaluation
    eval_config = EvalConfig(
        # environment
        env_id=args.env_id,
        env_args=args.env_args,
        env_dir_path=args.env_dir_path,
        # evaluation
        model=args.model,
        client_config=client_config,
        sampling_args=merged_sampling_args,
        num_examples=args.num_examples,
        rollouts_per_example=args.rollouts_per_example,
        max_concurrent=args.max_concurrent,
        max_concurrent_generation=args.max_concurrent_generation,
        max_concurrent_scoring=args.max_concurrent_scoring,
        interleave_scoring=not args.no_interleave_scoring,
        # logging
        print_results=True,
        verbose=args.verbose,
        # saving
        state_columns=args.state_columns,
        save_results=args.save_results,
        save_every=args.save_every,
        save_to_hf_hub=args.save_to_hf_hub,
        hf_hub_dataset_name=args.hf_hub_dataset_name,
    )
    logger.debug(f"Evaluation config: {eval_config.model_dump_json(indent=2)}")
    asyncio.run(run_evaluation(eval_config))


if __name__ == "__main__":
    main()
