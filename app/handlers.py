from __future__ import annotations

import json

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from app import db
from app.keyboards import main_menu, order_status_keyboard, service_types
from app.states import OrderForm
from app.text import STATUS_LABELS, format_order


def build_router(settings) -> Router:
    router = Router()

    @router.message(CommandStart())
    async def start_handler(message: Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer(
            "Бот принимает заказы по Marvel Contest of Champions.\n"
            "Открой мини-приложение для нормальной формы заказа или используй чат-режим.",
            reply_markup=main_menu(settings.webapp_url),
        )

    @router.message(F.web_app_data)
    async def process_web_app_order(message: Message, state: FSMContext) -> None:
        await state.clear()
        data = json.loads(message.web_app_data.data)

        order_id = db.create_order(
            settings.db_path,
            {
                "telegram_user_id": message.from_user.id,
                "telegram_username": message.from_user.username,
                "customer_name": data["customer_name"],
                "service_type": data["service_type"],
                "game_nickname": data["game_nickname"],
                "contact": data["contact"],
                "deadline": data["deadline"],
                "details": data["details"],
                "status": "new",
            },
        )
        order = db.get_order(settings.db_path, order_id)

        await message.answer(
            f"Заказ #{order_id} принят через приложение. Администратор получил уведомление.",
            reply_markup=main_menu(settings.webapp_url),
        )

        for admin_id in settings.admin_ids:
            await message.bot.send_message(
                admin_id,
                format_order(order),
                reply_markup=order_status_keyboard(order_id),
            )

    @router.message(F.text == "Создать заказ в чате")
    async def create_order_start(message: Message, state: FSMContext) -> None:
        await state.clear()
        await state.set_state(OrderForm.customer_name)
        await message.answer(
            "Как к вам обращаться?",
            reply_markup=ReplyKeyboardRemove(),
        )

    @router.message(OrderForm.customer_name)
    async def process_customer_name(message: Message, state: FSMContext) -> None:
        await state.update_data(customer_name=message.text.strip())
        await state.set_state(OrderForm.service_type)
        await message.answer(
            "Выберите тип услуги:",
            reply_markup=service_types(),
        )

    @router.message(OrderForm.service_type)
    async def process_service_type(message: Message, state: FSMContext) -> None:
        await state.update_data(service_type=message.text.strip())
        await state.set_state(OrderForm.game_nickname)
        await message.answer(
            "Введите игровой ник в Marvel Contest of Champions:",
            reply_markup=ReplyKeyboardRemove(),
        )

    @router.message(OrderForm.game_nickname)
    async def process_game_nickname(message: Message, state: FSMContext) -> None:
        await state.update_data(game_nickname=message.text.strip())
        await state.set_state(OrderForm.contact)
        await message.answer("Оставьте контакт для связи: Telegram / Discord / WhatsApp и т.д.")

    @router.message(OrderForm.contact)
    async def process_contact(message: Message, state: FSMContext) -> None:
        await state.update_data(contact=message.text.strip())
        await state.set_state(OrderForm.deadline)
        await message.answer("Какой срок выполнения нужен?")

    @router.message(OrderForm.deadline)
    async def process_deadline(message: Message, state: FSMContext) -> None:
        await state.update_data(deadline=message.text.strip())
        await state.set_state(OrderForm.details)
        await message.answer("Опишите заказ подробнее: что именно нужно сделать?")

    @router.message(OrderForm.details)
    async def process_details(message: Message, state: FSMContext) -> None:
        await state.update_data(details=message.text.strip())
        data = await state.get_data()

        order_id = db.create_order(
            settings.db_path,
            {
                "telegram_user_id": message.from_user.id,
                "telegram_username": message.from_user.username,
                "customer_name": data["customer_name"],
                "service_type": data["service_type"],
                "game_nickname": data["game_nickname"],
                "contact": data["contact"],
                "deadline": data["deadline"],
                "details": data["details"],
                "status": "new",
            },
        )
        order = db.get_order(settings.db_path, order_id)
        await state.clear()

        await message.answer(
            f"Заказ #{order_id} принят. Администратор получил уведомление.",
            reply_markup=main_menu(settings.webapp_url),
        )

        for admin_id in settings.admin_ids:
            await message.bot.send_message(
                admin_id,
                format_order(order),
                reply_markup=order_status_keyboard(order_id),
            )

    @router.callback_query(F.data.startswith("order:"))
    async def process_order_status(callback: CallbackQuery) -> None:
        if callback.from_user.id not in settings.admin_ids:
            await callback.answer("Недостаточно прав.", show_alert=True)
            return

        _, raw_order_id, status = callback.data.split(":", 2)
        order_id = int(raw_order_id)

        updated = db.update_order_status(settings.db_path, order_id, status)
        if not updated:
            await callback.answer("Заказ не найден.", show_alert=True)
            return

        order = db.get_order(settings.db_path, order_id)
        await callback.message.edit_text(
            format_order(order),
            reply_markup=order_status_keyboard(order_id),
        )
        await callback.answer(f"Статус изменен: {STATUS_LABELS.get(status, status)}")

    return router
