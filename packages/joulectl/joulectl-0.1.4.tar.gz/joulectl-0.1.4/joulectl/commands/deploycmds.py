import click
from tabulate import tabulate
from joulectl import joulecomms as jc

def executeDeploy(url: str, filename: str, params: dict, host: str):
    response = jc.postData(url=url,
                           filename=filename,
                           params=params,
                           headers={"Content-Type": "application/json; charset=utf-8"},
                           host=host)
    if params["pod"]:
        data = response.json()
        table = []
        for rsp in data["hostResponses"]:
            cmd = rsp["command"]
            msg = rsp["message"]
            code = rsp["serviceCode"]
        table.append([rsp["host"], cmd, code, msg])
        click.echo(tabulate(table, headers=["Host","Command", "Response", "Message"]))
    else:
       click.echo(response.text)

@click.command()
@click.argument("filename", type=click.Path(exists=True))
@click.option("--pod", help="Joule pod name", default="")
@click.pass_context
def transport(ctx: click.Context, filename: str, pod: str):
    """Deploy transport to the Joule server.

    FILENAME is the specification file to deploy
    """
    joule_host = ctx.obj["joule_host"]
    url = f"http://{joule_host}/joule/management/transports/register"
    options = {'pod':pod}
    executeDeploy(url=url,
                filename=filename,
                params=options,
                host=joule_host)

@click.command()
@click.argument("filename",type=click.Path(exists=True))
@click.option("--pod", help="Joule pod name", default="")
@click.pass_context
def stream(ctx: click.Context, filename: str, pod: str):
    """Deploy a stream to the Joule server.

    FILENAME is the specification file to deploy
    """
    joule_host = ctx.obj["joule_host"]
    url = f"http://{joule_host}/joule/management/stream/register"
    options = {'pod':pod}
    executeDeploy(url=url,
                  filename=filename,
                  params=options,
                  host=joule_host)

@click.command()
@click.argument("filename", type=click.Path(exists=True))
@click.option("--pod", help="Joule pod name", default="")
@click.pass_context
def usecase(ctx: click.Context, filename: str, pod: str):
    """Deploy use case to the Joule server.

    FILENAME is the specification file to deploy
    """
    joule_host = ctx.obj["joule_host"]
    url = f"http://{joule_host}/joule/management/usecase/deploy"
    params = {'pod':pod}
    executeDeploy(url=url,
                  filename=filename,
                  params=params,
                  host=joule_host)
