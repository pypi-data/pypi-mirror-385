import click
from click import Group
from litestar.plugins import CLIPlugin

from ..core.cli import coro
from ..core.database import session_maker
from .factories import UserFactory
from .services import provide_auth_service


class AuthPlugin(CLIPlugin):
    def on_cli_init(self, cli: Group) -> None:
        @cli.group(help="Manage auth, load data with ``load`` command")
        @click.version_option(prog_name="auth")
        def auth(): ...

        @auth.command(help="load auth data")
        @coro
        async def load():
            async with session_maker() as session:
                click.echo("Loading auth data...")

                for _ in range(10):
                    session.add(UserFactory.build())
                await session.commit()

        @auth.command(help="load auth data")
        @coro
        async def reset():
            async with session_maker() as session:
                auth_service = provide_auth_service(session)
                await auth_service.delete_where()
                await auth_service.create_many(
                    [UserFactory.build() for _ in range(10)], auto_commit=True
                )
