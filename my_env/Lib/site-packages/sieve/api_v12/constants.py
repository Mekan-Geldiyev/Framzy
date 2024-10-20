import os

# API Constants
API_URL = os.environ.get('SIEVE_API_URL', 'https://mango.sievedata.com')
API_BASE = os.environ.get('SIEVE_API_BASE', 'v1')
DASHBOARD_URL = os.environ.get('SIEVE_DASHBOARD_URL', 'https://sievedata.com/app')

# User Info Constants
USER_API_KEY = 'API-Key'
USER_NAME = 'name'

# Project Constants
PROJECT_NAME = 'project_name'
PROJECT_LAYERS = 'layers'
PROJECT_USER = 'customer_name'
PROJECT_STORE_DATA = 'store_data'
PROJECT_FPS = 'fps'
PROJECT_LAYER_ITERATION_TYPE = 'iteration'
PROJECT_LAYER_MODELS = 'models'
PROJECT_CREATE_CONFIG = 'config'


# Model Constants
MODEL_ID = 'model_id'
MODEL_NAME = 'model_name'

# Job Constants
JOB_ID = 'job_id'
JOB_SOURCE_NAME = 'source_name'
JOB_SOURCE_TYPE = 'source_type'
JOB_SOURCE_URL = 'source_url'
JOB_STATUS = 'status'
JOB_TIME_STARTED = 'time_started'
JOB_TIME_FINISHED = 'time_finished'
JOB_TIME_SUBMITTED = 'time_submitted'