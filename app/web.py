from __future__ import annotations

from pathlib import Path

from aiohttp import web


def build_web_app() -> web.Application:
    app = web.Application()
    static_dir = Path(__file__).resolve().parent.parent / "webapp"

    async def index(_: web.Request) -> web.FileResponse:
        return web.FileResponse(static_dir / "index.html")

    app.router.add_get("/", index)
    app.router.add_static("/assets/", path=static_dir / "assets", name="assets")
    return app
