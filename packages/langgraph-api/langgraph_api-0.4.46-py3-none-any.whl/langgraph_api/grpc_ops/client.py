"""gRPC client wrapper for LangGraph persistence services."""

import os

import structlog
from grpc import aio  # type: ignore[import]

from .generated.core_api_pb2_grpc import AdminStub, AssistantsStub

logger = structlog.stdlib.get_logger(__name__)


class GrpcClient:
    """gRPC client for LangGraph persistence services."""

    def __init__(
        self,
        server_address: str | None = None,
    ):
        """Initialize the gRPC client.

        Args:
            server_address: The gRPC server address (default: localhost:50051)
        """
        self.server_address = server_address or os.getenv(
            "GRPC_SERVER_ADDRESS", "localhost:50051"
        )
        self._channel: aio.Channel | None = None
        self._assistants_stub: AssistantsStub | None = None
        self._admin_stub: AdminStub | None = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def connect(self):
        """Connect to the gRPC server."""
        if self._channel is not None:
            return

        self._channel = aio.insecure_channel(self.server_address)

        self._assistants_stub = AssistantsStub(self._channel)
        self._admin_stub = AdminStub(self._channel)

        await logger.adebug(
            "Connected to gRPC server", server_address=self.server_address
        )

    async def close(self):
        """Close the gRPC connection."""
        if self._channel is not None:
            await self._channel.close()
            self._channel = None
            self._assistants_stub = None
            self._admin_stub = None
            await logger.adebug("Closed gRPC connection")

    @property
    def assistants(self) -> AssistantsStub:
        """Get the assistants service stub."""
        if self._assistants_stub is None:
            raise RuntimeError(
                "Client not connected. Use async context manager or call connect() first."
            )
        return self._assistants_stub

    @property
    def admin(self) -> AdminStub:
        """Get the admin service stub."""
        if self._admin_stub is None:
            raise RuntimeError(
                "Client not connected. Use async context manager or call connect() first."
            )
        return self._admin_stub
