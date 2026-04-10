from __future__ import annotations

import json

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from app import db
from app.keyboards import main_menu, order_status_keyboard, service_types
from app.states import OrderForm
from app.text import STATUS_LABELS, format_order, parse_attachments


def _build_order_payload(message: Message, data: dict, attachments: list[dict] | None = None) -> dict:
    username = f"@{message.from_user.username}" if message.from_user.username else ""

    return {
        "telegram_user_id": message.from_user.id,
        "telegram_username": message.from_user.username,
        "customer_name": message.from_user.full_name,
        "service_type": data["service_type"],
        "target_content": data["target_content"],
        "content_info": data["content_info"],
        "game_nickname": data["game_nickname"],
        "contact": username or str(message.from_user.id),
        "deadline": data["deadline"],
        "priority_factors": data["priority_factors"],
        "details": data.get("details", ""),
        "attachments": attachments or data.get("attachments", []),
        "status": "new",
    }


async def _notify_admins(message: Message, settings, order: dict) -> None:
    attachments = parse_attachments(order)

    for admin_id in settings.admin_ids:
        await message.bot.send_message(
            admin_id,
            format_order(order),
            reply_markup=order_status_keyboard(order["id"]),
        )
        for attachment in attachments[:10]:
            url = attachment.get("url")
            if url:
                await message.bot.send_photo(admin_id, photo=url)


def build_router(settings) -> Router:
    router = Router()

    @router.message(CommandStart())
    async def start_handler(message: Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer(
            "Открой приложение и оформи заказ по контенту MCOC. "
            "Если надо, можно заполнить форму и в чат-режиме.",
            reply_markup=main_menu(settings.webapp_url),
        )

    @router.message(F.web_app_data)
    async def process_web_app_order(message: Message, state: FSMContext) -> None:
        await state.clear()
        data = json.loads(message.web_app_data.data)
        payload = _build_order_payload(
            message,
            {
                "service_type": data["service_type"],
                "target_content": data["target_content"],
                "content_info": data["content_info"],
                "game_nickname": data["game_nickname"],
                "deadline": data["deadline"],
                "priority_factors": data["priority_factors"],
                "details": data.get("details", ""),
                "attachments": data.get("attachments", []),
            },
        )

        order_id = db.create_order(settings.db_path, payload)
        order = db.get_order(settings.db_path, order_id)

        await message.answer(
            f"Заказ #{order_id} отправлен. Скрины и условия переданы администратору.",
            reply_markup=main_menu(settings.webapp_url),
        )
        await _notify_admins(message, settings, order)

    @router.message(F.text == "Создать заказ в чате")
    async def create_order_start(message: Message, state: FSMContext) -> None:
        await state.clear()
        await state.set_state(OrderForm.service_type)
        await message.answer(
            "Выберите тип заявки:",
            reply_markup=service_types(),
        )

    @router.message(OrderForm.service_type)
    async def process_service_type(message: Message, state: FSMContext) -> None:
        await state.update_data(service_type=message.text.strip())
        await state.set_state(OrderForm.target_content)
        await message.answer(
            "Что именно нужно пройти?",
            reply_markup=ReplyKeyboardRemove(),
        )

    @router.message(OrderForm.target_content)
    async def process_target_content(message: Message, state: FSMContext) -> None:
        await state.update_data(target_content=message.text.strip())
        await state.set_state(OrderForm.content_info)
        await message.answer("Напиши информацию по контенту: акт, квест, путь, условия, ограничения.")

    @router.message(OrderForm.content_info)
    async def process_content_info(message: Message, state: FSMContext) -> None:
        await state.update_data(content_info=message.text.strip())
        await state.set_state(OrderForm.game_nickname)
        await message.answer("Укажи игровой ник или ID аккаунта.")

    @router.message(OrderForm.game_nickname)
    async def process_game_nickname(message: Message, state: FSMContext) -> None:
        await state.update_data(game_nickname=message.text.strip())
        await state.set_state(OrderForm.deadline)
        await message.answer("Когда это нужно сделать?")

    @router.message(OrderForm.deadline)
    async def process_deadline(message: Message, state: FSMContext) -> None:
        await state.update_data(deadline=message.text.strip())
        await state.set_state(OrderForm.priority_factors)
        await message.answer("Укажи важные факторы: лимиты, ревивы, бюджет, запреты, предпочтения.")

    @router.message(OrderForm.priority_factors)
    async def process_priority_factors(message: Message, state: FSMContext) -> None:
        await state.update_data(priority_factors=message.text.strip())
        await state.set_state(OrderForm.details)
        await message.answer(
            "Если есть что-то еще важное, напиши. "
            "Скрины персов после заявки можешь прислать отдельными сообщениями админу."
        )

    @router.message(OrderForm.details)
    async def process_details(message: Message, state: FSMContext) -> None:
        await state.update_data(details=message.text.strip())
        data = await state.get_data()
        payload = _build_order_payload(message, data)

        order_id = db.create_order(settings.db_path, payload)
        order = db.get_order(settings.db_path, order_id)
        await state.clear()

        await message.answer(
            f"Заказ #{order_id} принят. Если нужно, отдельно пришли скрины персов в чат администратору.",
            reply_markup=main_menu(settings.webapp_url),
        )
        await _notify_admins(message, settings, order)

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
