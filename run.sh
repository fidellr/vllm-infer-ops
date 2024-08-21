#!/bin/bash
#!. .venv/bin/activate

BASE_DIR="${PWD}"
USER_ACTION=$1
export OPENAI_BASE_MODEL=$2

if [[ ${USER_ACTION} == "ray_serve" ]]; then
	. .venv/bin/activate &&
		cd "${BASE_DIR}/engines/vllm_based" &&
		$(which serve) run ray_serve:build model="${MODEL_REPO_ID}" tensor-parallel-size=1

	#  Current
	echo "current_dir: ${PWD}"
	cat serve_config.yaml
else
	echo "Error: Non-empty engine user command. Please use 'ray_serve' or any user actions that supported. (current supported: ray_serve)"
	exit 1
fi
