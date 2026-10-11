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


def photos_missing() -> bool:
    """На новом сервере фото товаров ещё не скачаны (в GitHub их нет) — их надо загрузить из канала."""
    return any(p["photos"] and not (settings.DATA_DIR / p["photos"][0]).exists() for p in catalog.products.values())


async def background_update():
    try:
        n = await run_update()
        logging.info("Каталог и фото загружены из канала: %s товаров", n)
    except Exception:
        logging.exception("Не удалось загрузить каталог из канала")


async def main():
    setup_logging()
    bot = create_bot()
    await init_database()
    dp = create_dispatcher()
    webhook = settings.BOT_MODE == "webhook" and bool(settings.SERVER_URL)
    runner = await start_web_server(bot, dp if webhook else None)  # порт открываем сразу — сервер ждёт его
    await set_commands(bot)

    if not catalog.products or photos_missing():
        logging.info("Нет товаров или фото — загружаю из канала в фоне…")
        asyncio.create_task(background_update())

    if settings.webapp_url:  # постоянный адрес (сервер)
        await set_shop_button(bot, settings.webapp_url)
    else:
        # пока туннель поднимается, не показываем кнопку со старым (уже нерабочим) адресом
        await set_shop_button(bot, None)
        if settings.TUNNEL != "off":
            asyncio.create_task(tunnel_supervisor(bot))

    asyncio.create_task(auto_update_loop())
    logging.info("Бот запущен (%s), товаров в каталоге: %s", "webhook" if webhook else "polling", len(catalog.products))
    try:
        if webhook:
            await bot.set_webhook(settings.SERVER_URL + settings.WEBHOOK_PATH, secret_token=settings.WEBHOOK_SECRET,
                                  allowed_updates=dp.resolve_used_update_types())
            await asyncio.Event().wait()  # работаем, пока сервер не остановят
        else:
            await bot.delete_webhook()  # если раньше бот работал на сервере — забираем сообщения себе
            await dp.start_polling(bot)
    finally:
        await runner.cleanup()
        stop_tunnel()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
