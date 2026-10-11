"""
Отмечает, что покупатель пользовался ботом сегодня (для /stats). Только личные чаты, не группа заказов.
"""
from aiogram import BaseMiddleware

from src.models.visit import record_visit


class ActivityMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = data.get("event_from_user")
        chat = data.get("event_chat")
        if user and chat and chat.type == "private":
            record_visit(user.id, "bot")
        return await handler(event, data)
