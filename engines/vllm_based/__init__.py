# from ray.job_submission import JobSubmissionClient

# # If using a remote cluster, replace 127.0.0.1 with the head node's IP address or set up port forwarding.
# client = JobSubmissionClient("http://0.0.0.0:8265")
# job_id = client.submit_job(
#     # Entrypoint shell command to execute
#     entrypoint="python script.py",
#     # Path to the local directory that contains the script.py file
#     runtime_env={"working_dir": "./"}
# )
# print(job_id)