#!/bin/bash

BASE_DIR="${PWD}"
USER_ACTION=$1
MODEL_REPO_ID=$2
BUILD_CLI_ARGS='{"model": "'$MODEL_REPO_ID'", "tensor-parallel-size": "1"}'

if [[ ${USER_ACTION} == "ray_serve" ]]; then
	ray start --include-dashboard True --head
	# ray job submit --working-dir . -- \
	# 	BUILD_CLI_ARGS=$BUILD_CLI_ARGS serve run engines.vllm_based.ray_serve:app model="$MODEL_REPO_ID" tensor-parallel-size=1
	BUILD_CLI_ARGS="'$BUILD_CLI_ARGS'" serve deploy serve_config.yaml

	#  Current
	echo "current_dir: ${PWD}"
else
	echo "Error: Non-empty engine user command. Please use 'ray_serve' or any user actions that supported. (current supported: ray_serve)"
	exit 1
fi
