""" CLI Commands related to secrets """

import typer
from rich import print
from rich.table import Table
from sieve._openapi.exceptions import NotFoundException
import sieve.api.secrets as secret

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
    result = secret.list()
    data = result.data

    print(f"\nFound {len(data)} secrets:")
    table = Table("Name", "Value", "Created At", "Last Modified")
    for item in data:
        table.add_row(
            item.name,
            item.value,
            item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            item.last_modified.strftime("%Y-%m-%d %H:%M:%S"),
        )

    print(table)
    print("\n")


@cli.command()
def get(name: str):
    ret = secret.get(name).model_dump()
    ret["created_at"] = ret["created_at"].strftime("%Y-%m-%d %H:%M:%S")
    ret["last_modified"] = ret["last_modified"].strftime("%Y-%m-%d %H:%M:%S")
    print(ret)


@cli.command()
def create(name: str, value: str):
    ret = secret.create(name, value)
    print("Secret created.")


@cli.command()
def update(name: str, value: str):
    ret = secret.update(name, value)
    print(ret)


@cli.command()
def delete(name: str):
    try:
        ret = secret.delete(name)
    except NotFoundException:
        print("[red]Could not find a secret called", name, "![red]")
