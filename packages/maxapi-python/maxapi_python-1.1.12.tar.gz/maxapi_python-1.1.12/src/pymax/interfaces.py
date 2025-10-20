import asyncio
import logging
import socket
import ssl
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from logging import Logger
from pathlib import Path
from typing import TYPE_CHECKING, Any

import websockets

from .filters import Filter
from .static import Constants
from .types import Channel, Chat, Dialog, Me, Message, User

if TYPE_CHECKING:
    from uuid import UUID

    from .crud import Database


class ClientProtocol(ABC):
    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self.logger = logger
        self._users: dict[int, User] = {}
        self.chats: list[Chat] = []
        self.phone: str = ""
        self._database: Database
        self._device_id: UUID
        self._on_message_handlers: list[
            tuple[Callable[[Message], Any], Filter | None]
        ] = []
        self.uri: str

        self.is_connected: bool = False
        self.phone: str
        self.chats: list[Chat] = []
        self.dialogs: list[Dialog] = []
        self.channels: list[Channel] = []
        self.me: Me | None = None
        self.host: str
        self.port: int
        self._users: dict[int, User] = {}
        self._work_dir: str
        self._database_path: Path
        self._ws: websockets.ClientConnection | None = None
        self._seq: int = 0
        self._pending: dict[int, asyncio.Future[dict[str, Any]]] = {}
        self._recv_task: asyncio.Task[Any] | None = None
        self._incoming: asyncio.Queue[dict[str, Any]] | None = None
        self.user_agent = Constants.DEFAULT_USER_AGENT.value

        self._session_id: int
        self._action_id: int = 0
        self._current_screen: str = "chats_list_tab"

        self._on_message_handlers: list[
            tuple[Callable[[Message], Any], Filter | None]
        ] = []
        self._on_start_handler: Callable[[], Any | Awaitable[Any]] | None = None
        self._background_tasks: set[asyncio.Task[Any]] = set()
        self._ssl_context: ssl.SSLContext
        self._socket: socket.socket | None = None

    @abstractmethod
    async def _send_and_wait(
        self,
        opcode: int,
        payload: dict[str, Any],
        cmd: int = 0,
        timeout: float = Constants.DEFAULT_TIMEOUT.value,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    async def _get_chat(self, chat_id: int) -> Chat | None:
        pass
