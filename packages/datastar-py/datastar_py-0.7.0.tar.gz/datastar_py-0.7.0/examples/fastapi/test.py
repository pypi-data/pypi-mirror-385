import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

import nats
import uvicorn
from datastar_py.consts import ElementPatchMode
from datastar_py.starlette import datastar_response
from fastapi import FastAPI
from starlette.responses import HTMLResponse
from htpy import body, head, html, title, script, p, div
from datastar_py import ServerSentEventGenerator as SSE

nc = None


@asynccontextmanager
async def lifecycle(app):
    print("lifecycle")
    global nc
    nc = await nats.connect("nats://127.0.0.1:4222")
    try:
        yield
    finally:
        await nc.close()


app = FastAPI(lifespan=lifecycle)


@app.get("/")
async def read_root():
    return HTMLResponse(
        html[
            head[
                script(
                    type="module",
                    src="https://cdn.jsdelivr.net/gh/starfederation/datastar@main/bundles/datastar.js",
                ),
                title["Hello there"],
            ],
            body[
                p(data_on_load='@get("/updates")'),
                p(data_on_click="@get('/foo')")["Connects on page load. Click to get /foo"],
                div(id="messages"),
                div(id="notes"),
            ],
        ]
    )


@app.get("/foo")
@datastar_response
async def foo():
    now = datetime.now().isoformat()
    # yield SSE.patch_elements("<p>ping</p>", selector="#notes", mode=ElementPatchMode.INNER)
    print("pre published")
    await nc.publish("patch", b"<p>FROM /FOO</p>")
    print("published")
    # yield SSE.patch_elements("<p>pong</p>", selector="#notes", mode=ElementPatchMode.INNER)


@app.get("/updates")
@datastar_response
async def updates():
    sub = await nc.subscribe("patch")
    print("subscribed to updates")
    print("before async for")
    async for msg in sub.messages:
        print(f"Received: {msg = }")
        data = msg.data.decode()
        print(f"Received: {data = }")
        yield SSE.patch_elements(data, selector="#messages", mode=ElementPatchMode.APPEND).encode()
    print("End of code")


async def main() -> None:
    nc = await nats.connect("nats://127.0.0.1:4222")
    sub = await nc.subscribe("patch")
    await nc.publish("patch", b"<p>thing</p>")
    async for msg in sub.messages:
        print(f"Received: {msg = }")


if __name__ == "__main__":
    uvicorn.run(app)
    # asyncio.run(main())
