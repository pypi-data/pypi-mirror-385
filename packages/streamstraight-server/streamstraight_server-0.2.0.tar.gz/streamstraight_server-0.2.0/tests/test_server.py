import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any, Dict, List, Tuple

import pytest

from streamstraight_server import ServerOptionsDict, StreamOptionsDict
from streamstraight_server.constants import get_package_version
from streamstraight_server.protocol import (
    ProducerClientToServerEvents,
    ProducerServerToClientEvents,
)
from streamstraight_server.server import StreamstraightServer, StreamstraightServerError


class FakeAsyncClient:
    def __init__(self) -> None:
        self.connected = False
        self.emitted: List[Tuple[str, Dict[str, Any]]] = []
        self.disconnect_calls = 0
        self.connect_args: Dict[str, Any] | None = None
        self._event_handlers: Dict[str, Any] = {}
        self._handlers: Dict[str, List[Any]] = {}

    def event(self, func):
        self._event_handlers[func.__name__] = func
        return func

    def on(self, event: str, handler):
        self._handlers.setdefault(event, []).append(handler)
        return handler

    async def connect(self, url: str, auth, headers):
        self.connected = True
        self.connect_args = {
            "url": url,
            "auth": auth,
            "headers": headers,
        }
        handler = self._event_handlers.get("connect")
        if handler:
            await handler()

    async def emit(self, event: str, payload: Dict[str, Any]):
        self.emitted.append((event, payload))
        if event == ProducerClientToServerEvents.CHUNK:
            await asyncio.sleep(0)
            for handler in self._handlers.get(ProducerServerToClientEvents.ACK, []):
                await handler({"seq": payload["seq"], "redisId": f"redis-{payload['seq']}"})
        if event == ProducerClientToServerEvents.END:
            await asyncio.sleep(0)
            for handler in self._handlers.get(ProducerServerToClientEvents.ACK, []):
                seq = payload.get("lastSeq", 0) + 1
                await handler({"seq": seq, "redisId": payload.get("redisId", f"redis-{seq}")})

    async def disconnect(self):
        self.disconnect_calls += 1
        self.connected = False
        handler = self._event_handlers.get("disconnect")
        if handler:
            await handler()


@pytest.fixture(autouse=True)
def patch_socketio(monkeypatch):
    fake_client = FakeAsyncClient()
    monkeypatch.setattr(
        "streamstraight_server.server.socketio.AsyncClient",
        lambda: fake_client,
    )
    return fake_client


@pytest.mark.asyncio
async def test_connect_uses_auth_headers(patch_socketio):
    fake_client: FakeAsyncClient = patch_socketio
    server = StreamstraightServer(ServerOptionsDict(api_key="abc", base_url="http://example"))
    await server.connect(StreamOptionsDict(stream_id="stream-1"))

    assert fake_client.connect_args is not None
    assert fake_client.connect_args["url"] == "http://example"
    assert fake_client.connect_args["auth"]["streamId"] == "stream-1"
    assert fake_client.connect_args["auth"]["sdkVersion"] == get_package_version()
    assert fake_client.connect_args["headers"]["Authorization"] == "Bearer abc"


@pytest.mark.asyncio
async def test_stream_sends_chunks_and_end(patch_socketio):
    fake_client: FakeAsyncClient = patch_socketio
    server = StreamstraightServer(ServerOptionsDict(api_key="abc"))

    async def generate() -> AsyncIterator[str]:
        yield "first"
        yield "second"

    await server.connect(StreamOptionsDict(stream_id="demo", encoder=lambda value: value))
    await server.stream(generate())

    chunk_events = [
        event for event in fake_client.emitted if event[0] == ProducerClientToServerEvents.CHUNK
    ]
    assert len(chunk_events) == 2

    assert fake_client.emitted[-1][0] == ProducerClientToServerEvents.END
    assert fake_client.disconnect_calls == 1


@pytest.mark.asyncio
async def test_stream_default_encoder_handles_model_dump_json(patch_socketio):
    fake_client: FakeAsyncClient = patch_socketio
    server = StreamstraightServer(ServerOptionsDict(api_key="abc"))

    class DummyModel:
        def __init__(self, text: str) -> None:
            self.text = text

        def model_dump_json(self) -> str:
            return json.dumps({"text": self.text})

    async def generate() -> AsyncIterator[DummyModel]:
        yield DummyModel("hello")

    await server.connect(StreamOptionsDict(stream_id="demo"))
    await server.stream(generate())

    first_event = fake_client.emitted[0]
    assert first_event[0] == ProducerClientToServerEvents.CHUNK
    assert first_event[1]["data"] == json.dumps({"text": "hello"})


@pytest.mark.asyncio
async def test_stream_disconnects_when_source_errors(patch_socketio):
    fake_client: FakeAsyncClient = patch_socketio
    server = StreamstraightServer(ServerOptionsDict(api_key="abc"))

    async def generate() -> AsyncIterator[str]:
        yield "first"
        raise RuntimeError("explode")

    await server.connect(StreamOptionsDict(stream_id="demo", encoder=lambda value: value))

    with pytest.raises(StreamstraightServerError, match="explode"):
        await server.stream(generate())

    assert fake_client.disconnect_calls == 1
    assert fake_client.connected is False


@pytest.mark.asyncio
async def test_stream_writer_context_sends_chunks_and_end(patch_socketio):
    fake_client: FakeAsyncClient = patch_socketio
    server = StreamstraightServer(ServerOptionsDict(api_key="abc"))

    await server.connect(StreamOptionsDict(stream_id="writer", encoder=lambda value: value))

    async with server.stream_writer() as writer:
        ack = await writer.send("hello")
        assert ack is not None
        assert ack["redisId"] == "redis-0"

    chunk_events = [
        event for event in fake_client.emitted if event[0] == ProducerClientToServerEvents.CHUNK
    ]
    assert len(chunk_events) == 1
    assert chunk_events[0][1]["data"] == "hello"

    end_event = fake_client.emitted[-1]
    assert end_event[0] == ProducerClientToServerEvents.END
    assert end_event[1]["reason"] == "completed"

    assert fake_client.disconnect_calls == 1
    assert fake_client.connected is False


@pytest.mark.asyncio
async def test_stream_writer_aborts_on_exception(patch_socketio):
    server = StreamstraightServer(ServerOptionsDict(api_key="abc"))

    await server.connect(StreamOptionsDict(stream_id="writer", encoder=lambda value: value))

    with pytest.raises(RuntimeError, match="boom"):
        async with server.stream_writer() as writer:
            await writer.send("chunk")
            raise RuntimeError("boom")


@pytest.mark.asyncio
async def test_stream_writer_send_after_close_raises(patch_socketio):
    fake_client: FakeAsyncClient = patch_socketio
    server = StreamstraightServer(ServerOptionsDict(api_key="abc"))

    await server.connect(StreamOptionsDict(stream_id="writer", encoder=lambda value: value))

    writer = server.stream_writer()
    await writer.__aenter__()
    await writer.close()

    with pytest.raises(StreamstraightServerError, match="already closed"):
        await writer.send("chunk")

    assert fake_client.disconnect_calls == 1


@pytest.mark.asyncio
async def test_stream_writer_reuses_existing_stream_options(patch_socketio):
    fake_client: FakeAsyncClient = patch_socketio
    server = StreamstraightServer(ServerOptionsDict(api_key="abc"))

    await server.connect(StreamOptionsDict(stream_id="writer", encoder=lambda value: value))

    async with server.stream_writer() as writer:
        await writer.send("chunk")

    chunk_events = [
        event for event in fake_client.emitted if event[0] == ProducerClientToServerEvents.CHUNK
    ]
    assert len(chunk_events) == 1
    assert fake_client.emitted[-1][0] == ProducerClientToServerEvents.END


@pytest.mark.asyncio
async def test_stream_writer_requires_stream_options():
    server = StreamstraightServer(ServerOptionsDict(api_key="abc"))

    with pytest.raises(
        StreamstraightServerError,
        match="stream options not initialized",
    ):
        async with server.stream_writer():
            pass
