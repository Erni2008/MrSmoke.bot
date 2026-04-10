from __future__ import annotations

from pathlib import Path

from aiohttp import web


def build_web_app() -> web.Application:
    app = web.Application()
    static_dir = Path(__file__).resolve().parent.parent / "webapp"

    async def index(_: web.Request) -> web.FileResponse:
        return web.FileResponse(static_dir / "index.html")

    async def health(_: web.Request) -> web.Response:
        return web.json_response({"status": "ok"})

    async def favicon(_: web.Request) -> web.Response:
        return web.Response(status=204)

    async def spa_fallback(request: web.Request) -> web.StreamResponse:
        if request.path.startswith("/assets/"):
            raise web.HTTPNotFound()
        return web.FileResponse(static_dir / "index.html")

    app.router.add_get("/", index)
    app.router.add_get("/healthz", health)
    app.router.add_get("/favicon.ico", favicon)
    app.router.add_static("/assets/", path=static_dir / "assets", name="assets")
    app.router.add_get("/{tail:.*}", spa_fallback)
    return app
