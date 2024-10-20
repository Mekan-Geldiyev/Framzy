""" CLI Commands for interacting with models"""

import typer
from rich import print
from rich.table import Table
import sieve.api.models as model
import ast
import sieve

cli = typer.Typer()


def color_status(status):
    if status == "building":
        return f"[yellow]{status}[/yellow]"
    elif status == "ready":
        return f"[green]{status}[/green]"
    elif status == "error":
        return f"[red]{status}[/red]"


@cli.command()
def push(
    model_id: str,
    inputs: str = typer.Argument(..., callback=ast.literal_eval),
    env: str = typer.Argument(..., callback=ast.literal_eval),
):
    sieve.push(model_id=model_id, inputs=inputs, env=env)


@cli.command()
def list():
    data, _ = model.list()
    print(f"\nFound {len(data)} models:")
    table = Table("ID", "Name", "Status", "GPU")
    for item in data:
        table.add_row(
            item["id"], item["name"], color_status(item["status"]), item["gpu"]
        )

    print(table)
    print("\n")


@cli.command()
def status(model_id: str):
    ret = model.status(model_id)
    print(ret)


@cli.command()
def info(model_id: str):
    ret = model.info(model_id)
    print(ret)
