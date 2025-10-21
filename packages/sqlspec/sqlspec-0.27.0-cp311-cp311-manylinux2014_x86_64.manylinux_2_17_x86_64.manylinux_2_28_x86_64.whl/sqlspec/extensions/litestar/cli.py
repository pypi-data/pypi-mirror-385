"""Litestar CLI integration for SQLSpec migrations."""

from contextlib import suppress
from typing import TYPE_CHECKING

import rich_click as click
from litestar.cli._utils import LitestarGroup

from sqlspec.cli import add_migration_commands

if TYPE_CHECKING:
    from litestar import Litestar

    from sqlspec.extensions.litestar.plugin import SQLSpecPlugin


def get_database_migration_plugin(app: "Litestar") -> "SQLSpecPlugin":
    """Retrieve the SQLSpec plugin from the Litestar application's plugins.

    Args:
        app: The Litestar application

    Returns:
        The SQLSpec plugin

    Raises:
        ImproperConfigurationError: If the SQLSpec plugin is not found
    """
    from sqlspec.exceptions import ImproperConfigurationError
    from sqlspec.extensions.litestar.plugin import SQLSpecPlugin

    with suppress(KeyError):
        return app.plugins.get(SQLSpecPlugin)
    msg = "Failed to initialize database migrations. The required SQLSpec plugin is missing."
    raise ImproperConfigurationError(msg)


@click.group(cls=LitestarGroup, name="db", aliases=["database"])
def database_group(ctx: "click.Context") -> None:
    """Manage SQLSpec database components."""
    ctx.obj = {"app": ctx.obj, "configs": get_database_migration_plugin(ctx.obj.app).config}


add_migration_commands(database_group)


def add_sessions_delete_expired_command() -> None:
    """Add delete-expired command to Litestar's sessions CLI group."""
    try:
        from litestar.cli._utils import console
        from litestar.cli.commands.sessions import get_session_backend, sessions_group
    except ImportError:
        return

    @sessions_group.command("delete-expired")  # type: ignore[misc]
    @click.option(
        "--verbose", is_flag=True, default=False, help="Show detailed information about the cleanup operation"
    )
    def delete_expired_sessions_command(app: "Litestar", verbose: bool) -> None:
        """Delete expired sessions from the session store.

        This command removes all sessions that have passed their expiration time.
        It can be scheduled via cron or systemd timers for automatic maintenance.

        Examples:
            litestar sessions delete-expired
            litestar sessions delete-expired --verbose
        """
        import anyio

        backend = get_session_backend(app)
        store = backend.config.get_store_from_app(app)

        if not hasattr(store, "delete_expired"):
            console.print(f"[red]{type(store).__name__} does not support deleting expired sessions")
            return

        async def _delete_expired() -> int:
            return await store.delete_expired()  # type: ignore[no-any-return]

        count = anyio.run(_delete_expired)

        if count > 0:
            if verbose:
                console.print(f"[green]Successfully deleted {count} expired session(s)")
            else:
                console.print(f"[green]Deleted {count} expired session(s)")
        else:
            console.print("[yellow]No expired sessions found")


add_sessions_delete_expired_command()
