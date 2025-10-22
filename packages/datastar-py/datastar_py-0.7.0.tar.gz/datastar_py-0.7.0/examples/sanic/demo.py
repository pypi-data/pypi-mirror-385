# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "datastar-py",
#     "jinja2",
#     "sanic[ext]",
# ]
# [tool.uv.sources]
# datastar-py = { path = "../../" }
# ///
import asyncio

from sanic import Sanic, html

from datastar_py.sanic import ServerSentEventGenerator as SSE
from datastar_py.sanic import datastar_response

app = Sanic("test")
import os

print(os.getcwd())

app.static("/static", "./examples/sanic")


@app.before_server_stop
async def before_server_stop(app, loop):
    print("before_server_stop")


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>DataStar Demo</title>
    <script src="/static/datastar.js" type="module"></script>
</head>
<body>
    <div id='foo' data-indicator:connected data-init='@get("/hello", {alwaysReconnect: true, retryInterval: 10000, retryScaler: 2})'
    data-on:datastar-fetch__window='console.log(evt.detail)'></div>
    <div id='bar'>aoeu</div>
    <pre data-json-signals style="background-color: gray;"></pre>
</body>
</html>
"""


@app.get("/")
async def home(request):
    return html(HTML)


@app.get("/hello")
@datastar_response
async def hello(request):
    # raise Exception()
    await asyncio.sleep(1)
    for x in range(5):
        yield SSE.patch_elements(f"<div id='bar'>{x}</div>")
        await asyncio.sleep(1)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, dev=True)
