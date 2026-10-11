"""
Проверки доступа: администратор бота и подпись Telegram у запросов из мини-приложения.
"""
import time

from aiogram.types import Message
from aiogram.utils.web_app import WebAppUser, safe_parse_webapp_init_data

from src.config.settings import ADMIN_IDS, BOT_TOKEN


def is_admin(m: Message) -> bool:
    return m.from_user.id in ADMIN_IDS


def webapp_user(init_data: str) -> tuple[WebAppUser | None, str | None]:
    """Покупатель из initData мини-приложения → (user, None) или (None, ключ текста ошибки).
    Подпись проверяется токеном бота: заказ можно отправить только из настоящего окна бота."""
    try:
        init = safe_parse_webapp_init_data(BOT_TOKEN, init_data)
    except ValueError:
        return None, "err_auth"
    if not init.user:
        return None, "err_open_bot"
    if time.time() - init.auth_date.timestamp() > 24 * 3600:
        return None, "err_session"
    return init.user, None
