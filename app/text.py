from __future__ import annotations


STATUS_LABELS = {
    "new": "Новый",
    "in_progress": "В работе",
    "done": "Завершен",
    "canceled": "Отменен",
}


def format_order(order: dict) -> str:
    username = f"@{order['telegram_username']}" if order.get("telegram_username") else "не указан"
    return (
        f"Заказ #{order['id']}\n"
        f"Статус: {STATUS_LABELS.get(order['status'], order['status'])}\n\n"
        f"Клиент: {order['customer_name']}\n"
        f"Telegram: {username}\n"
        f"Telegram ID: {order['telegram_user_id']}\n"
        f"Услуга: {order['service_type']}\n"
        f"Игровой ник: {order['game_nickname']}\n"
        f"Контакт: {order['contact']}\n"
        f"Срок: {order['deadline']}\n"
        f"Детали: {order['details']}\n"
        f"Создан: {order['created_at']}"
    )
