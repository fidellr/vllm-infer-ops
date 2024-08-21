#!/bin/bash
#!. .venv/bin/activate


BASE_DIR="${PWD}"
USER_ACTION=$1
MODEL_REPO_ID=$2



if [[ "$USER_ACTION" = "ray_serve" ]]; then
	. .venv/bin/activate && \
	cd "$BASE_DIR/engines/vllm_based" && \
	ray start --include-dashboard=True --head
	 
	#  Current
	 echo "current_dir: $PWD"
	 cat serve_config.yaml
else
	echo "Error: Non-empty engine user command. Please use 'ray_serve' or any user actions that supported. (current supported: ray_serve)"
	exit 1
fi