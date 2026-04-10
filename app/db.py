from __future__ import annotations

import json
import sqlite3
from contextlib import closing


def _ensure_column(connection: sqlite3.Connection, column: str, definition: str) -> None:
    existing_columns = {
        row[1]
        for row in connection.execute("PRAGMA table_info(orders)")
    }
    if column not in existing_columns:
        connection.execute(f"ALTER TABLE orders ADD COLUMN {column} {definition}")


def init_db(db_path: str) -> None:
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_user_id INTEGER NOT NULL,
                telegram_username TEXT,
                customer_name TEXT NOT NULL,
                service_type TEXT NOT NULL,
                game_nickname TEXT NOT NULL,
                contact TEXT NOT NULL,
                deadline TEXT NOT NULL,
                details TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        _ensure_column(connection, "target_content", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(connection, "content_info", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(connection, "priority_factors", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(connection, "attachments_json", "TEXT NOT NULL DEFAULT '[]'")
        connection.commit()


def create_order(db_path: str, payload: dict) -> int:
    attachments_json = json.dumps(payload.get("attachments", []), ensure_ascii=False)

    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO orders (
                telegram_user_id,
                telegram_username,
                customer_name,
                service_type,
                game_nickname,
                contact,
                deadline,
                details,
                target_content,
                content_info,
                priority_factors,
                attachments_json,
                status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["telegram_user_id"],
                payload.get("telegram_username"),
                payload["customer_name"],
                payload["service_type"],
                payload["game_nickname"],
                payload["contact"],
                payload["deadline"],
                payload.get("details", ""),
                payload.get("target_content", ""),
                payload.get("content_info", ""),
                payload.get("priority_factors", ""),
                attachments_json,
                payload.get("status", "new"),
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)


def get_order(db_path: str, order_id: int) -> dict | None:
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        with closing(
            connection.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        ) as cursor:
            row = cursor.fetchone()
            return dict(row) if row else None


def update_order_status(db_path: str, order_id: int, status: str) -> bool:
    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            (status, order_id),
        )
        connection.commit()
        return cursor.rowcount > 0
