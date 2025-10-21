from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterable
from typing import Any, Callable, Dict, Generic, List, Mapping, Optional, TypeVar, cast

import socketio

from .constants import DEFAULT_ACK_TIMEOUT_MS, get_base_url, get_package_version
from .options import (
    ServerOptionsDict,
    StreamOptionsDict,
    _ServerOptions,
    _StreamOptions,
    normalize_server_options,
    normalize_stream_options,
)
from .protocol import (
    CURRENT_PROTOCOL_VERSION,
    ConnectionServerToClientEvents,
    ProducerClientToServerEvents,
    ProducerHandshakeAuth,
    ProducerServerToClientEvents,
    StreamChunkAckPayload,
    StreamEndNotification,
    StreamEndReason,
    StreamErrorPayload,
    StreamInfoPayload,
)
from .utils import ensure_async_iterable


def _default_encode_chunk(chunk: Any) -> str:
    """Encode outbound payloads, supporting Pydantic v2 models by default."""

    model_dump_json = getattr(chunk, "model_dump_json", None)
    if callable(model_dump_json):
        # Pydantic v2 models expose ``model_dump_json`` which already returns a ``str``.
        return cast(str, model_dump_json())

    return json.dumps(chunk, separators=(",", ":"))


logger = logging.getLogger(__name__)

C = TypeVar("C")


class StreamstraightServerError(Exception):
    """Raised when the Streamstraight server SDK encounters an error."""


class StreamstraightServer(Generic[C]):
    def __init__(self, options: _ServerOptions | ServerOptionsDict | Mapping[str, Any]):
        options = normalize_server_options(options)
        if not options.api_key:
            raise StreamstraightServerError("api_key is required")

        self._options = options
        self._socket: Optional[socketio.AsyncClient] = None
        self._stream_options: Optional[_StreamOptions[C]] = None
        self._seq = 0
        self._ack_futures: Dict[int, asyncio.Future[StreamChunkAckPayload]] = {}
        self._ack_timeouts: Dict[int, asyncio.TimerHandle] = {}
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._connect_lock = asyncio.Lock()

    async def connect(
        self, stream_options: _StreamOptions[C] | StreamOptionsDict | Mapping[str, Any]
    ) -> None:
        stream_options = normalize_stream_options(stream_options)
        logger.info(
            "[streamstraight-server] connect requested stream_id=%s overwrite=%s keep_open=%s",
            stream_options.stream_id,
            stream_options.overwrite_existing_stream,
            stream_options.keep_open,
        )
        async with self._connect_lock:
            if self._socket and self._socket.connected:
                self._stream_options = stream_options
                logger.debug("[streamstraight-server] reusing existing socket")
                return

            self._stream_options = stream_options
            self._loop = asyncio.get_running_loop()
            self._seq = 0
            self._ack_futures.clear()
            self._ack_timeouts.clear()
            self._socket = socketio.AsyncClient()

            self._register_handlers()

            url = self._options.base_url or get_base_url()
            auth: ProducerHandshakeAuth = {
                "role": "producer",
                "streamId": stream_options.stream_id,
                "version": CURRENT_PROTOCOL_VERSION,
                "sdkVersion": get_package_version(),
            }
            if stream_options.overwrite_existing_stream:
                auth["overwriteExistingStream"] = True

            headers = {"Authorization": f"Bearer {self._options.api_key}"}

            logger.info(
                "[streamstraight-server] connecting url=%s role=%s stream_id=%s",
                url,
                auth["role"],
                stream_options.stream_id,
            )
            try:
                await self._socket.connect(url, auth=auth, headers=headers)
                logger.info(
                    "[streamstraight-server] socket connected stream_id=%s",
                    stream_options.stream_id,
                )
            except Exception as exc:  # pragma: no cover - passthrough to caller
                await self._cleanup_socket()
                raise StreamstraightServerError(str(exc)) from exc

    async def _cleanup_socket(self) -> None:
        if self._socket:
            try:
                await self._socket.disconnect()
            except Exception:  # pragma: no cover - best effort cleanup
                pass
        logger.debug("[streamstraight-server] socket cleanup complete")
        self._socket = None
        self._reject_all_acks(StreamstraightServerError("socket not initialized"))
        self._ack_timeouts.clear()
        self._stream_options = None
        self._loop = None

    def _register_handlers(self) -> None:
        if not self._socket:
            return

        async def on_connect() -> None:
            logger.debug("[streamstraight-server] connected")

        async def on_disconnect() -> None:
            logger.debug("[streamstraight-server] disconnected")
            self._reject_all_acks(StreamstraightServerError("socket disconnected"))

        async def on_connect_error(error: Any) -> None:
            logger.error("[streamstraight-server] connect_error %s", error)
            self._reject_all_acks(
                StreamstraightServerError(
                    "Connection error. Please check your internet connection."
                )
            )

        async def on_connection_error(payload: Dict[str, Any]) -> None:
            logger.error(
                "[streamstraight-server] %s %s",
                ConnectionServerToClientEvents.ERROR,
                payload,
            )

        async def on_ack(payload: StreamChunkAckPayload) -> None:
            seq = payload["seq"]
            logger.debug(
                "[streamstraight-server] ack received seq=%s redis_id=%s",
                payload["seq"],
                payload["redisId"],
            )
            future = self._ack_futures.pop(seq, None)
            timeout = self._ack_timeouts.pop(seq, None)
            if timeout:
                timeout.cancel()
            if future and not future.done():
                future.set_result(payload)

        async def on_error(payload: StreamErrorPayload) -> None:
            logger.error(
                "[streamstraight-server] %s %s",
                ProducerServerToClientEvents.ERROR,
                payload,
            )

        async def on_info(payload: StreamInfoPayload) -> None:
            logger.debug(
                "[streamstraight-server] %s %s",
                ProducerServerToClientEvents.INFO,
                payload,
            )

        self._socket.event(on_connect)
        self._socket.event(on_disconnect)
        self._socket.on("connect_error", on_connect_error)
        self._socket.on(ConnectionServerToClientEvents.ERROR, on_connection_error)
        self._socket.on(ProducerServerToClientEvents.ACK, on_ack)
        self._socket.on(ProducerServerToClientEvents.ERROR, on_error)
        self._socket.on(ProducerServerToClientEvents.INFO, on_info)

    def _reject_all_acks(self, error: Exception) -> None:
        for future in self._ack_futures.values():
            if not future.done():
                future.set_exception(error)
        for timeout in self._ack_timeouts.values():
            timeout.cancel()
        self._ack_futures.clear()
        self._ack_timeouts.clear()

    def _create_ack_future(self, seq: int) -> asyncio.Future[StreamChunkAckPayload]:
        if not self._loop:
            raise StreamstraightServerError("event loop not initialized")
        future: asyncio.Future[StreamChunkAckPayload] = self._loop.create_future()
        self._ack_futures[seq] = future

        timeout_ms = self._options.ack_timeout_ms or DEFAULT_ACK_TIMEOUT_MS
        timeout_seconds = timeout_ms / 1000

        def on_timeout() -> None:
            if future.done():
                return
            future.set_exception(StreamstraightServerError("Ack timeout"))
            self._ack_futures.pop(seq, None)

        handle = self._loop.call_later(timeout_seconds, on_timeout)
        self._ack_timeouts[seq] = handle
        return future

    async def _send_chunk(self, data: str) -> asyncio.Future[StreamChunkAckPayload]:
        if not self._socket or not self._socket.connected:
            raise StreamstraightServerError("socket not initialized")

        seq = self._seq
        self._seq += 1

        future = self._create_ack_future(seq)
        logger.debug("[streamstraight-server] emitting chunk seq=%s size=%s", seq, len(data))

        def _log_ack_completion(fut: asyncio.Future[StreamChunkAckPayload]) -> None:
            status = "cancelled"
            redis_id: str | None = None
            if fut.cancelled():
                pass
            else:
                try:
                    payload = fut.result()
                except Exception as exc:  # pragma: no cover - diagnostic only
                    status = f"error:{exc}"
                else:
                    status = "ok"
                    redis_id = payload["redisId"]
            logger.debug(
                "[streamstraight-server] ack future resolved seq=%s status=%s redis_id=%s",
                seq,
                status,
                redis_id,
            )

        future.add_done_callback(_log_ack_completion)
        payload = {"seq": seq, "data": data}

        try:
            await self._socket.emit(ProducerClientToServerEvents.CHUNK, payload)
        except Exception as exc:
            timeout = self._ack_timeouts.pop(seq, None)
            if timeout:
                timeout.cancel()
            self._ack_futures.pop(seq, None)
            if not future.done():
                future.set_exception(StreamstraightServerError(str(exc)))
            raise

        return future

    async def _send_end(
        self,
        last_ack: StreamChunkAckPayload | None,
        chunk_count: int,
        *,
        reason: StreamEndReason = "completed",
    ) -> StreamChunkAckPayload:
        if not self._socket or not self._socket.connected:
            raise StreamstraightServerError("socket not initialized")

        if last_ack and last_ack.get("seq") is not None:
            last_seq = int(last_ack["seq"])
        else:
            last_seq = max(self._seq - 1, 0)

        end_payload: StreamEndNotification = {
            "reason": reason,
            "lastSeq": last_seq,
        }

        redis_id = last_ack.get("redisId") if last_ack else None
        if redis_id:
            end_payload["redisId"] = redis_id

        logger.info(
            "[streamstraight-server] emitting end frame last_seq=%s redis_id=%s chunks=%s reason=%s",
            last_seq,
            end_payload.get("redisId"),
            chunk_count,
            reason,
        )

        end_seq = last_seq + 1
        end_ack_future = self._create_ack_future(end_seq)
        try:
            await self._socket.emit(ProducerClientToServerEvents.END, end_payload)
        except Exception as exc:
            timeout = self._ack_timeouts.pop(end_seq, None)
            if timeout:
                timeout.cancel()
            self._ack_futures.pop(end_seq, None)
            if not end_ack_future.done():
                end_ack_future.set_exception(StreamstraightServerError(str(exc)))
            raise

        return await end_ack_future

    async def _send_iterable(self, source: AsyncIterable[C] | Any) -> None:
        if not self._stream_options:
            raise StreamstraightServerError("stream options not initialized")

        encoder = self._stream_options.encoder or _default_encode_chunk

        logger.info(
            "[streamstraight-server] starting stream emission stream_id=%s",
            self._stream_options.stream_id,
        )

        ack_futures: List[asyncio.Future[StreamChunkAckPayload]] = []
        chunk_count = 0
        last_ack: StreamChunkAckPayload | None = None

        try:
            async for chunk in ensure_async_iterable(source):
                encoded_chunk = encoder(chunk)
                if not isinstance(encoded_chunk, str):
                    raise StreamstraightServerError("encoder must return a string")
                if encoded_chunk == "":
                    continue
                chunk_count += 1
                logger.debug(
                    "[streamstraight-server] queueing chunk index=%s length=%s",
                    chunk_count,
                    len(encoded_chunk),
                )
                ack_future = await self._send_chunk(encoded_chunk)
                ack_futures.append(ack_future)

            if ack_futures:
                logger.debug(
                    "[streamstraight-server] awaiting %s ack(s) for stream",
                    len(ack_futures),
                )
                acks = await asyncio.gather(*ack_futures)
                logger.debug(
                    "[streamstraight-server] received %s ack(s) for stream",
                    len(ack_futures),
                )
                last_ack = acks[-1] if acks else None

            await self._send_end(last_ack, chunk_count, reason="completed")
        except Exception as exc:
            stream_error = (
                exc
                if isinstance(exc, StreamstraightServerError)
                else StreamstraightServerError(str(exc))
            )
            stream_id = self._stream_options.stream_id if self._stream_options else "<unknown>"
            logger.exception(
                "[streamstraight-server] stream emission failed stream_id=%s error=%s",
                stream_id,
                stream_error,
            )

            self._reject_all_acks(stream_error)

            pending: List[asyncio.Future[StreamChunkAckPayload]] = list(ack_futures)
            if pending:
                await asyncio.gather(*pending, return_exceptions=True)

            await self.disconnect()

            if stream_error is exc:
                raise
            raise stream_error from exc

    async def stream(self, source: AsyncIterable[C] | Any) -> None:
        if not self._stream_options:
            raise StreamstraightServerError("stream options not initialized")

        logger.info(
            "[streamstraight-server] streaming payload stream_id=%s",
            self._stream_options.stream_id,
        )
        try:
            await self._send_iterable(source)
        except Exception:
            # _send_iterable already disconnects and wraps the error; just propagate.
            raise
        else:
            if not self._stream_options.keep_open:
                logger.debug("[streamstraight-server] keep_open disabled; disconnecting")
                await self.disconnect()

    async def disconnect(self) -> None:
        await self._cleanup_socket()

    def stream_writer(self) -> "StreamWriter[C]":
        return StreamWriter(self)


class StreamWriter(Generic[C]):
    def __init__(self, server: StreamstraightServer[C]) -> None:
        self._server = server
        self._encoder: Optional[Callable[[C], str]] = None
        self._chunk_count = 0
        self._last_ack: StreamChunkAckPayload | None = None
        self._closed = False
        self._close_ack: StreamChunkAckPayload | None = None
        self._lock = asyncio.Lock()

    async def __aenter__(self) -> "StreamWriter[C]":
        options = self._server._stream_options
        if not options:
            raise StreamstraightServerError(
                "stream options not initialized; call streamstraight_server(...) or server.connect(...) first"
            )

        await self._server.connect(options)
        if not self._server._stream_options:
            raise StreamstraightServerError("stream options not initialized")

        self._encoder = self._server._stream_options.encoder or _default_encode_chunk
        self._chunk_count = 0
        self._last_ack = None
        self._closed = False
        self._close_ack = None
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        reason: StreamEndReason = "completed" if exc_type is None else "aborted"
        try:
            await self.close(reason=reason)
        except Exception:
            if exc_type is None:
                raise
            logger.exception("[streamstraight-server] writer close failed during context exit")

    async def send(self, chunk: C) -> StreamChunkAckPayload | None:
        if self._closed:
            raise StreamstraightServerError("stream writer already closed")
        if self._encoder is None:
            raise StreamstraightServerError("stream writer not initialized")

        encoded_chunk = self._encoder(chunk)
        if not isinstance(encoded_chunk, str):
            raise StreamstraightServerError("encoder must return a string")
        if encoded_chunk == "":
            return None

        async with self._lock:
            if self._closed:
                raise StreamstraightServerError("stream writer already closed")
            ack_future = await self._server._send_chunk(encoded_chunk)
            ack = await ack_future
            self._chunk_count += 1
            self._last_ack = ack
            return ack

    async def close(self, *, reason: StreamEndReason = "completed") -> StreamChunkAckPayload | None:
        async with self._lock:
            if self._closed:
                return self._close_ack
            self._closed = True

        try:
            ack = await self._server._send_end(self._last_ack, self._chunk_count, reason=reason)
            self._close_ack = ack
            return ack
        finally:
            options = self._server._stream_options
            if not options or not options.keep_open:
                await self._server.disconnect()
