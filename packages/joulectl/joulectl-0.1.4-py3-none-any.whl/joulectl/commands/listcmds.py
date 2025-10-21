import click
import requests
from tabulate import tabulate

from joulectl import joulecomms as jc

def displayTransportList(response: requests.Response):
    table = []
    if response.status_code != 204:
        data = response.json()
        for key in data.keys():
            dd = data.get(key)
            table.append([key, dd.get("x"), dd.get("y")])
    click.echo(tabulate(table, headers=["Name", "Type","Description"]))

@click.command()
@click.pass_context
def pods(ctx: click.Context):
    """List running pods with the number of running joule processes"""
    joule_host = ctx.obj["joule_host"]
    url = f"http://{joule_host}/joule/management/pods/list"
    response = jc.callServer(method="GET",url=url, host=joule_host, headers={}, params={})
    table = []
    if response.status_code != 204:
        data = response.json()
        for element in data:
            pod = element['name']
            members = element['members']
            table.append([pod,members])

    click.echo(tabulate(table, headers=["Pod", "Members"]))

@click.command()
@click.argument("pod")
@click.pass_context
def members(ctx: click.Context, pod: str):
    """List running members within a pod

    POD name
    """
    joule_host = ctx.obj["joule_host"]
    url = f"http://{joule_host}/joule/management/pods/connected"
    response = jc.callServer(method="GET",url=url, host=joule_host, headers={}, params={'pod':pod})
    table = []
    if response.status_code != 204:
        data = response.json()
        for host in data:
            for process in data[host]:
                created = data[host][process]["created"]
                updated = data[host][process]["updated"]
                status = data[host][process]["status"]
                table.append([host,process,status, created, updated])

    click.echo(tabulate(table, headers=["Host", "Process", "Status", "Created At", "Updated At"]))

@click.command()
@click.option("--pod", prompt=False)
@click.option("--type", prompt=False)
@click.pass_context
def transports(ctx: click.Context, pod: str, type: str):
    """List deployed transports

    POD name \n
    TYPE must be one of: SOURCE or SINK if provided, otherwise all transports are listed
    """
    joule_host = ctx.obj["joule_host"]
    url = f"http://{joule_host}/joule/management/transports/list"
    if type == "SOURCE" or type == "SINK":
        response = jc.callServer(method="GET",url=url, host=joule_host, headers={}, params={'type':type, 'pod':pod})
        displayTransportList(response)
    else:
        response = jc.callServer(method="GET",url=url, host=joule_host, headers={}, params={})
        table = []
        if response.status_code != 204:
            data = response.json()
            for e in data:
                pod = e["pod"]
                name = e["name"]
                transport = e["transport"]
                type = e["type"]
                created = e["created_at"]
                table.append([pod,name,transport, type,created])
            click.echo(tabulate(table, headers=["Pod", "Name", "Transport", "Type", "Created At"]))

@click.command()
@click.option("--pod", prompt=False)
@click.pass_context
def streams(ctx: click.Context, pod:str):
    """List registered streams

    POD name
    """
    joule_host = ctx.obj["joule_host"]
    url = f"http://{joule_host}/joule/management/stream/list"

    response = jc.callServer(method="GET", url=url, host=joule_host, headers={}, params={'pod':pod})
    table = []
    if response.status_code != 204:
        data = response.json()
        for e in data:
            pod = e["pod"]
            name = e["name"]
            metrics_enabled = e["metrics_enabled"]
            telemetry_enabled = e["telemetry_enabled"]
            valid_from = e["valid_from"]
            valid_to = e["valid_to"]
            created = e["created_at"]
            table.append([pod,name,metrics_enabled,telemetry_enabled, valid_from,valid_to,created])
        click.echo(tabulate(table, headers=["Pod", "Name", "Metrics Enabled","Telemetry Enabled","Valid From", "Valid To", "Created At"]))

@click.command()
@click.pass_context
def usecases(ctx: click.Context):
    """List all deployed use cases
    """
    joule_host = ctx.obj["joule_host"]
    url = f"http://{joule_host}/joule/management/usecase/list"
    response = jc.callServer(method="GET", url=url, host=joule_host, headers={}, params={})
    data = response.json()
    click.echo(data)
    table = []
    for element in data:
        pod = element['pod']
        name = element['name']
        stream = element['stream']
        sources = element['sources']
        sinks = element['sinks']
        refData = element['ref_data']
        validFrom = element['valid_from']
        validTo = element['valid_to']
        createdAt = element['created_at']
        table.append([pod,name,stream, sources, sinks, refData, validFrom, validTo, createdAt])
    click.echo(tabulate(table, headers=["Pod","Name","Stream","Sources","Sinks","Reference Data", "Valid From", "Valid To","Created At"]))

