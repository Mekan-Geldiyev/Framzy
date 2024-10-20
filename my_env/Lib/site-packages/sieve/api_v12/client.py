from __future__ import annotations

import os
import requests
import json
from typing import List, Optional

from typing import Dict, List

from ..types.api import SieveLayer, SieveWorkflow
from ..api.constants import API_URL, API_BASE, JOB_ID, JOB_SOURCE_NAME, JOB_SOURCE_TYPE, JOB_SOURCE_URL, JOB_STATUS, JOB_TIME_FINISHED, JOB_TIME_STARTED, JOB_TIME_SUBMITTED, PROJECT_CREATE_CONFIG, PROJECT_NAME, PROJECT_LAYERS, PROJECT_STORE_DATA, PROJECT_FPS, USER_API_KEY, USER_NAME
from ..api.utils import get as sieve_get
from ..api.utils import post as sieve_post
from ..api.utils import delete as sieve_delete


class SieveJob():
    """
    Class for a job within Sieve
    """
    @classmethod
    def from_json(cls, job_json) -> SieveJob:
        """
        Create a SieveJob from a json object

        Args:
            job_json (dict): The json object to create the job from

        Returns:
            SieveJob: The created job
        """
        if JOB_TIME_SUBMITTED not in job_json:
            job_json[JOB_TIME_SUBMITTED] = None
        if JOB_TIME_STARTED not in job_json:
            job_json[JOB_TIME_STARTED] = None
        if JOB_TIME_FINISHED not in job_json:
            job_json[JOB_TIME_FINISHED] = None
        return SieveJob(
            id=job_json[JOB_ID],
            status=job_json[JOB_STATUS],
            source_name=job_json[JOB_SOURCE_NAME],
            source_type=job_json[JOB_SOURCE_TYPE],
            time_submitted=job_json[JOB_TIME_SUBMITTED],
            time_started=job_json[JOB_TIME_STARTED],
            time_finished=job_json[JOB_TIME_FINISHED],
            project_name=job_json[PROJECT_NAME],
        )

    @classmethod
    def from_project_and_id(cls, project_name: str, job_id: str) -> SieveJob:
        """
        Get a job from a project and job id

        Args:
            project_name (str): The name of the project
            job_id (str): The id of the job

        Returns:
            SieveJob: The job
        """
        job_json = sieve_get(
            f"{API_URL}/{API_BASE}/projects/{project_name}/jobs/{job_id}"
        )
        if job_json.status_code != 200:
            raise Exception(
                f"Error getting job {job_id} from project {project_name}")

        out = job_json.json()
        out[PROJECT_NAME] = project_name
        return SieveJob.from_json(out)

    def __init__(
        self,
        project_name: str,
        id: str,
        status: str,
        source_name: str,
        source_type: str,
        time_submitted: Optional[str],
        time_started: Optional[str],
        time_finished: Optional[str],
    ) -> None:
        self.id = id
        self.status = status
        self.source_name = source_name
        self.source_type = source_type
        self.time_submitted = time_submitted
        self.time_started = time_started
        self.time_finished = time_finished
        self.project_name = project_name

    def poll(self):
        """
        Polls the job and updates class variables
        """
        job_json = sieve_get(
            f"{API_URL}/{API_BASE}/projects/{self.project_name}/jobs/{self.id}"
        )
        self.status = job_json[JOB_STATUS]
        if JOB_TIME_SUBMITTED in job_json:
            self.time_submitted = job_json[JOB_TIME_SUBMITTED]
        if JOB_TIME_STARTED in job_json:
            self.time_started = job_json[JOB_TIME_STARTED]
        if JOB_TIME_FINISHED in job_json:
            self.time_finished = job_json[JOB_TIME_FINISHED]
        return self.status

    @property
    def dict(self) -> Dict:
        out = {
            JOB_ID: self.id,
            JOB_STATUS: self.status,
            JOB_SOURCE_NAME: self.source_name,
            JOB_SOURCE_TYPE: self.source_type,
            JOB_TIME_SUBMITTED: self.time_submitted,
            JOB_TIME_STARTED: self.time_started,
            JOB_TIME_FINISHED: self.time_finished,
        }
        return {k: v for k, v in out.items() if v is not None}

    def __str__(self) -> str:
        return f'SieveJob(id={self.id}, status={self.status})'

    def __repr__(self) -> str:
        return self.__str__()


class SieveProject():
    """
    Class for a Sieve project
    """
    @classmethod
    def from_name(self, name: str, load_project_info=True) -> SieveProject:
        """
        Create a SieveProject object from a project name

        Args:
            name: the name of the project

        Returns:
            a SieveProject object
        """
        project = SieveProject(name, None, None, None)
        if load_project_info:
            project._get_from_api(name)
        return project

    @classmethod
    def from_json(cls, project_json) -> SieveProject:
        """
        Create a SieveProject object from a JSON object

        Args:
            project_json: a JSON object representing a Sieve project

        Returns:
            a SieveProject object
        """
        return SieveProject(
            name=project_json[PROJECT_NAME],
            workflow=SieveWorkflow([SieveLayer.from_json(layer_json)
                                   for layer_json in project_json[PROJECT_LAYERS]]),
            fps=project_json[PROJECT_FPS],
            store_data=project_json[PROJECT_STORE_DATA]
        )

    def __init__(
        self,
        name: str,
        workflow: SieveWorkflow,
        fps: int,
        store_data: bool
    ) -> None:
        self.name = name
        self.workflow = workflow
        self.fps = fps
        self.store_data = store_data
        self.created = False

    def _update_attributes_from_json(self, project_json):
        """
        Update the attributes of the SieveProject object from a JSON object

        Args:
            project_json: a JSON object representing a Sieve project

        Returns:
            None
        """
        self.name = project_json[PROJECT_NAME]
        self.workflow = SieveWorkflow([SieveLayer.from_json(
            layer_json) for layer_json in project_json[PROJECT_LAYERS]])
        self.store_data = project_json[PROJECT_STORE_DATA]
        self.fps = project_json[PROJECT_FPS]
        self.created = True

    def _get_from_api(self, name):
        """
        Get the project from the API

        Args:
            name: the name of the project

        Returns:
            None
        """
        res = sieve_get(f'{API_URL}/{API_BASE}/projects/{name}')
        if res.status_code == 200:
            res_json = res.json()
            self._update_attributes_from_json(res_json)
        else:
            try:
                res_json = res.json()
            except:
                raise Exception(f'Error: {res.status_code} {res.text}')
            raise Exception(res_json['description'])

    def create(self):
        """
        Create the project on the API

        Args:
            None

        Returns:
            None
        """
        res = sieve_post(
            f'{API_URL}/{API_BASE}/projects',
            data={
                PROJECT_CREATE_CONFIG: self.dict,
                PROJECT_NAME: self.name
            }
        )
        if res.status_code == 200:
            res_json = res.json()
            project_json = res_json
            self._update_attributes_from_json(project_json)
        else:
            try:
                res_json = res.json()
            except:
                raise Exception(f'Error: {res.status_code} {res.text}')
            raise Exception(res_json['description'])

    def delete(self):
        """
        Delete the project from the API

        Args:
            None

        Returns:
            None
        """
        res = sieve_delete(f'{API_URL}/{API_BASE}/projects/{self.name}')
        if res.status_code == 200:
            self.created = False
        else:
            try:
                res_json = res.json()
            except:
                raise Exception(f'Error: {res.status_code} {res.text}')
            raise Exception(res_json['description'])

    def list_jobs(
        self,
        offset: int = 0,
        limit: int = 10000,
    ) -> List[SieveJob]:
        """
        List the jobs in the project

        Args:
            None

        Returns:
            a list of SieveJob objects
        """
        res = sieve_get(
            f'{API_URL}/{API_BASE}/projects/{self.name}/jobs?offset={offset}&limit={limit}',
        )
        if res.status_code == 200:
            res_json = res.json()
            out = []
            for job_json in res_json['data']:
                job_json[PROJECT_NAME] = self.name
                out.append(SieveJob.from_json(job_json))
            return out
        else:
            try:
                res_json = res.json()
            except:
                raise Exception(f'Error: {res.status_code} {res.text}')
            raise Exception(res_json['description'])

    def get_job(self, job_id: str) -> SieveJob:
        return SieveJob.from_project_and_id(self.name, job_id)

    def get_job_status(self, job_id: str) -> str:
        return self.get_job(job_id).status

    def push(self, source_name: str, source_url: str, local_upload=False):
        """
        Push a source to the project

        Args:
            source_name: the name of the source
            source_url: the url of the source
            local_upload: whether to upload the source from the local machine

        Returns:
            job_id: the id of the job
        """
        if local_upload:
            res = sieve_post(
                f'{API_URL}/{API_BASE}/create_local_upload_url',
                data={
                    "file_name": source_name,
                }
            )
            if res.status_code == 200:
                res_json = res.json()
                upload_url = res_json['upload_url']
                with open(source_url, 'rb') as f:
                    put_res = requests.put(
                        upload_url,
                        data=f,
                        headers={
                            'x-goog-content-length-range': '0,1000000000',
                        }
                    )
                if put_res.status_code == 200:
                    source_url = res_json['get_url']
                else:
                    try:
                        res_json = put_res.json()
                    except:
                        raise Exception(f'Error: {put_res.status_code}')
                    raise Exception(res_json['description'])
            else:
                try:
                    res_json = res.json()
                except:
                    raise Exception(f'Error: {res.status_code}')
                raise Exception(res_json['description'])

        res = sieve_post(
            f'{API_URL}/{API_BASE}/push',
            data={
                JOB_SOURCE_NAME: source_name,
                JOB_SOURCE_URL: source_url,
                PROJECT_NAME: self.name,
            }
        )
        if res.status_code == 200:
            res_json = res.json()
            return res_json['job_id']
        else:
            try:
                res_json = res.json()
            except:
                raise Exception(f'Error: {res.status_code} {res.text}')
            raise Exception(res_json['description'])

    @property
    def dict(self) -> Dict:
        """
        Get the project as a dictionary

        Args:
            None

        Returns:
            a dictionary representing the project
        """
        return {
            PROJECT_NAME: self.name,
            PROJECT_LAYERS: [layer.dict for layer in self.workflow.layers],
            PROJECT_STORE_DATA: self.store_data,
            PROJECT_FPS: self.fps
        }

    def __str__(self) -> str:
        return f'SieveProject(name={self.name}, fps={self.fps}, store_data={self.store_data})'

    def __repr__(self) -> str:
        return self.__str__()


class SieveClient():
    """
    Class for Sieve account information

    Fields:
        name:
            the system-given name for the user
        api_key:
            The user's API key
    """

    def _get_from_api(self):
        """
        Get the user from the API

        Args:
            None

        Returns:
            None
        """
        res = sieve_get(f'{API_URL}/{API_BASE}/user')
        if res.status_code == 200:
            res_json = res.json()
            slug = res_json[USER_NAME]
            api_key = res_json[USER_API_KEY]
            self._name = slug
            self.api_key = api_key
        else:
            try:
                res_json = res.json()
                raise Exception(res_json['description'])
            except:
                raise Exception(f'Error: {res.status_code} {res.text}')

    def __init__(self) -> None:
        """
        Create a SieveClient object

        Args:
            None

        Returns:
            None
        """
        key = os.environ.get('SIEVE_API_KEY', None)
        if key is None:
            raise Exception(
                'SIEVE_API_KEY not set. Please set the environment variable SIEVE_API_KEY to your API key.')
        self.api_key = key

    def list_projects(self) -> List[SieveProject]:
        """
        List all projects inside the user's account

        Returns:
            A list of projects
        """
        res = sieve_get(f'{API_URL}/{API_BASE}/projects')
        if res.status_code == 200:
            res_json = res.json()
            return [SieveProject.from_json(project_json) for project_json in res_json['data']]
        else:
            try:
                res_json = res.json()
                raise Exception(res_json['description'])
            except:
                raise Exception(f'Error: {res.status_code} {res.text}')

    def create_project(self, project: SieveProject) -> SieveProject:
        """
        Create a new project inside the user's account

        Args:
            project:
                The project to be created

        Returns:
            The created project
        """
        project.create()
        return project

    def get_project(self, name: str) -> SieveProject:
        """
        Get a project from the user's account

        Args:
            name:
                The name of the project to be retrieved

        Returns:
            The retrieved project
        """
        return SieveProject.from_name(name)

    def delete_project(self, name: str) -> None:
        """
        Delete a project from the user's account

        Args:
            name:
                The name of the project to be deleted
        """
        return SieveProject.from_name(name, load_project_info=False).delete()

    def list_jobs(
        self,
        project_name: str,
        offset: int = 0,
        limit: int = 10000,
    ) -> List[SieveJob]:
        """
        List the jobs in the project

        Args:
            project_name:
                The name of the project to list jobs from

        Returns:
            a list of SieveJob objects
        """
        return SieveProject.from_name(project_name, load_project_info=False).list_jobs(offset=offset, limit=limit)

    def get_job(self, project_name: str, job_id: str) -> SieveJob:
        """
        Get a job from the project

        Args:
            project_name:
                The name of the project to get the job from
            job_id:
                The ID of the job to get

        Returns:
            a SieveJob object       
        """
        return SieveJob.from_project_and_id(project_name, job_id)

    def push(
        self,
        project_name: str,
        source_name: str,
        source_url: str,
        local_upload: bool = False,
    ) -> SieveJob:
        """
        Push a job to the project

        Args:
            project_name:
                The name of the project to push the job to
            source_name:
                The name of the source
            source_url:
                The URL of the source
            upload:
                Whether to upload the source to Sieve's servers

        Returns:
            a SieveJob object
        """
        return SieveProject.from_name(project_name, load_project_info=False).push(source_name, source_url, local_upload=local_upload)

    def search_feedback(
        self,
        query: dict,
        limit: int,
        offset: int,
        paginate: bool,
    ):
        query = json.loads(query)

        if paginate:
            out = self._paginate(
                f'{API_URL}/{API_BASE}/feedback/search', query, limit=limit)
            return out

        print(
            f'{API_URL}/{API_BASE}/feedback/search?offset={offset}&limit={limit}',
            query
        )
        res = sieve_post(
            f'{API_URL}/{API_BASE}/feedback/search?offset={offset}&limit={limit}',
            data=query
        )

        try:
            res_json = res.json()
        except:
            print("Failed while getting json from response.")
            return

        if 200 <= res.status_code < 300:
            out = []
            for result in res_json['data']:
                out.append(result)
            return out
        if 400 <= res.status_code < 500:
            print("There was an issue processing your request: " +
                  res.json()['description'])
            return
        if 500 <= res.status_code:
            print(
                "There was an internal error while processing your request: " + res.json()['description'])
            return

    def _paginate(self, url: str, data: dict, limit: int = 1000):
        offset = 0
        out = []

        res = sieve_post(
            f'{url}?offset={offset}&limit={limit}',
            data=data
        )
        res_json = res.json()
        out.extend(res_json['data'])

        while 200 <= res.status_code <= 300 and len(res.json()['data']) > 0:
            offset += limit
            res = sieve_post(
                f'{url}?offset={offset}&limit={limit}',
                data=data
            )
            res_json = res.json()
            if len(res_json['data']) > 0:
                out.extend(res_json['data'])

        if 400 <= res.status_code < 500:
            print(
                f'There was an issue processing your request. " + {res.text} + " returning data fetched succesfully until offset {offset - limit}')
            return out
        if 500 <= res.status_code:
            print(
                f'There was an internal error while processing your request. " + res.text + " returning data fetched succesfully until offset {offset - limit}')
            return out

        return out

    def query_intervals(self, query: Dict, limit: int = 7500, offset: int = 0, paginate: bool = False):
        return self.query("intervals", query, limit, offset, paginate)

    def query_metadata(self, query: Dict, limit: int = 7500, offset: int = 0, paginate: bool = False):
        return self.query("metadata", query, limit, offset, paginate)

    def query_jobs(self, query: Dict, limit: int = 7500, offset: int = 0, paginate: bool = False):
        return self.query("jobs", query, limit, offset, paginate)

    def query(self, target: str, query: Dict, limit: int = 7500, offset: int = 0, paginate: bool = False):
        query = json.loads(query)

        if paginate and target in ['metadata', 'jobs']:
            out = self._paginate(
                f'{API_URL}/{API_BASE}/query/{target}', query, limit=limit)
            return out
        elif paginate and target not in ['metadata', 'jobs']:
            print(
                f'pagination not supported for {target}, continuing with offset {offset} and limmit {limit}')

        res = sieve_post(
            f'{API_URL}/{API_BASE}/query/{target}?offset={offset}&limit={limit}',
            data=query
        )

        try:
            res_json = res.json()
        except:
            print("Failed while getting json from response.")
            return

        if 200 <= res.status_code < 300:
            if target == 'intervals':
                key = 'intervals'
            if target in ['metadata', 'jobs']:
                key = 'data'
            out = []
            for result in res_json[key]:
                out.append(result)
            return out
        if 400 <= res.status_code < 500:
            print("There was an issue processing your request: " +
                  res.json()['description'])
            return
        if 500 <= res.status_code:
            print(
                "There was an internal error while processing your request: " + res.json()['description'])
            return

    @property
    def name(self) -> str:
        """
        Get the name of the user

        Args:
            None

        Returns:
            None        
        """
        if hasattr(self, '_name'):
            return self._name
        else:
            self._get_from_api()
            return self._name

    @property
    def dict(self) -> Dict:
        """
        Get the user as a dictionary

        Args:
            None

        Returns:
            a dictionary representing the user
        """
        if hasattr(self, '_name'):
            return {
                USER_NAME: self._name,
                USER_API_KEY: self.api_key
            }
        return {
            USER_NAME: self.name,
            USER_API_KEY: self.api_key
        }

    @classmethod
    def from_json(cls, json: Dict) -> SieveClient:
        """
        Create a SieveClient object from a dictionary

        Args:
            json:
                The dictionary to be converted

        Returns:
            The created SieveClient object
        """
        return cls(
            name=json[USER_NAME],
            api_key=json[USER_API_KEY]
        )

    def __str__(self) -> str:
        return f'SieveClient(name={self.name}, api_key={self.api_key})'

    def __repr__(self) -> str:
        return self.__str__()
