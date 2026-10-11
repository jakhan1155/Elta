"""
Каталог в чате: категории, страницы товаров, карточка товара, поиск.
"""
import html

from aiogram import Bot, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from src.config import settings
from src.config.settings import ADMIN_USERNAME, PAGE_SIZE
from src.models.cart import get_cart
from src.models.catalog import catalog, price_num
from src.models.user import lang_of
from src.utils.formatting import fmt_money
from src.utils.keyboards import cancel_kb, categories_kb, ikb, is_btn, main_kb, product_button, shop_button
from src.utils.photos import send_photos
from src.utils.texts import cat_name, t

router = Router(name="catalog")
fallback_router = Router(name="search_fallback")  # подключается последним: любой текст — поиск


class Search(StatesGroup):
    query = State()


def catalog_text(lang: str) -> str:
    return t(lang, "catalog_title", n=len(catalog.products))


def category_page(idx: int, page: int, lang: str) -> tuple[str, InlineKeyboardMarkup]:
    items = catalog.in_category(idx)
    pages = max(1, (len(items) + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(0, min(page, pages - 1))
    chunk = items[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]
    rows = [[product_button(p)] for p in chunk]
    nav = []
    if page > 0:
        nav.append({"text": "◀️", "callback_data": f"cat:{idx}:{page - 1}"})
    if pages > 1:
        nav.append({"text": f"{page + 1}/{pages}", "callback_data": "noop"})
    if page < pages - 1:
        nav.append({"text": "▶️", "callback_data": f"cat:{idx}:{page + 1}"})
    rows.append(nav)
    rows.append([{"text": t(lang, "all_cats"), "callback_data": "cats"}])
    title = html.escape(cat_name(catalog.categories[idx], lang))
    return f"<b>{title}</b>\n{t(lang, 'choose_product')}", ikb(rows)


def product_card(p: dict, user_id: int, lang: str) -> tuple[str, InlineKeyboardMarkup]:
    art = f'\n{t(lang, "article")}: <code>{html.escape(p["article"])}</code>' if p.get("article") else ""
    desc = html.escape(p["description"])
    text = (f'<b>{html.escape(p["title"])}</b>{art}\n\n{desc}\n\n'
            f'<b>{t(lang, "price")}: {fmt_money(price_num(p))}</b>')
    if len(text) > 4000:
        text = text[:3990] + "…"
    qty = get_cart(user_id).get(str(p["id"]), 0)
    cat_idx = catalog.categories.index(p["category"]) if p["category"] in catalog.categories else None
    rows = [
        [{"text": t(lang, "add_cart") + (t(lang, "in_cart", n=qty) if qty else ""), "callback_data": f'add:{p["id"]}'}],
        [{"text": t(lang, "buy_now"), "callback_data": f'buy:{p["id"]}'}],
        [shop_button(lang, "open_in_shop", p["id"])] if settings.webapp_url else [],
        [{"text": t(lang, "ask_manager"), "url": f"https://t.me/{ADMIN_USERNAME}"},
         {"text": t(lang, "channel_post"), "url": p["post_url"]}],
        [{"text": t(lang, "back"), "callback_data": f"cat:{cat_idx}:0" if cat_idx is not None else "cats"}],
    ]
    return text, ikb(rows)


async def show_product(bot: Bot, chat_id: int, user, pid: int):
    lang = lang_of(user)
    p = catalog.products.get(pid)
    if not p:
        await bot.send_message(chat_id, t(lang, "item_gone"))
        return
    await send_photos(bot, chat_id, p)
    text, kb = product_card(p, user.id, lang)
    await bot.send_message(chat_id, text, reply_markup=kb)


@router.message(is_btn("btn_catalog"))
@router.message(Command("catalog"))
async def show_catalog(m: Message, state: FSMContext):
    await state.clear()
    lang = lang_of(m.from_user)
    if not catalog.products:
        await m.answer(t(lang, "catalog_empty"))
        return
    await m.answer(catalog_text(lang), reply_markup=categories_kb(lang))


@router.message(is_btn("btn_search"))
async def search_start(m: Message, state: FSMContext):
    await state.set_state(Search.query)
    lang = lang_of(m.from_user)
    await m.answer(t(lang, "search_prompt"), reply_markup=cancel_kb(lang))


async def do_search(m: Message, query: str):
    lang = lang_of(m.from_user)
    found = catalog.search(query)
    if not found:
        await m.answer(t(lang, "not_found", q=html.escape(query), m=ADMIN_USERNAME), reply_markup=main_kb(lang))
        return
    rows = [[product_button(p)] for p in found[:20]]
    await m.answer(t(lang, "found", n=len(found)), reply_markup=main_kb(lang))
    await m.answer(t(lang, "choose_product"), reply_markup=ikb(rows))


@router.message(Search.query, F.text)
async def search_query(m: Message, state: FSMContext):
    await state.clear()
    await do_search(m, m.text)


@router.callback_query(F.data == "noop")
async def noop(c: CallbackQuery):
    await c.answer()


@router.callback_query(F.data == "cats")
async def cb_cats(c: CallbackQuery):
    lang = lang_of(c.from_user)
    await c.message.edit_text(catalog_text(lang), reply_markup=categories_kb(lang))
    await c.answer()


@router.callback_query(F.data == "new")
async def cb_new(c: CallbackQuery):
    lang = lang_of(c.from_user)
    newest = sorted(catalog.products.values(), key=lambda p: -p["id"])[:PAGE_SIZE]
    rows = [[product_button(p)] for p in newest] + [[{"text": t(lang, "all_cats"), "callback_data": "cats"}]]
    await c.message.edit_text(f"<b>{t(lang, 'new')}</b>", reply_markup=ikb(rows))
    await c.answer()


@router.callback_query(F.data.startswith("cat:"))
async def cb_category(c: CallbackQuery):
    lang = lang_of(c.from_user)
    _, idx, page = c.data.split(":")
    idx = int(idx)
    if idx >= len(catalog.categories):
        await c.answer(t(lang, "catalog_changed"), show_alert=True)
        return
    text, kb = category_page(idx, int(page), lang)
    await c.message.edit_text(text, reply_markup=kb)
    await c.answer()


@router.callback_query(F.data.startswith("p:"))
async def cb_product(c: CallbackQuery):
    await c.answer()
    await show_product(c.bot, c.message.chat.id, c.from_user, int(c.data[2:]))


# Любой другой текст — считаем поисковым запросом
@fallback_router.message(StateFilter(None), F.text & ~F.text.startswith("/"))
async def free_text(m: Message):
    await do_search(m, m.text)
