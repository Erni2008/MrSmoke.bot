from __future__ import annotations

import html
import json


STATUS_LABELS = {
    "new": "Новый",
    "in_progress": "В работе",
    "done": "Завершен",
    "canceled": "Отменен",
}


def _safe(value: str | None) -> str:
    return html.escape((value or "").strip() or "не указано")


def parse_attachments(order: dict) -> list[dict]:
    raw = order.get("attachments_json") or "[]"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []


def format_order(order: dict) -> str:
    username = f"@{order['telegram_username']}" if order.get("telegram_username") else "не указан"
    attachments_count = len(parse_attachments(order))
    extra = _safe(order.get("details"))

    return (
        f"<b>Заказ #{order['id']}</b>\n"
        f"Статус: {STATUS_LABELS.get(order['status'], order['status'])}\n\n"
        f"<b>Клиент:</b> {_safe(order.get('customer_name'))}\n"
        f"<b>Telegram:</b> {_safe(username)}\n"
        f"<b>Telegram ID:</b> {order['telegram_user_id']}\n"
        f"<b>Тип заявки:</b> {_safe(order.get('service_type'))}\n"
        f"<b>Что пройти:</b> {_safe(order.get('target_content'))}\n"
        f"<b>Инфа по контенту:</b> {_safe(order.get('content_info'))}\n"
        f"<b>Игровой ник:</b> {_safe(order.get('game_nickname'))}\n"
        f"<b>Когда нужно:</b> {_safe(order.get('deadline'))}\n"
        f"<b>Важные факторы:</b> {_safe(order.get('priority_factors'))}\n"
        f"<b>Дополнительно:</b> {extra}\n"
        f"<b>Скрины персов:</b> {attachments_count}\n"
        f"<b>Создан:</b> {_safe(order.get('created_at'))}"
    )
