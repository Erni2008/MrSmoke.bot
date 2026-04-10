from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def load_env(env_path: str = ".env") -> None:
    path = Path(env_path)
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


@dataclass(slots=True)
class Settings:
    bot_token: str
    admin_ids: list[int]
    db_path: str = "bot.db"
    webapp_url: str = "http://127.0.0.1:8080"
    web_host: str = "127.0.0.1"
    web_port: int = 8080


def get_settings() -> Settings:
    load_env()

    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is not set. Create a .env file based on .env.example.")

    raw_admin_ids = os.getenv("ADMIN_IDS", "")
    admin_ids = [
        int(item.strip())
        for item in raw_admin_ids.split(",")
        if item.strip()
    ]

    if not admin_ids:
        raise RuntimeError("ADMIN_IDS is not set. Add at least one Telegram user ID.")

    render_port = os.getenv("PORT", "").strip()
    default_port = render_port or os.getenv("WEB_PORT", "8080").strip()
    default_host = "0.0.0.0" if render_port else "127.0.0.1"

    webapp_url = os.getenv("WEBAPP_URL", f"http://127.0.0.1:{default_port}").strip()
    web_host = os.getenv("WEB_HOST", default_host).strip()
    web_port = int(default_port)

    return Settings(
        bot_token=token,
        admin_ids=admin_ids,
        webapp_url=webapp_url,
        web_host=web_host,
        web_port=web_port,
    )
