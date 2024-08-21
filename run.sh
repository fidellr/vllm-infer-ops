#!/usr/bin/bash

# Define the path to the base directory containing the requirements files
BASE_DIR="${PWD}"
VLLM_VERSION=0.5.4

# Determine which requirements file to use based on the user command
MLOPS=$1
BASE_ENGINE=$2

if [ "$MLOPS" = "bentoml" ] || [ "$MLOPS" = "ray" ]; then
	REQUIREMENTS_FILE="${BASE_DIR}/ops/${MLOPS}/requirements-${MLOPS}.txt"
else
	echo "Error: Invalid user command. Please use 'bentoml' or 'ray'."
	exit 1
fi

if [[ ${BASE_ENGINE} == "vllm" ]]; then
	ENGINE_REQUIREMENTS_FILE="${BASE_DIR}/engines/vllm_based/requirements-vllm.txt"
	echo "vllm --index-url https://vllm-wheels.s3.us-west-2.amazonaws.com/nightly/vllm-${VLLM_VERSION}-cp38-abi3-manylinux1_x86_64.whl" >"${ENGINE_REQUIREMENTS_FILE}"

else
	echo "Error: Non-empty engine user command. Please use 'vllm' or '..' that supported."
	exit 1
fi

pip install -r "${ENGINE_REQUIREMENTS_FILE}"
pip install -r "${REQUIREMENTS_FILE}" --force-reinstall
