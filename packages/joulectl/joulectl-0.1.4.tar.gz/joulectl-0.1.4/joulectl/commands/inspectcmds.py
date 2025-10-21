import click
import json
import requests

def executeDetail(url: str, params: dict, filename: str):
    response = requests.get(url, params=params)
    if response.status_code == 652:
        click.echo("Resource not found")
        return

    if response.status_code == 200:
        data = response.json()
        with open(filename, 'w') as f:
            json.dump(data,f, ensure_ascii=False)

@click.command()
@click.pass_context
@click.argument("name")
@click.argument("type")
@click.option("--pod", help="Joule pod name", default="")
@click.option("--filename", help="filename to use for returned specification", default="")
def transport(ctx: click.Context, name: str, type: str, pod: str, filename: str):
    """Return a transport specification as a file

    NAME of the transport \n
    TYPE must be one of: SOURCE or SINK
    """
    joule_host = ctx.obj["joule_host"]
    url = f"http://{joule_host}/joule/management/transports/detail"
    params = {'type': type, 'name': name, 'pod': pod}
    specfilename = name + ".json"
    if filename:
        specfilename = filename
    executeDetail(url, params=params, filename=specfilename)

@click.command()
@click.pass_context
@click.argument("name")
@click.option("--pod", help="Joule pod name", default="")
@click.option("--filename", help="filename to use for returned specification", default="")
def stream(ctx: click.Context, name: str, pod: str, filename: str):
    """Return a stream specification as a file

    NAME of the stream
    """
    joule_host = ctx.obj["joule_host"]
    url = f"http://{joule_host}/joule/management/stream/detail"
    params = {'name': name, 'pod': pod}
    specfilename = name + ".json"
    if filename:
        specfilename = filename
    executeDetail(url, params=params, filename=specfilename)

@click.command()
@click.pass_context
@click.argument("name")
@click.option("--pod", help="Joule pod name", default="")
@click.option("--filename", help="filename to use for returned specification", default="")
def usecase(ctx: click.Context, name: str,pod: str, filename: str):
    """Return a use case specification as a file

    NAME of the use case
    """
    joule_host = ctx.obj["joule_host"]
    url = f"http://{joule_host}/joule/management/usecase/detail"
    params = {'name': name, 'pod':pod}
    specfilename = name + ".json"
    if filename:
        specfilename = filename
    executeDetail(url, params=params,filename=specfilename)