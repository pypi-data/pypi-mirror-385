import typer

from arlas.cli.service import Service
from arlas.cli.variables import variables

user = typer.Typer()


@user.command(help="Create user", name="add", epilog=variables["help_epilog"])
def add(email: str = typer.Argument(help="User's email")):
    config = variables["arlas"]
    print(Service.create_user(config, email).get("id"))


@user.command(help="Describe user", name="describe", epilog=variables["help_epilog"])
def describe(uid: str = typer.Argument(help="User's identifier")):
    config = variables["arlas"]
    print(Service.describe_user(config, uid))


@user.command(help="Update user", name="update", epilog=variables["help_epilog"])
def update(uid: str = typer.Argument(help="User's identifier"),
           oldPassword: str = typer.Option(help="Old password", default=None),
           newPassword: str = typer.Option(help="New password", default=None),
           locale: str = typer.Option(help="Locale", default=None),
           timezone: str = typer.Option(help="Timezone", default=None),
           firstname: str = typer.Option(help="Firstname", default=None),
           lastname: str = typer.Option(help="Lastname", default=None)
           ):
    config = variables["arlas"]
    print(Service.update_user(config, uid, oldPassword, newPassword, locale, timezone, firstname, lastname))


@user.command(help="Delete user", name="delete", epilog=variables["help_epilog"])
def delete(id: str = typer.Argument(help="User's identifier")):
    config = variables["arlas"]
    print(Service.delete_user(config, id).get("message"))


@user.command(help="Activate user account", name="activate", epilog=variables["help_epilog"])
def activate(id: str = typer.Argument(help="User's identifier")):
    config = variables["arlas"]
    print(Service.activate(config, id).get("message"))


@user.command(help="Deactivate user account", name="deactivate", epilog=variables["help_epilog"])
def deactivate(id: str = typer.Argument(help="User's identifier")):
    config = variables["arlas"]
    print(Service.deactivate(config, id).get("message"))


@user.command(help="Launch reset user's password process", name="reset-password", epilog=variables["help_epilog"])
def reset_password(email: str = typer.Argument(help="User's email")):
    config = variables["arlas"]
    print(Service.reset_password(config, email).get("message"))
