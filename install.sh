#!/bin/bash

# Define the path to the base directory containing the requirements files
BASE_DIR="${PWD}"
VLLM_VERSION=0.5.4

# Determine which requirements file to use based on the user command
MLOPS=$1
BASE_ENGINE=$2
MODEL_REPO_ID=$3

python3 -m venv .venv
source .venv/bin/activate

if [[ ${MLOPS} == "ray" ]]; then
	REQUIREMENTS_FILE="${BASE_DIR}/ops/${MLOPS}/requirements-${MLOPS}.txt"
elif [[ ${MLOPS} == "bentoml" ]]; then
	REQUIREMENTS_FILE="${BASE_DIR}/ops/${MLOPS}/requirements-${MLOPS}.txt"
fi

if [[ ${BASE_ENGINE} == "vllm" ]]; then
	ENGINE_REQUIREMENTS_FILE="${BASE_DIR}/engines/vllm_based/requirements-vllm.txt"
	echo "vllm --index-url https://vllm-wheels.s3.us-west-2.amazonaws.com/nightly/vllm-${VLLM_VERSION}-cp38-abi3-manylinux1_x86_64.whl" >>"${ENGINE_REQUIREMENTS_FILE}"

else
	echo "Error: Non-empty engine user command. Please use 'vllm' or '..' that supported."
	exit 1
fi

python3 -m pip install -r "${ENGINE_REQUIREMENTS_FILE}"
python3 -m pip install -r "${REQUIREMENTS_FILE}"

export BUILD_CLI_ARGS='{"model": "'${MODEL_REPO_ID}'", "tensor-parallel-size": "1"}'
# cd "${BASE_DIR}/engines/vllm_based" && \
# BUILD_CLI_ARGS=${BUILD_CLI_ARGS} serve build "${MLOPS}"_serve:app -o serve_config.yaml
# echo "current_dir: ${PWD}"
