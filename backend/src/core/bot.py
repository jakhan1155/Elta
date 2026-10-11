"""
Создание бота и диспетчера, команды и кнопка «Магазин» в меню.
"""
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand, MenuButtonCommands, MenuButtonWebApp, WebAppInfo

from src.config.settings import BOT_TOKEN
from src.middlewares.activity_middleware import ActivityMiddleware
from src.routes.bot_routes import setup_bot_routes


def create_bot() -> Bot:
    if not BOT_TOKEN:
        raise SystemExit("Укажите BOT_TOKEN в файле backend/.env (см. .env.example)")
    return Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.message.outer_middleware(ActivityMiddleware())
    dp.callback_query.outer_middleware(ActivityMiddleware())
    setup_bot_routes(dp)
    return dp


async def set_commands(bot: Bot) -> None:
    try:
        await bot.set_my_commands([BotCommand(command="start", description="Boshlash / Начать"),
                                   BotCommand(command="til", description="Tilni o'zgartirish / Сменить язык")])
    except Exception:
        logging.exception("Не удалось установить команды бота")


async def set_shop_button(bot: Bot, url: str | None) -> None:
    """Кнопка «🛍 Магазин» слева от поля ввода; без адреса — обычное меню команд."""
    if url:
        await bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text="🛍 Магазин", web_app=WebAppInfo(url=url + "/")))
        logging.info("Кнопка «Магазин» → %s", url)
    else:
        await bot.set_chat_menu_button(menu_button=MenuButtonCommands())
