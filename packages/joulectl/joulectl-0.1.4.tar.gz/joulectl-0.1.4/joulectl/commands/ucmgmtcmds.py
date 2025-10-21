import click
import requests
from tabulate import tabulate

def displayResponse(name: str,response: requests.Response):
    table = []
    if response.status_code != 204:
        data = response.json()
        cmd = data["command"]
        code = data["aggregatedServiceCode"]
        table.append([name,cmd,code])
        click.echo(tabulate(table, headers=["Name", "Command","Response"]))
    else:
        click.echo("Unknown use case - {}".format(name))

@click.command()
@click.pass_context
@click.argument("name")
@click.option("--pod", help="Joule pod name", default="")
def resume(ctx: click.Context, name: str, pod: str):
    """Resume use case processing

    NAME is the use case
    """
    joule_host = ctx.obj["joule_host"]
    url = f"http://{joule_host}/joule/management/usecase/resume"
    params={"name": name, "pod": pod}
    response = requests.request(method="PUT", url=url, params=params)
    if response.status_code != 204:
        displayResponse(name,response)


@click.command()
@click.argument("name")
@click.pass_context
@click.option("--pod", help="Joule pod name", default="")
def pause(ctx: click.Context, name: str, pod: str):
    """Pause use case processing

    NAME is the use case
    """
    joule_host = ctx.obj["joule_host"]
    url = f"http://{joule_host}/joule/management/usecase/pause"
    params={"name": name, "pod": pod}
    response = requests.request(method="PUT", url=url, params=params)
    if response.status_code != 204:
        displayResponse(name,response)