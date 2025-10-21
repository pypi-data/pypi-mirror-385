# Streamstraight Python SDK

`streamstraight-server` mirrors the `@streamstraight/server` Node SDK for producers who prefer Python. It connects to Streamstraight over Socket.IO, manages chunk acknowledgements, and exposes helpers for minting client JWTs.

## Quickstart

```bash
uv add streamstraight-server
```

## Usage

Streamstraight needs a unique `stream_id` for every stream you produce. Once connected, you can either push chunks manually with the writer API or hand us an async iterator/object that yields JSON‑serializable chunks. The writer reuses the most recent stream configuration, so call `await server.connect({...})` again if you need to swap streams or override the encoder.

### Push chunks with the writer context manager

```python
import asyncio
from collections.abc import AsyncIterator

from streamstraight_server import streamstraight_server


async def generate() -> AsyncIterator[str]:
    yield "first"
    yield "second"


async def main() -> None:
    server = await streamstraight_server(
        {"api_key": "YOUR_STREAMSTRAIGHT_API_KEY"},
        {"stream_id": "your-stream-id"},
    )  # connects and configures the stream

    async with server.stream_writer() as writer:
        async for chunk in generate():
            await writer.send(chunk)
            # You can optionally mirror the same chunks to your HTTP response here.

asyncio.run(main())
```

### Pipe an async iterator directly

```python
import asyncio
from streamstraight_server import streamstraight_server


async def generate():
    # Replace with your LLM or other async generator
    yield {"content": "first chunk"}
    yield {"content": "second chunk"}


async def main() -> None:
    server = await streamstraight_server(
        {"api_key": "YOUR_STREAMSTRAIGHT_API_KEY"},
        {"stream_id": "your-stream-id"},
    )

    await server.stream(generate())

asyncio.run(main())
```

### Mint a client JWT for your browser client

```python
from streamstraight_server import fetch_client_token

token = await fetch_client_token({"api_key": "YOUR_STREAMSTRAIGHT_API_KEY"})
```
