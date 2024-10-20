from typing import Union
import click
import yaml

from sieve.api.constants import PROJECT_LAYERS, PROJECT_FPS, PROJECT_STORE_DATA

COMMAND_TYPES = {
    "list": ['ls', 'list'],
    "job-status": ['job-status', 'job', 'jobs'],
    "delete": ['delete', 'del'],
    "create": ['create'],
    "push": ['push'],
}

@click.group()
def main():
    pass

@main.command()
@click.argument("project_name", type=str)
@click.argument("command", nargs=1)
@click.argument('extra_arg', required=False)
@click.option("--limit", "-l", type=int, default=100,  help="maximum number of results to return")
@click.option("--offset", "-o", type=int, default=0, help="offset to start from")
@click.option("--workflow", "-wf", type=click.Path(exists=True), help="workflow to use for project")
@click.option("--fps", type=int, default=30, help="frames per second")
@click.option("--store-data", type=bool, default=True, help="store data in Sieve's system")
@click.option("--source-name", type=str, help="name of resource to initialize project with")
@click.option("--source-url", type=str, help="url of source to initialize project with")
@click.option("--source-path", type=click.Path(exists=True), help="path to local source to initialize project with")
@click.option("--last-layer", type=int, default=-1, help="last layer to use for project")
def main(
    project_name,
    command,
    extra_arg,
    limit,
    offset,
    workflow,
    fps,
    store_data,
    source_name,
    source_url,
    source_path,
    last_layer
):
    from sieve.api.client import SieveClient, SieveProject
    from sieve.types.api import SieveWorkflow
    client = SieveClient()
    if command in COMMAND_TYPES["list"]:
        for j in client.list_jobs(project_name, limit=limit, offset=offset):
            print(j)
    elif command in COMMAND_TYPES["job-status"]:
        try:
            print(client.get_job(project_name, extra_arg))
        except Exception as e:
            print(str(e))
    elif command in COMMAND_TYPES["delete"]:
        try:
            print(client.delete_project(project_name))
        except Exception as e:
            print(str(e))
    elif command in COMMAND_TYPES["create"]:
        wf = yaml.safe_load(open(workflow, 'r'))
        proj = SieveProject(
            name=project_name,
            workflow=SieveWorkflow.from_json(wf[PROJECT_LAYERS]),
            fps=wf[PROJECT_FPS],
            store_data=wf[PROJECT_STORE_DATA],
        )
        try:
            print(client.create_project(proj))
        except Exception as e:
            print(str(e))
    elif command in COMMAND_TYPES["push"]:
        if source_url:
            local_upload = False
        elif source_path:
            local_upload = True
            source_url = source_path
        try:
            print(client.push(project_name, source_name, source_url, last_layer, local_upload=local_upload))
        except Exception as e:
            print(str(e))
