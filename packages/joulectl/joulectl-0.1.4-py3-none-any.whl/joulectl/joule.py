import click
from tabulate import tabulate

from joulectl.commands import listcmds, deploycmds, inspectcmds, undeploycmds, ucmgmtcmds
from joulectl.config.config import CONFIG_FILE, DEFAULT_JOULE_HOST, load_config, save_config

@click.group()
@click.version_option()
@click.pass_context
def cli(ctx: click.Context):
    """Joule deployment and management tool \n
    joulctl version 0.1.3
    """
    tc = load_config()

    # Initialise ctx with empty dict
    ctx.ensure_object(dict)
    ctx.obj["joule_host"] = tc.get("joule_host", DEFAULT_JOULE_HOST)
    ctx.obj["config"] = tc

@cli.group()
def ls():
    """List deployed transports, streams and use cases."""
    pass

@cli.group()
def deploy():
    """Deploy command for transports, streams and use cases."""
    pass

@cli.group()
def undeploy():
    """Undeploy command for transports, streams and use cases."""
    pass

@cli.group()
def process():
    """Management command for use cases"""
    pass

@cli.group()
def inspect():
    """Get deployed specifications for transports, streams and use cases."""
    pass

@cli.group()
def config():
    """Configure joulectl setting."""
    pass

@config.command()
def create():
    """Create a new configuration file."""
    nc = load_config()
    save_config(nc)
    click.echo("Configuration created.")

@config.command()
def show():
    """Show configuration setting"""
    if not CONFIG_FILE.exists():
        click.echo("No configuration found.")
        return
    displyConfiguration()

@config.command()
@click.argument("host")
def update(host: str):
    """Update configuration setting for joule host.

    HOST address and port send commands too e.g., 192.168.1.10:60110
    """
    cg = load_config()
    if host:
        cg['joule_host'] = host
        save_config(cg)
        click.echo(f"Joule host set to {host}")

def displyConfiguration():
    dc = load_config()
    table = []
    for key, value in dc.items():
        table.append([key, value])

    click.echo(tabulate(table, headers=["Key", "Configuration"]))


## Command setting
ls.add_command(listcmds.transports)
ls.add_command(listcmds.streams)
ls.add_command(listcmds.usecases)
ls.add_command(listcmds.pods)
ls.add_command(listcmds.members)

deploy.add_command(deploycmds.transport)
deploy.add_command(deploycmds.stream)
deploy.add_command(deploycmds.usecase)

process.add_command(ucmgmtcmds.pause)
process.add_command(ucmgmtcmds.resume)

undeploy.add_command(undeploycmds.transport)
undeploy.add_command(undeploycmds.stream)
undeploy.add_command(undeploycmds.usecase)

inspect.add_command(inspectcmds.transport)
inspect.add_command(inspectcmds.stream)
inspect.add_command(inspectcmds.usecase)