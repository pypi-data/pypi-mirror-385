import click
import requests
from tabulate import tabulate
from joulectl import joulecomms as jc

def displayResponse(pod: str, response: requests.Response):
    if pod:
        data = response.json()
        table = []
        for rsp in data["hostResponses"]:
            cmd = rsp["command"]
            msg = rsp["message"]
            code = rsp["serviceCode"]
        table.append([rsp["host"], cmd, code, msg])
        click.echo(tabulate(table,headers=["Host","Command", "Response", "Message"]))
    else:
        click.echo(response.text)

@click.command()
@click.option("--pod", help="Joule pod name", default="")
@click.argument("name")
@click.argument("type")
@click.pass_context
def transport(ctx: click.Context, pod: str, name: str, type: str):
    """Undeploy transport

    NAME of the transport \n
    TYPE must be one of: SOURCE or SINK
    """
    if type == "SOURCE" or type == "SINK":
        joule_host = ctx.obj["joule_host"]

        url = f"http://{joule_host}/joule/management/transports/unregister"
        params = {'name': name, 'type': type, 'pod': pod}
        response = jc.callServer(method="DELETE", url=url, host=joule_host, headers={},params=params)
        if response.status_code == 200:
            displayResponse(pod, response)
        else:
            click.echo(response.text)
    else:
        click.echo("Unknown transport type: {}".format(type))

@click.command()
@click.option("--pod", help="Joule pod name", default="")
@click.argument("name")
@click.pass_context
def stream(ctx: click.Context, name: str, pod: str):
    """Undeploy stream

    NAME of stream
    """
    joule_host = ctx.obj["joule_host"]
    url = f"http://{joule_host}/joule/management/stream/unregister"
    params = {'name': name, 'pod': pod}
    response = jc.callServer(method="DELETE", url=url, host=joule_host, headers={},params=params)
    if response.status_code == 200:
        displayResponse(pod, response)
    else:
        click.echo(response.text)

@click.command()
@click.option("--pod", help="Joule pod name", default="")
@click.argument("name")
@click.pass_context
def usecase(ctx: click.Context, name: str, pod: str):
    """Undeploy use case

    NAME of use case
    """
    joule_host = ctx.obj["joule_host"]
    url = f"http://{joule_host}/joule/management/usecase/undeploy"
    params = {'name': name, 'pod': pod}
    response = jc.callServer(method="DELETE", url=url, host=joule_host, headers={},params=params)
    displayResponse(pod, response)