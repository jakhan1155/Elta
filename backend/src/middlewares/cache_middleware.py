"""
Мини-приложение: файлы интерфейса (страница, скрипты, стили) браузер Telegram всегда перепроверяет,
чтобы после обновления покупатели сразу видели новую версию. Фото товаров кэшируются как обычно.
"""
from aiohttp import web


@web.middleware
async def no_cache_middleware(request: web.Request, handler):
    resp = await handler(request)
    if request.path == "/" or request.path.startswith("/src/"):
        resp.headers["Cache-Control"] = "no-cache"
    return resp
