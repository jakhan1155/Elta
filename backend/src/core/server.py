"""
Веб-сервер мини-приложения (aiohttp) внутри процесса бота.
"""
import logging

from aiogram import Bot
from aiohttp import web

from src.config.settings import WEB_HOST, WEB_PORT
from src.middlewares.cache_middleware import no_cache_middleware
from src.routes.web_routes import setup_web_routes


def create_web_app(bot: Bot) -> web.Application:
    app = web.Application(client_max_size=64 * 1024, middlewares=[no_cache_middleware])
    app["bot"] = bot
    setup_web_routes(app)
    return app


async def start_web_server(bot: Bot) -> web.AppRunner:
    runner = web.AppRunner(create_web_app(bot), access_log=None)
    await runner.setup()
    await web.TCPSite(runner, WEB_HOST, WEB_PORT).start()
    logging.info("Мини-приложение: http://127.0.0.1:%s", WEB_PORT)
    return runner
