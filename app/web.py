from __future__ import annotations

import asyncio
from pathlib import Path
from uuid import uuid4

from aiohttp import web


def build_web_app(settings) -> web.Application:
    app = web.Application(client_max_size=15 * 1024 * 1024)
    static_dir = Path(__file__).resolve().parent.parent / "webapp"
    upload_dir = Path(__file__).resolve().parent.parent / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    async def index(_: web.Request) -> web.FileResponse:
        return web.FileResponse(static_dir / "index.html")

    async def health(_: web.Request) -> web.Response:
        return web.json_response({"status": "ok"})

    async def favicon(_: web.Request) -> web.Response:
        return web.Response(status=204)

    async def upload(request: web.Request) -> web.Response:
        reader = await request.multipart()
        field = await reader.next()

        if field is None or field.name != "file":
            raise web.HTTPBadRequest(text="file field is required")

        content_type = (field.headers.get("Content-Type") or "").lower()
        if not content_type.startswith("image/"):
            raise web.HTTPBadRequest(text="only image uploads are allowed")

        suffix = Path(field.filename or "").suffix or ".jpg"
        filename = f"{uuid4().hex}{suffix}"
        destination = upload_dir / filename

        size = 0
        with destination.open("wb") as file_handle:
            while True:
                chunk = await field.read_chunk()
                if not chunk:
                    break
                size += len(chunk)
                if size > 10 * 1024 * 1024:
                    destination.unlink(missing_ok=True)
                    raise web.HTTPBadRequest(text="file is too large")
                file_handle.write(chunk)

        await asyncio.sleep(0)
        return web.json_response(
            {
                "url": f"{settings.webapp_url.rstrip('/')}/uploads/{filename}",
                "filename": filename,
            }
        )

    async def spa_fallback(request: web.Request) -> web.StreamResponse:
        if request.path.startswith("/assets/") or request.path.startswith("/uploads/"):
            raise web.HTTPNotFound()
        return web.FileResponse(static_dir / "index.html")

    app.router.add_get("/", index)
    app.router.add_get("/healthz", health)
    app.router.add_get("/favicon.ico", favicon)
    app.router.add_post("/api/upload", upload)
    app.router.add_static("/assets/", path=static_dir / "assets", name="assets")
    app.router.add_static("/uploads/", path=upload_dir, name="uploads")
    app.router.add_get("/{tail:.*}", spa_fallback)
    return app
