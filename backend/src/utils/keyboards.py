"""
Шаблоны кнопок бота (тексты — на языке покупателя).
"""
from aiogram import F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from src.config import settings
from src.models.catalog import catalog, price_num
from src.utils.formatting import fmt_money
from src.utils.texts import all_variants, cat_name, t


def is_btn(key: str):
    """Фильтр для кнопки меню на любом языке."""
    return F.text.in_(all_variants(key))


def main_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text=t(lang, "btn_catalog")), KeyboardButton(text=t(lang, "btn_cart"))],
        [KeyboardButton(text=t(lang, "btn_search")), KeyboardButton(text=t(lang, "btn_contacts"))],
        [KeyboardButton(text=t(lang, "btn_lang"))],
    ])


def cancel_kb(lang: str, *rows) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[*rows, [KeyboardButton(text=t(lang, "btn_cancel"))]])


def ikb(rows) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(**b) for b in row] for row in rows if row
    ])


def lang_kb() -> InlineKeyboardMarkup:
    return ikb([[{"text": "🇺🇿 O'zbekcha", "callback_data": "lang:uz"},
                 {"text": "🇷🇺 Русский", "callback_data": "lang:ru"}]])


def shop_button(lang: str, key: str = "shop_open", product_id: int | None = None) -> dict | None:
    if not settings.webapp_url:
        return None
    url = settings.webapp_url + "/?lang=" + lang + (f"&p={product_id}" if product_id else "")
    return {"text": t(lang, key), "web_app": {"url": url}}


def categories_kb(lang: str) -> InlineKeyboardMarkup:
    shop = shop_button(lang, "shop_open_app")
    rows = [[shop]] if shop else []
    for i, cat in enumerate(catalog.categories):
        rows.append([{"text": f"{cat_name(cat, lang)} ({len(catalog.in_category(i))})", "callback_data": f"cat:{i}:0"}])
    rows.append([{"text": t(lang, "new"), "callback_data": "new"}])
    return ikb(rows)


def product_button(p: dict) -> dict:
    return {"text": f'{p["title"][:48]} — {fmt_money(price_num(p))}', "callback_data": f'p:{p["id"]}'}
