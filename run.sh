#!/bin/bash
BASE_DIR="${PWD}"
USER_ACTION=$1
MODEL_REPO_ID=$2

if [[ ${USER_ACTION} == "ray_serve" ]]; then
	cd "${BASE_DIR}/engines/vllm_based" &&
		$(command -v serve) run ray_serve:app model="${MODEL_REPO_ID}" tensor-parallel-size=1

	#  Current
	echo "current_dir: ${PWD}"
else
	echo "Error: Non-empty engine user command. Please use 'ray_serve' or any user actions that supported. (current supported: ray_serve)"
	exit 1
fi
