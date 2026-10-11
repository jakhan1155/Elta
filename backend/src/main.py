"""
Telegram-бот магазина ELTA + мини-приложение (каталог из канала t.me/elta_uz).

Запуск:  python backend/src/main.py   (настройки — backend/.env, см. .env.example)
Обычно запускается сам: scripts/run_bot.ps1 (автозагрузка Windows).
"""
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # папка backend — чтобы работали импорты src.*

from src.config import settings
from src.controllers.admin_controller import auto_update_loop, run_update
from src.core.bot import create_bot, create_dispatcher, set_commands, set_shop_button
from src.core.server import start_web_server
from src.core.tunnel import stop_tunnel, tunnel_supervisor
from src.database import connection as db
from src.database.json_store import carts, langs, orders
from src.models.catalog import catalog
from src.utils.logger import setup_logging


async def init_database() -> None:
    """Neon: заказы, корзины, языки. Недоступна — работаем на локальных файлах, заказы не теряются."""
    if not settings.DATABASE_URL:
        return
    try:
        await db.init(settings.DATABASE_URL, orders.data, carts.data)
        carts.data = await db.load_carts()  # корзины — из базы
        carts.save()
        langs.data = {**langs.data, **await db.load_langs()}
        langs.save()
    except Exception:
        db.pool = None
        logging.exception("Neon недоступна — работаю на локальных файлах")


async def main():
    setup_logging()
    bot = create_bot()
    if not catalog.products:
        logging.info("catalog.json пуст — загружаю товары из канала…")
        await run_update()
    await init_database()
    dp = create_dispatcher()
    await set_commands(bot)
    runner = await start_web_server(bot)

    if settings.webapp_url:  # постоянный адрес (сервер с доменом)
        await set_shop_button(bot, settings.webapp_url)
    else:
        # пока туннель поднимается, не показываем кнопку со старым (уже нерабочим) адресом
        await set_shop_button(bot, None)
        if settings.TUNNEL != "off":
            asyncio.create_task(tunnel_supervisor(bot))

    asyncio.create_task(auto_update_loop())
    logging.info("Бот запущен, товаров в каталоге: %s", len(catalog.products))
    try:
        await dp.start_polling(bot)
    finally:
        await runner.cleanup()
        stop_tunnel()


if __name__ == "__main__":
    asyncio.run(main())
