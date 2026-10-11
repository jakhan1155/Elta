"""
Адреса веб-сервера мини-приложения.
"""
from aiohttp import web

from src.config.settings import FRONTEND_DIR, PHOTOS_DIR
from src.controllers import webapp_controller as wc


def setup_web_routes(app: web.Application) -> None:
    app.router.add_get("/", wc.web_index)
    app.router.add_get("/health", wc.web_health)  # проверка сервером, что бот жив
    app.router.add_get("/api/catalog", wc.web_catalog)
    app.router.add_post("/api/order", wc.web_order)
    app.router.add_post("/api/lang", wc.web_lang)
    app.router.add_static("/src/", FRONTEND_DIR / "src")                 # скрипты и стили магазина
    app.router.add_static("/images/", FRONTEND_DIR / "public" / "images")  # логотип, круги категорий
    app.router.add_static("/photos/", PHOTOS_DIR)                        # фото товаров из канала
