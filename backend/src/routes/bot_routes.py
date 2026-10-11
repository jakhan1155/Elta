"""
Все обработчики бота в одном месте. Порядок важен: кнопки меню — раньше шагов оформления заказа,
«любой текст = поиск» — самым последним.
"""
from aiogram import Dispatcher

from src.controllers import admin_controller, cart_controller, catalog_controller, checkout_controller, start_controller


def setup_bot_routes(dp: Dispatcher) -> None:
    dp.include_routers(
        start_controller.router,          # /start, язык, отмена, контакты
        cart_controller.router,           # корзина
        catalog_controller.router,        # каталог, карточка товара, поиск
        checkout_controller.router,       # оформление заказа
        admin_controller.router,          # /update, /orders, /admin
        catalog_controller.fallback_router,  # любой другой текст — поиск
    )
