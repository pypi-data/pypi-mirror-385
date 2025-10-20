import click
import typer

from arlas.cli.service import Service
from arlas.cli.settings import Configuration
from arlas.cli.variables import variables

iam = typer.Typer()


@iam.callback()
def configuration(ctx: click.Context,
                  config: str = typer.Option(default=None,
                                             help=f"Name of the ARLAS configuration to use from your configuration file"
                                                  f" ({variables['configuration_file']}).")):
    quiet = ctx.invoked_subcommand in ["token"]
    variables["arlas"] = Configuration.solve_config(config, quiet=quiet)


@iam.command(help="Get ARLAS token", name="token", epilog=variables["help_epilog"])
def token():
    config = variables["arlas"]
    print(Service.__get_token__(arlas=config))