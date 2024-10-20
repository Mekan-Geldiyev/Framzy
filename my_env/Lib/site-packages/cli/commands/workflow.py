""" CLI Commands related to interacting with workflows """

import typer
from rich import print
from rich.table import Table
import sieve.api.workflows as wf
from rich.prompt import Prompt

cli = typer.Typer()


def check_workflow_exists(name):
    get_wf = wf.info(name)
    if get_wf["status"] > 400:
        print(
            f"[red bold]ERROR:[/red bold] Could not find workflow [bold]{name}[/bold]\n"
        )
        print("Run `sieve workflow list` to list your workflows\n")
        return False
    return get_wf


@cli.command()
def list():
    data, _ = wf.list()

    print(f"\nFound {len(data)} workflows:")
    table = Table("ID", "Name")
    for item in data:
        table.add_row(item["id"], item["name"])

    print(table)
    print("\n")


@cli.command()
def delete(name: str):
    if not check_workflow_exists(name):
        return

    confirm = typer.confirm(f"Permanently delete {name}?", abort=True)
    if confirm:
        ret = wf.delete(name)
        print(ret)


@cli.command()
def info(name: str):
    get_wf = check_workflow_exists(name)
    if not get_wf:
        return
    print(get_wf)
