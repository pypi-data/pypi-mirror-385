import asyncio
import json
from typing import Any

import websockets
from typing_extensions import override

from pymax.exceptions import LoginError, WebSocketNotConnectedError
from pymax.interfaces import ClientProtocol
from pymax.payloads import BaseWebSocketMessage, SyncPayload
from pymax.static import ChatType, Constants, Opcode
from pymax.types import Channel, Chat, Dialog, Me, Message


class WebSocketMixin(ClientProtocol):
    @property
    def ws(self) -> websockets.ClientConnection:
        if self._ws is None or not self.is_connected:
            self.logger.critical("WebSocket not connected when access attempted")
            raise WebSocketNotConnectedError
        return self._ws

    def _make_message(
        self, opcode: int, payload: dict[str, Any], cmd: int = 0
    ) -> dict[str, Any]:
        self._seq += 1

        msg = BaseWebSocketMessage(
            ver=11,
            cmd=cmd,
            seq=self._seq,
            opcode=opcode,
            payload=payload,
        ).model_dump(by_alias=True)

        self.logger.debug(
            "make_message opcode=%s cmd=%s seq=%s", opcode, cmd, self._seq
        )
        return msg

    async def _send_interactive_ping(self) -> None:
        while self.is_connected:
            try:
                await self._send_and_wait(
                    opcode=1,
                    payload={"interactive": True},
                    cmd=0,
                )
                self.logger.debug("Interactive ping sent successfully")
            except Exception:
                self.logger.warning("Interactive ping failed", exc_info=True)
            await asyncio.sleep(30)

    async def _connect(self, user_agent: dict[str, Any]) -> dict[str, Any]:
        try:
            self.logger.info("Connecting to WebSocket %s", self.uri)
            self._ws = await websockets.connect(self.uri, origin="https://web.max.ru")  # type: ignore[]
            self.is_connected = True
            self._incoming = asyncio.Queue()
            self._pending = {}
            self._recv_task = asyncio.create_task(self._recv_loop())
            self.logger.info("WebSocket connected, starting handshake")
            return await self._handshake(user_agent)
        except Exception as e:
            self.logger.error("Failed to connect: %s", e, exc_info=True)
            raise ConnectionError(f"Failed to connect: {e}")

    async def _handshake(self, user_agent: dict[str, Any]) -> dict[str, Any]:
        try:
            self.logger.debug(
                "Sending handshake with user_agent keys=%s", list(user_agent.keys())
            )
            resp = await self._send_and_wait(
                opcode=Opcode.SESSION_INIT,
                payload={"deviceId": str(self._device_id), "userAgent": user_agent},
            )
            self.logger.info("Handshake completed")
            return resp
        except Exception as e:
            self.logger.error("Handshake failed: %s", e, exc_info=True)
            raise ConnectionError(f"Handshake failed: {e}")

    async def _recv_loop(self) -> None:
        if self._ws is None:
            self.logger.warning("Recv loop started without websocket instance")
            return

        self.logger.debug("Receive loop started")
        while True:
            try:
                raw = await self._ws.recv()
                try:
                    data = json.loads(raw)
                except Exception:
                    self.logger.warning("JSON parse error", exc_info=True)
                    continue

                seq = data.get("seq")
                fut = self._pending.get(seq) if isinstance(seq, int) else None

                if fut and not fut.done():
                    fut.set_result(data)
                    self.logger.debug("Matched response for pending seq=%s", seq)
                else:
                    if self._incoming is not None:
                        try:
                            self._incoming.put_nowait(data)
                        except asyncio.QueueFull:
                            self.logger.warning(
                                "Incoming queue full; dropping message seq=%s",
                                data.get("seq"),
                            )

                    if (
                        data.get("opcode") == Opcode.NOTIF_MESSAGE
                        and self._on_message_handlers
                    ):
                        try:
                            for handler, filter in self._on_message_handlers:
                                payload = data.get("payload", {})
                                msg = Message.from_dict(payload)
                                if msg:
                                    if msg.status:
                                        continue  # TODO: заглушка! сделать отдельный хендлер
                                    if filter:
                                        if filter.match(msg):
                                            result = handler(msg)
                                        else:
                                            continue
                                    else:
                                        result = handler(msg)
                                    if asyncio.iscoroutine(result):
                                        task = asyncio.create_task(result)
                                        self._background_tasks.add(task)
                                        task.add_done_callback(
                                            lambda t: self._background_tasks.discard(t)
                                            or self._log_task_exception(t)
                                        )
                        except Exception:
                            self.logger.exception("Error in on_message_handler")

            except websockets.exceptions.ConnectionClosed:
                self.logger.info("WebSocket connection closed; exiting recv loop")
                break
            except Exception:
                self.logger.exception("Error in recv_loop; backing off briefly")
                await asyncio.sleep(0.5)

    def _log_task_exception(self, task: asyncio.Task[Any]) -> None:
        try:
            exc = task.exception()
            if exc:
                self.logger.exception("Background task exception: %s", exc)
        except Exception:
            pass

    @override
    async def _send_and_wait(
        self,
        opcode: int,
        payload: dict[str, Any],
        cmd: int = 0,
        timeout: float = Constants.DEFAULT_TIMEOUT.value,
    ) -> dict[str, Any]:
        ws = self.ws

        msg = self._make_message(opcode, payload, cmd)
        loop = asyncio.get_running_loop()
        fut: asyncio.Future[dict[str, Any]] = loop.create_future()
        self._pending[msg["seq"]] = fut

        try:
            self.logger.debug(
                "Sending frame opcode=%s cmd=%s seq=%s", opcode, cmd, msg["seq"]
            )
            await ws.send(json.dumps(msg))
            data = await asyncio.wait_for(fut, timeout=timeout)
            self.logger.debug(
                "Received frame for seq=%s opcode=%s",
                data.get("seq"),
                data.get("opcode"),
            )
            return data
        except Exception:
            self.logger.exception(
                "Send and wait failed (opcode=%s, seq=%s)", opcode, msg["seq"]
            )
            raise RuntimeError("Send and wait failed")
        finally:
            self._pending.pop(msg["seq"], None)

    async def _sync(self) -> None:
        self.logger.info("Starting initial sync")

        payload = SyncPayload(
            interactive=True,
            token=self._token,
            chats_sync=0,
            contacts_sync=0,
            presence_sync=0,
            drafts_sync=0,
            chats_count=40,
        ).model_dump(by_alias=True)

        try:
            data = await self._send_and_wait(opcode=19, payload=payload)
            raw_payload = data.get("payload", {})

            if error := raw_payload.get("error"):
                self.logger.error("Sync error: %s", error)

                if error == "login.token":
                    if self._ws:
                        await self._ws.close()
                    self.is_connected = False
                    self._ws = None
                    self._recv_task = None
                    raise LoginError(
                        raw_payload.get("localizedMessage", "Unknown error")
                    )

                return

            for raw_chat in raw_payload.get("chats", []):
                try:
                    if raw_chat.get("type") == ChatType.DIALOG.value:
                        self.dialogs.append(Dialog.from_dict(raw_chat))
                    elif raw_chat.get("type") == ChatType.CHAT.value:
                        self.chats.append(Chat.from_dict(raw_chat))
                    elif raw_chat.get("type") == ChatType.CHANNEL.value:
                        self.channels.append(Channel.from_dict(raw_chat))
                except Exception:
                    self.logger.exception("Error parsing chat entry")

            if raw_payload.get("profile", {}).get("contact"):
                self.me = Me.from_dict(
                    raw_payload.get("profile", {}).get("contact", {})
                )

            self.logger.info(
                "Sync completed: dialogs=%d chats=%d channels=%d",
                len(self.dialogs),
                len(self.chats),
                len(self.channels),
            )

        except LoginError:
            raise
        except Exception:
            self.logger.exception("Sync failed")
            self.is_connected = False
            if self._ws:
                await self._ws.close()
            self._ws = None
            raise

    @override
    async def _get_chat(self, chat_id: int) -> Chat | None:
        for chat in self.chats:
            if chat.id == chat_id:
                return chat
        return None
