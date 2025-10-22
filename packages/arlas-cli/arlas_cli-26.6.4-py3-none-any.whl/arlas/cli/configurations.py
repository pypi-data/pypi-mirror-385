import re
import sys
import typer
import yaml
from prettytable import PrettyTable
from arlas.cli.settings import ARLAS, AuthorizationService, Configuration, Resource
from arlas.cli.variables import variables
import arlas.cli.arlas_cloud as arlas_cloud
from arlas.cli.service import Service

configurations = typer.Typer()


def check_configuration_exists(name: str):
    """Checks if a given configuration exists in the ARLAS settings.

    Prints an error message to `stderr` and exits the program with an error code (1)
    if the specified configuration is not found.

    Args:
        name (str): The name of the configuration to check in `Configuration.settings.arlas`.

    Returns:
        None: This function does not return anything. It terminates the program on failure.

    Raises:
        SystemExit: The function calls `exit(1)` if the configuration does not exist,
                   which terminates the program with an error code.
    """

    if not Configuration.settings.arlas.get(name):
        error_msg = f"Error: configuration '{name}' not found"
        if len(Configuration.settings.arlas) > 0:
            error_msg += f" among: {','.join(Configuration.settings.arlas.keys())}."
        else:
            error_msg += "."
        print(error_msg, file=sys.stderr)
        exit(1)


@configurations.command(help="Set default configuration among existing configurations", name="set", epilog=variables["help_epilog"])
def set_default_configuration(name: str = typer.Argument(help="Name of the configuration to become default")):
    check_configuration_exists(name=name)
    Configuration.settings.default = name
    Configuration.save(variables["configuration_file"])
    Configuration.init(variables["configuration_file"])
    print(f"Default configuration is now '{name}'")


@configurations.command(help="Display the default configuration", name="default", epilog=variables["help_epilog"])
def default():
    if Configuration.settings.default is None:
        print("No default configuration")
    else:
        print(f"Default configuration is '{Configuration.settings.default}'")


@configurations.command(help="Check the services of a configuration", name="check", epilog=variables["help_epilog"])
def test_configuration(name: str = typer.Argument(help="Configuration to be checked")):
    check_configuration_exists(name=name)
    print("ARLAS Server: ... ", end="")
    print(f" {Service.test_arlas_server(name)}")
    print("ARLAS Persistence: ... ", end="")
    print(f" {Service.test_arlas_persistence(name)}")
    print("ARLAS IAM: ... ", end="")
    print(f" {Service.test_arlas_iam(name)}")
    print("Elasticsearch: ... ", end="")
    print(f" {Service.test_es(name)}")

@configurations.command(help="List configurations", name="list", epilog=variables["help_epilog"])
def list_configurations():
    confs = []
    for (name, conf) in Configuration.settings.arlas.items():
        if name == Configuration.settings.default:
            name += " (*)"
        confs.append([name, conf.server.location])
    tab = PrettyTable(["name", "ARLAS server url"], sortby="name", align="l")
    tab.add_rows(confs)
    print(tab)
    print("(*) Default configuration")


@configurations.command(help="Add a configuration", name="create", epilog=variables["help_epilog"])
def create_configuration(
    name: str = typer.Argument(help="Name of the configuration"),
    server: str = typer.Option(help="ARLAS Server url"),
    headers: list[str] = typer.Option([], help="header (name:value)"),

    persistence: str = typer.Option(default=None, help="ARLAS Persistence url"),
    persistence_headers: list[str] = typer.Option([], help="header (name:value)"),

    elastic: str = typer.Option(default=None, help="elasticsearch url"),
    elastic_login: str = typer.Option(default=None, help="elasticsearch login"),
    elastic_password: str = typer.Option(default=None, help="elasticsearch password"),
    elastic_headers: list[str] = typer.Option([], help="header (name:value)"),
    allow_delete: bool = typer.Option(default=False, help="Is delete command allowed for this configuration?"),

    auth_token_url: str = typer.Option(default=None, help="Token URL of the authentication service"),
    auth_headers: list[str] = typer.Option([], help="header (name:value)"),
    auth_org: str = typer.Option(default=None, help="ARLAS IAM Organization"),
    auth_login: str = typer.Option(default=None, help="login"),
    auth_password: str = typer.Option(default=None, help="password"),
    auth_client_id: str = typer.Option(default=None, help="Client ID"),
    auth_client_secret: str = typer.Option(default=None, help="Client secret"),
    auth_grant_type: str = typer.Option(default=None, help="Grant type (e.g. password)"),
    auth_arlas_iam: bool = typer.Option(default=True, help="Is it an ARLAS IAM service?")
):
    if Configuration.settings.arlas.get(name):
        print("Error: a configuration with that name already exists, please remove it first.", file=sys.stderr)
        exit(1)

    if auth_org:
        headers.append("arlas-org-filter:" + auth_org)
        auth_headers.append("arlas-org-filter:" + auth_org)
        persistence_headers.append("arlas-org-filter:" + auth_org)

    conf = ARLAS(
        server=Resource(location=server, headers=dict(map(lambda h: (h.split(":")[0], h.split(":")[1]), headers))),
        allow_delete=allow_delete)
    if persistence:
        conf.persistence = Resource(location=persistence,
                                    headers=dict(map(lambda h: (h.split(":")[0], h.split(":")[1]), persistence_headers)))

    if auth_token_url:
        conf.authorization = AuthorizationService(
            token_url=Resource(login=auth_login, password=auth_password, location=auth_token_url,
                               headers=dict(map(lambda h: (h.split(":")[0], h.split(":")[1]), auth_headers))),
            client_id=auth_client_id,
            client_secret=auth_client_secret,
            grant_type=auth_grant_type,
            arlas_iam=auth_arlas_iam
        )
    if elastic:
        conf.elastic = Resource(location=elastic, login=elastic_login, password=elastic_password,
                                headers=dict(map(lambda h: (h.split(":")[0], h.split(":")[1]), elastic_headers)))

    if len(Configuration.settings.arlas) == 0:
        # Set the first created configuration as default
        Configuration.settings.default = name
        print(f"Default configuration is now '{name}'")

    Configuration.settings.arlas[name] = conf
    Configuration.save(variables["configuration_file"])
    Configuration.init(variables["configuration_file"])
    print(f"Configuration '{name}' created.")


@configurations.command(help="Add a configuration for ARLAS Cloud", name="login", epilog=variables["help_epilog"])
def login(
    auth_login: str = typer.Argument(help="ARLAS login"),
    elastic_login: str = typer.Argument(help="Elasticsearch login"),
    elastic: str = typer.Argument(help="Elasticsearch url"),
    auth_org: str = typer.Option(default=None, help="ARLAS IAM Organization, default is your email domain name"),
    allow_delete: bool = typer.Option(default=True, help="Is delete command allowed for this configuration?"),
    auth_password: str = typer.Option(default=None, help="ARLAS password"),
    elastic_password: str = typer.Option(default=None, help="elasticsearch password")
):
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', auth_login):
        print(f"Error: login {auth_login} is not a valid email", file=sys.stderr)
        exit(1)

    name = "cloud.arlas.io." + auth_login.split("@")[0]
    if Configuration.settings.arlas.get(name):
        print("Error: a configuration with that name already exists, please remove it first.", file=sys.stderr)
        exit(1)
    print(f"Creating configuration '{name}' ...")
    if not auth_org:
        auth_org = auth_login.split("@")[1]
        print(f"Using {auth_org} as your organisation name.")
    if not auth_password:
        auth_password = typer.prompt(f"Please enter your password for ARLAS Cloud (account {auth_login})\n",
                                     hide_input=True, prompt_suffix="Password:")
    if not elastic_password:
        elastic_password = typer.prompt(f"Thank you, now, please enter your password for elasticsearch (account {elastic_login})\n",
                                        hide_input=True, prompt_suffix="Password:")

    create_configuration(
        name=name,
        server=arlas_cloud.ARLAS_SERVER,
        headers=[arlas_cloud.CONTENT_TYPE],
        persistence=arlas_cloud.ARLAS_PERSISTENCE,
        persistence_headers=[arlas_cloud.CONTENT_TYPE],
        elastic=elastic,
        elastic_login=elastic_login,
        elastic_password=elastic_password,
        elastic_headers=[arlas_cloud.CONTENT_TYPE],
        allow_delete=allow_delete,
        auth_token_url=arlas_cloud.AUTH_TOKEN_URL,
        auth_headers=[arlas_cloud.CONTENT_TYPE],
        auth_org=auth_org,
        auth_login=auth_login,
        auth_password=auth_password,
        auth_arlas_iam=True,
        auth_client_id=None,
        auth_client_secret=None,
        auth_grant_type=None,
    )
    Configuration.settings.default = name
    Configuration.save(variables["configuration_file"])
    Configuration.init(variables["configuration_file"])
    print(f"'{name}' is now your default configuration.")


@configurations.command(help="Delete a configuration", name="delete", epilog=variables["help_epilog"])
def delete_configuration(
    config: str = typer.Argument(help="Name of the configuration"),
):
    check_configuration_exists(name=config)

    # Handle default configuration
    if Configuration.settings.default == config:
        if typer.confirm(f"You are about to delete the default configuration '{config}'.\n",
                         prompt_suffix="Do you want to continue?", default=False):
            Configuration.settings.default = None
            print(f"No default configuration set any more.")
        else:
            print(f"Error: Configuration '{config}' not deleted", file=sys.stderr)
            exit(1)

    # Delete the configuration
    Configuration.settings.arlas.pop(config)
    Configuration.save(variables["configuration_file"])
    Configuration.init(variables["configuration_file"])
    print(f"Configuration '{config}' deleted.")


@configurations.command(help="Describe a configuration", name="describe", epilog=variables["help_epilog"])
def describe_configuration(
    config: str = typer.Argument(help="Name of the configuration"),
):
    check_configuration_exists(name=config)
    print(yaml.dump(Configuration.settings.arlas[config].model_dump()))
