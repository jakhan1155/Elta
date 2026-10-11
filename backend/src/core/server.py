"""
Веб-сервер мини-приложения (aiohttp) внутри процесса бота.
В режиме webhook сюда же Telegram присылает сообщения боту.
"""
import logging

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web

from src.config.settings import WEB_HOST, WEB_PORT, WEBHOOK_PATH, WEBHOOK_SECRET
from src.middlewares.cache_middleware import no_cache_middleware
from src.routes.web_routes import setup_web_routes


def create_web_app(bot: Bot, dp: Dispatcher | None = None) -> web.Application:
    app = web.Application(client_max_size=64 * 1024, middlewares=[no_cache_middleware])
    app["bot"] = bot
    setup_web_routes(app)
    if dp:  # webhook: принимаем только запросы с секретом, который знает Telegram
        SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET).register(app, path=WEBHOOK_PATH)
    return app


async def start_web_server(bot: Bot, dp: Dispatcher | None = None) -> web.AppRunner:
    runner = web.AppRunner(create_web_app(bot, dp), access_log=None)
    await runner.setup()
    await web.TCPSite(runner, WEB_HOST, WEB_PORT).start()
    logging.info("Веб-сервер: http://%s:%s", WEB_HOST, WEB_PORT)
    return runner
