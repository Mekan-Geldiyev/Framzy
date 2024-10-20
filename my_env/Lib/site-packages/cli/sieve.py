"""
This file defines the CLI for Sieve.

It directly defines the push and deploy commands, which allow the
user to push a job or define a new workflow. It also defines the
overall CLI structure.
"""

import typer
from typing import Dict, Optional, List
from rich import print
from sieve.functions.function import _Function, Model
from sieve.workflows.workflow import _Workflow
import sieve
from cli.commands import model, workflow, job, secret
import importlib
import os
import inspect
from rich.table import Table
from rich.prompt import Prompt
import json
import ast
import importlib.machinery
from pathlib import Path
import sys
import glob
from networkx.readwrite import json_graph

cli = typer.Typer(
    help="Sieve CLI", pretty_exceptions_show_locals=False, invoke_without_command=True
)


def find_sieve_decorator(obj):
    if not hasattr(obj, "decorator_list"):
        return False
    for dec in obj.decorator_list:
        if (
            isinstance(dec, ast.Call)
            and dec.func.value.id == "sieve"
            and (
                dec.func.attr == "function"
                or dec.func.attr == "Model"
                or dec.func.attr == "workflow"
            )
        ):
            return dec
    return False


def import_file(name, path):
    try:
        parent_dir = Path(path).parents[0]
        sys.path.append(str(parent_dir))
        for p in parent_dir.rglob("*"):
            if p.is_dir():
                sys.path.append(str(p))
        return importlib.machinery.SourceFileLoader(name, path).load_module()
    except Exception as e:
        raise Exception(f"Could not import file {path}. Failed with: {e}")


def validate_wf(workflow: _Workflow):
    try:
        graph = workflow()
        graph_dict = json_graph.node_link_data(graph)
    except Exception as e:
        raise Exception(f"Could not validate workflow. Failed with: {e}")


@cli.command()
def deploy(paths: List[str] = typer.Argument(None), yes: bool = typer.Option(False)):
    """
    This function looks for Sieve decorators in the files and paths provided, and deploys them to the Sieve server.

    We first search for all files in the directories or files specified, and then search for Sieve decorators
    in each file. If a Sieve decorator is found, we import the file and add the function or workflow to the
    list of functions or workflows to deploy. We then ask for confirmation before deploying the functions and
    workflows to the Sieve server. To deploy, we call the upload and deploy functions, which uploads the zip of
    the directory containing the file.

    :param paths: List of paths to search for Sieve decorators
    :type paths: List[str]
    :param yes: Whether to skip the confirmation prompt
    :type yes: bool
    """
    if len(paths) == 0 or paths is None:  # default case is CWD
        paths = ["."]

    searchable_files = []
    for filepath in paths:  # each argument can be a file or path
        if os.path.isfile(filepath) and os.path.splitext(filepath)[1] == ".py":
            searchable_files.append(filepath)
        elif os.path.isdir(
            filepath
        ):  # for a dir, search recursively for all Python files
            searchable_files.extend([str(p) for p in Path(filepath).rglob("*.py")])

    found_files, found_funcs, found_workflows = {}, [], []
    for path in searchable_files:
        module_name = os.path.splitext(os.path.basename(path))[0]
        with open(path, "r") as f:
            node = ast.parse(f.read())
            for obj in node.body:
                sieve_dec = find_sieve_decorator(obj)
                if sieve_dec:
                    dec_inputs = {
                        k.arg: k.value.value
                        for k in sieve_dec.keywords
                        if isinstance(k.value, ast.Constant)
                    }
                    if "name" not in dec_inputs:
                        raise TypeError(
                            "Please provide a name for your Sieve function and model annotations"
                        )

                    # import modules that contain Sieve decorators
                    if (
                        sieve_dec.func.attr == "function"
                        or sieve_dec.func.attr == "Model"
                        or sieve_dec.func.attr == "workflow"
                    ):
                        if path not in found_files:  # only import files once
                            found_files[path] = import_file(module_name, path)

                    if (
                        sieve_dec.func.attr == "function"
                        or sieve_dec.func.attr == "Model"
                    ):
                        found_funcs.append(getattr(found_files[path], obj.name))
                    elif sieve_dec.func.attr == "workflow":
                        wf = getattr(found_files[path], obj.name)
                        validate_wf(wf)
                        found_workflows.append(wf)
    if len(found_funcs) == 0 and len(found_workflows) == 0:
        print("[red bold]Error:[/red bold] No Sieve functions found")
        return

    built_funcs, built_wfs = [], []
    for obj in found_funcs:
        model_ref = sieve.upload(obj, single_build=False)
        if not model_ref:
            raise Exception("Failed to build function")
        built_funcs.append(model_ref)
    for obj in found_workflows:
        wf_ref = sieve.deploy(obj)
        if not wf_ref:
            raise Exception("Failed to build workflow")
        built_wfs.append(wf_ref)

    built_funcs_table, built_wfs_table = Table("Name", "Deployment"), Table(
        "ID", "Name"
    )
    for built_func in built_funcs:
        url = f"https://sievedata.com/functions/{built_func.owner}/{built_func.name}"
        built_funcs_table.add_row(built_func.name, url)
    for built_wf in built_wfs:
        built_wfs_table.add_row(built_wf.id, built_wf.name)

    if len(found_funcs) > 0:
        print(f"\n[green]:handshake:[/green] [bold]Functions deployed![/bold]")
        print(built_funcs_table)
    if len(found_workflows) > 0:
        print(built_wfs_table)


@cli.command()
def push(
    workflow_name: str,
    inputs: str = typer.Argument(..., callback=ast.literal_eval),
    env: str = typer.Argument(..., callback=ast.literal_eval),
):
    job = sieve.push(workflow_name, inputs=inputs, env=env)


@cli.command()
def whoami():
    user_response = sieve.whoami()
    if user_response.get("status") != 200:
        print("[red bold]Error: Invalid API Key[/red bold]")
        exit(1)

    user_response.pop("status")
    user_response.pop("id")
    user_response.pop("role")
    user_response.pop("organization_id")
    user_response.pop("domain")
    user_response.pop("credits_remaining")

    user_response["Organization name"] = user_response.pop("name")
    user_response["Email"] = user_response.pop("email")

    for key, value in user_response.items():
        print(f"{key}: {value}")


@cli.command()
def login():
    key = typer.prompt("Please enter your API key", hide_input=True)
    user_response = sieve.whoami(API_KEY=key)
    if user_response.get("status") != 200:
        print("[red bold]Error: Invalid API Key[/red bold]")
        exit(1)
    else:
        sieve.write_key(key)
        print("\n[green]:heavy_check_mark:[/green] Login successful")


cli.add_typer(model.cli, name="model")
cli.add_typer(workflow.cli, name="workflow")
cli.add_typer(job.cli, name="job")
cli.add_typer(secret.cli, name="secret")


@cli.callback()
def callback(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())
        raise typer.Exit()


if __name__ == "__main__":
    cli()
