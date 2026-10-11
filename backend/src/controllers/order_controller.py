"""
Приём заказа: сохранить и отправить в группу заказов (из чата и из мини-приложения).
"""
import html
import logging

from aiogram import Bot

from src.config.settings import ORDER_CHAT_ID
from src.models.order import full_name, make_order, save_order
from src.utils.formatting import fmt_money, items_text


async def place_order(bot: Bot, u, name: str, phone: str, address: str, items: list[dict], total: float,
                      comment: str = "", source: str = "чат") -> dict:
    """Сохраняет заказ и отправляет его в группу заказов. u — пользователь Telegram.
    Номер заказа видит только группа, покупателю его не показываем."""
    order = await save_order(make_order(u, name, phone, address, items, total, comment, source))
    if ORDER_CHAT_ID:
        who = f"@{u.username}" if u.username else f'<a href="tg://user?id={u.id}">{html.escape(full_name(u))}</a>'
        note = f"\n💬 {html.escape(comment)}" if comment else ""
        try:
            await bot.send_message(
                ORDER_CHAT_ID,
                f'🆕 <b>Новый заказ №{order["number"]}</b>  ({order["time"]}, {source})\n\n'
                f"{items_text(items)}\n\n💰 <b>Итого: {fmt_money(total)}</b>\n\n"
                f"👤 {html.escape(name)} ({who})\n📱 {html.escape(phone)}\n"
                f"🚚 {html.escape(address)}{note}",
            )
        except Exception:
            # чаще всего бот не добавлен в группу — заказ всё равно сохранён
            logging.exception("Не удалось отправить заказ в ORDER_CHAT_ID=%s", ORDER_CHAT_ID)
    return order
