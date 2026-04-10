from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)


def main_menu(webapp_url: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Открыть приложение", web_app=WebAppInfo(url=webapp_url))],
            [KeyboardButton(text="Создать заказ в чате")],
        ],
        resize_keyboard=True,
    )


def service_types() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Прохождение квестов")],
            [KeyboardButton(text="Эвенты")],
            [KeyboardButton(text="Арена")],
            [KeyboardButton(text="Прокачка аккаунта")],
            [KeyboardButton(text="Другое")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def order_status_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="В работе",
                    callback_data=f"order:{order_id}:in_progress",
                ),
                InlineKeyboardButton(
                    text="Завершен",
                    callback_data=f"order:{order_id}:done",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Отменен",
                    callback_data=f"order:{order_id}:canceled",
                ),
                InlineKeyboardButton(
                    text="Новый",
                    callback_data=f"order:{order_id}:new",
                ),
            ],
        ]
    )
