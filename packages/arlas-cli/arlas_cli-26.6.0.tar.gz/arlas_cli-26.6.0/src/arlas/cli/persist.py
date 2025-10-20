import sys

import click
import typer
from prettytable import PrettyTable

from arlas.cli.service import Service
from arlas.cli.settings import Configuration, Resource
from arlas.cli.variables import variables

persist = typer.Typer()


@persist.callback()
def configuration(ctx: click.Context,
                  config: str = typer.Option(default=None,
                                             help=f"Name of the ARLAS configuration to use from your configuration file"
                                                  f" ({variables['configuration_file']}).")):
    quiet = ctx.invoked_subcommand in ["add", "get"]
    variables["arlas"] = Configuration.solve_config(config, quiet)


@persist.command(help="Add an entry, returns its ID", name="add", epilog=variables["help_epilog"])
def add(
    file: str = typer.Argument(help="File path"),
    zone: str = typer.Argument(help="zone"),
    name: str = typer.Option(help="name", default="none"),
    reader: list[str] = typer.Option(help="Readers", default=[]),
    writer: list[str] = typer.Option(help="writers", default=[]),
    encode: bool = typer.Option(help="Encode in BASE64", default=False)
):
    config = variables["arlas"]
    entry_id = Service.persistence_add_file(config, Resource(location=file), zone=zone, name=name, readers=reader, 
                                            writers=writer, encode=encode)
    print(entry_id)


@persist.command(help="Delete an entry", name="delete", epilog=variables["help_epilog"])
def delete(
    entry_id: str = typer.Argument(help="Entry identifier")
):
    config = variables["arlas"]
    if not Configuration.settings.arlas.get(config).allow_delete:
        print(f"Error: delete on '{config}' is not allowed. "
              f"To allow delete, change your configuration file ({variables['configuration_file']}).", file=sys.stderr)
        exit(1)

    if typer.confirm(f"You are about to delete the entry '{entry_id}' on '{config}' configuration.\n",
                     prompt_suffix=f"Do you want to continue (del {entry_id} on {config})?",
                     default=False):
        if config != "local" and config.find("test") < 0:
            if typer.prompt(f"WARNING: You are not on a test environment. To delete '{entry_id}' on '{config}', "
                            f"type the name of the configuration ({config})") != config:
                print(f"Error: delete on '{config}' cancelled.", file=sys.stderr)
                exit(1)

    Service.persistence_delete(config, id=entry_id)
    print("Resource {} deleted.".format(entry_id))


@persist.command(help="Retrieve an entry", name="get", epilog=variables["help_epilog"])
def get(
    entry_id: str = typer.Argument(help="Entry identifier")
):
    config = variables["arlas"]
    print(Service.persistence_get(config, id=entry_id).get("doc_value"), end="")


@persist.command(help="List entries within a zone", name="zone", epilog=variables["help_epilog"])
def zone(
    zone: str = typer.Argument(help="Zone name")
):
    config = variables["arlas"]
    table = Service.persistence_zone(config, zone=zone)
    tab = PrettyTable(table[0], sortby="name", align="l")
    tab.add_rows(table[1:])
    print(tab)


@persist.command(help="List groups allowed to access a zone", name="groups", epilog=variables["help_epilog"])
def groups(
    zone: str = typer.Argument(help="Zone name")
):
    config = variables["arlas"]
    table = Service.persistence_groups(config, zone=zone)
    tab = PrettyTable(table[0], sortby="group", align="l")
    tab.add_rows(table[1:])
    print(tab)


@persist.command(help="Describe an entry", name="describe", epilog=variables["help_epilog"])
def describe(
    entry_id: str = typer.Argument(help="Entry identifier")
):
    config = variables["arlas"]
    table = Service.persistence_describe(config, id=entry_id)
    tab = PrettyTable(table[0], align="l")
    tab.add_rows(table[1:])
    print(tab)
