"""
This file defines the CLI for Sieve.

It directly defines the push and deploy commands, which allow the
user to push a job or define a new workflow. It also defines the
overall CLI structure.
"""

from requests import request
import requests
import typer
from typing import Dict, Optional, List
from rich import print
from sieve.api import utils
from sieve.functions.function import _Function, Model
import sieve
from sieve._openapi import ApiException
from sieve._cli.commands import secret
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


def find_sieve_decorator(obj: ast.stmt):
    if not (isinstance(obj, ast.FunctionDef) or isinstance(obj, ast.ClassDef)):
        return False
    for dec in obj.decorator_list:
        if (
            isinstance(dec, ast.Call)
            and isinstance(dec.func, ast.Attribute)
            and isinstance(dec.func.value, ast.Name)
            and dec.func.value.id == "sieve"
            and (dec.func.attr == "function" or dec.func.attr == "Model")
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
    if not paths:
        paths = ["."]

    searchable_files = []
    for filepath in paths:  # each argument can be a file or path
        if os.path.isfile(filepath) and os.path.splitext(filepath)[1] == ".py":
            searchable_files.append(filepath)
        elif os.path.isdir(
            filepath
        ):  # for a dir, search recursively for all Python files
            searchable_files.extend([str(p) for p in Path(filepath).rglob("*.py")])

    found_files, found_funcs = {}, []
    for path in searchable_files:
        module_name = os.path.splitext(os.path.basename(path))[0]
        with open(path, "r") as f:
            node = ast.parse(f.read())
            for obj in node.body:
                sieve_dec = find_sieve_decorator(obj)
                if sieve_dec:
                    dec_inputs = {
                        k.arg for k in sieve_dec.keywords
                    }
                    if "name" not in dec_inputs:
                        raise TypeError(
                            "Please provide a name for your Sieve function and model annotations"
                        )

                    # import modules that contain Sieve decorators
                    if (
                        sieve_dec.func.attr == "function"
                        or sieve_dec.func.attr == "Model"
                    ):
                        if path not in found_files:  # only import files once
                            found_files[path] = import_file(module_name, path)

                    if (
                        sieve_dec.func.attr == "function"
                        or sieve_dec.func.attr == "Model"
                    ):
                        found_funcs.append(getattr(found_files[path], obj.name))
    if len(found_funcs) == 0:
        print("[red bold]Error:[/red bold] No Sieve functions found")
        return

    built_funcs = []
    for obj in found_funcs:
        model_ref = sieve.upload(obj, single_build=False)
        if not model_ref:
            raise Exception("Failed to build function")
        built_funcs.append(model_ref)

    built_funcs_table = Table("Name", "Deployment", "Version ID")

    for built_func in built_funcs:
        url = f"https://sievedata.com/functions/{built_func.owner}/{built_func.name}"
        built_funcs_table.add_row(built_func.name, url, built_func.id)

    if len(found_funcs) > 0:
        print(f"\n[green]:handshake:[/green] [bold]Functions deployed![/bold]")
        print(built_funcs_table)


@cli.command()
def whoami():
    try:
        user, org = sieve.whoami()
    except ApiException:
        print("[red bold]Error: Invalid API Key[/red bold]")
        exit(1)

    print(f"Email: {user.email}")
    print(f"Organization name: {org.name}")


@cli.command()
def login():
    key = typer.prompt("Please enter your API key", hide_input=True)
    try:
        _, org = sieve.whoami(api_key=key)
        sieve.write_key(key)
        print(":white_check_mark: Successfully logged in as", org.name)
    except ApiException:
        print("[red bold]Error: Invalid API Key[/red bold]")
        exit(1)


cli.add_typer(secret.cli, name="secret")


@cli.callback()
def callback(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())
        raise typer.Exit()


def start_cli():
    utils.IS_CLI = True
    cli()


if __name__ == "__main__":
    start_cli()
