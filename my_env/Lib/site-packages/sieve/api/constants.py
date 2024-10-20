import os

""" API Constants """
API_URL = os.environ.get("SIEVE_API_URL", "https://mango.sievedata.com")
API_BASE = os.environ.get("SIEVE_API_BASE", "v1")
V2_API_BASE = os.environ.get("SIEVE_V2_API_BASE", "v2")
DASHBOARD_URL = os.environ.get("SIEVE_DASHBOARD_URL", "https://sievedata.com/dashboard")

""" User Info Constants """
USER_API_KEY = "API-Key"
USER_NAME = "name"

""" Model Constants """
MODEL_ID = "model_id"
MODEL_NAME = "model_name"

""" Job Constants """
JOB_ID = "job_id"
JOB_STATUS = "status"
JOB_TIME_STARTED = "time_started"
JOB_TIME_FINISHED = "time_finished"
JOB_TIME_SUBMITTED = "time_submitted"
