""" 
CLI commands for interacting with jobs.

Note: Pushing a job is handled in sieve/cli/sieve.py
"""

import typer
from rich import print
from rich.table import Table
import sieve.api.jobs as job
import sieve

cli = typer.Typer()


@cli.callback(invoke_without_command=True)
def show_help(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


def color_status(status):
    if status == "queued":
        return f"[yellow]{status}[/yellow]"
    elif status == "finished":
        return f"[green]{status}[/green]"
    elif status == "error":
        return f"[red]{status}[/red]"
    else:
        return status


@cli.command()
def list():
    data, _ = job.list()

    print(f"\nFound {len(data)} jobs:")
    table = Table("Job ID", "Workflow ID", "Status")
    for item in data:
        table.add_row(item["id"], item["workflow_id"], color_status(item["status"]))

    print(table)
    print("\n")


@cli.command()
def status(job_id: str):
    ret = job.status(job_id)
    print(ret)


@cli.command()
def info(job_id: str):
    ret = job.info(job_id)
    print(ret)


@cli.command()
def get(job_id: str):
    ret = job.get(job_id)
    print(ret)


@cli.command()
def logs(job_id: str):
    ret = sieve.logs(job_id=job_id)
    print(ret)
