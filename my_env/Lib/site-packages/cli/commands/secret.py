""" CLI Commands related to secrets """

import typer
from rich import print
from rich.table import Table
import sieve.api.secrets as secret

cli = typer.Typer()


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
    data, _ = secret.list()

    print(f"\nFound {len(data)} secrets:")
    table = Table("Name", "Value", "Created At", "Last Modified")
    for item in data:
        table.add_row(
            item["name"], item["value"], item["created_at"], item["last_modified"]
        )

    print(table)
    print("\n")


@cli.command()
def get(name: str):
    ret = secret.get(name)
    print(ret)


@cli.command()
def create(name: str, value: str):
    ret = secret.create(name, value)
    print(ret)


@cli.command()
def update(name: str, value: str):
    ret = secret.update(name, value)
    print(ret)


@cli.command()
def delete(name: str):
    ret = secret.delete(name)
    print(ret)
