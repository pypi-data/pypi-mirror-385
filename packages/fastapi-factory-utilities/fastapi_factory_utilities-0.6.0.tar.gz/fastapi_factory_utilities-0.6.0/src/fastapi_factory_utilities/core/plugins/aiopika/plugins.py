"""Provides the Aiopika plugin."""

from aio_pika import connect_robust
from aio_pika.abc import AbstractRobustConnection
from fastapi import Request
from structlog.stdlib import BoundLogger, get_logger

from fastapi_factory_utilities.core.plugins.abstracts import PluginAbstract

from .configs import AiopikaConfig, build_config_from_package

_logger: BoundLogger = get_logger(__package__)


class AiopikaPlugin(PluginAbstract):
    """Aiopika plugin."""

    def __init__(self, aiopika_config: AiopikaConfig | None = None) -> None:
        """Initialize the Aiopika plugin."""
        super().__init__()
        self._aiopika_config: AiopikaConfig | None = aiopika_config
        self._robust_connection: AbstractRobustConnection | None = None

    @property
    def robust_connection(self) -> AbstractRobustConnection:
        """Get the robust connection."""
        assert self._robust_connection is not None
        return self._robust_connection

    def on_load(self) -> None:
        """On load."""
        assert self._application is not None

        # Build the configuration if not provided
        if self._aiopika_config is None:
            self._aiopika_config = build_config_from_package(package_name=self._application.PACKAGE_NAME)

    async def on_startup(self) -> None:
        """On startup."""
        assert self._application is not None
        assert self._aiopika_config is not None

        self._robust_connection = await connect_robust(url=str(self._aiopika_config.amqp_url))
        self._add_to_state(key="robust_connection", value=self._robust_connection)
        _logger.debug("Aiopika plugin connected to the AMQP server.", amqp_url=self._aiopika_config.amqp_url)

    async def on_shutdown(self) -> None:
        """On shutdown."""
        if self._robust_connection is not None:
            await self._robust_connection.close()
        _logger.debug("Aiopika plugin shutdown.")


def depends_robust_connection(request: Request) -> AbstractRobustConnection:
    """Depends on the robust connection.

    Args:
        request (Request): The request.

    Returns:
        AbstractRobustConnection: The robust connection.
    """
    return request.app.state.robust_connection
