#!/usr/bin/bash

# Define the path to the base directory containing the requirements files
BASE_DIR="${PWD}"

# Determine which requirements file to use based on the user command
USER_COMMAND=$1
BASE_ENGINE=$2

if [ "$BASE_ENGINE" = "vllm" ]; then
	ENGINE_REQUIREMENTS_FILE="${BASE_DIR}/engines/vllm_based/requirements-vllm.txt"
else
	echo "Error: Non-empty engine user command. Please use 'vllm' or '..' that supported."
	exit 1
fi

if [ "$USER_COMMAND" = "bentoml" ]; then
	REQUIREMENTS_FILE="${BASE_DIR}/ops/bentoml/requirements-bentoml.txt"
elif [ "$USER_COMMAND" = "ray" ]; then
	REQUIREMENTS_FILE="${BASE_DIR}/ops/ray/requirements-ray.txt"
else
	echo "Error: Invalid user command. Please use 'bentoml' or 'ray'."
	exit 1
fi

pip install -r "${ENGINE_REQUIREMENTS_FILE}" -v
pip install -r "${REQUIREMENTS_FILE}" -v
