import click
import json
from sieve.api.constants import API_URL, API_BASE
from sieve.api.client import SieveClient


@click.group()
def main():
    pass


@main.command()
@click.argument("search", type=str, nargs=1)
@click.argument("query", default="", type=str, required=True)
@click.option("--limit", "-l", type=int, default=100, required=False, help="maximum number of results to return")
@click.option("--offset", "-o", type=int, default=0, required=False, help="offset to start from")
@click.option("--paginate", "-p", type=bool, required=False, help="paginate all results with page_size=limit")
@click.option("--file", "-f", default=None, type=str, required=False, help="file to write output to when specified")
def main(
    search,
    query,
    limit,
    offset,
    paginate,
    file,
):
    client = SieveClient()
    results = client.search_feedback(
        query, limit, offset, paginate
    )
    if file:
        print(f"Writing output to {file}")
        with open(file, 'w') as f:
            json.dump(results, f)
