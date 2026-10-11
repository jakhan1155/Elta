"""
Корзина в чате: просмотр, добавление, + / −, очистка.
"""
import html

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from src.controllers.catalog_controller import product_card
from src.models.cart import change_qty, clear_cart, get_cart
from src.models.catalog import catalog, price_num
from src.models.user import lang_of
from src.utils.formatting import fmt_money
from src.utils.keyboards import ikb, is_btn
from src.utils.texts import t

router = Router(name="cart")


def cart_view(user_id: int, lang: str) -> tuple[str, InlineKeyboardMarkup | None]:
    cart = {k: v for k, v in get_cart(user_id).items() if int(k) in catalog.products}  # товар могли убрать
    if not cart:
        return t(lang, "cart_empty"), None
    lines, rows, total = [t(lang, "cart_title")], [], 0.0
    for n, (pid, qty) in enumerate(cart.items(), 1):
        p = catalog.products[int(pid)]
        s = price_num(p) * qty
        total += s
        lines.append(f'{n}. {html.escape(p["title"])}\n    {qty} × {fmt_money(price_num(p))} = <b>{fmt_money(s)}</b>')
        rows.append([{"text": "➖", "callback_data": f"dec:{pid}"},
                     {"text": f'{p["title"][:22]} ×{qty}', "callback_data": f"p:{pid}"},
                     {"text": "➕", "callback_data": f"inc:{pid}"}])
    lines.append(f"\n💰 <b>{t(lang, 'total')}: {fmt_money(total)}</b>")
    rows.append([{"text": t(lang, "clear"), "callback_data": "clear"},
                 {"text": t(lang, "checkout"), "callback_data": "checkout"}])
    return "\n".join(lines), ikb(rows)


@router.message(is_btn("btn_cart"))
@router.message(Command("cart"))
async def show_cart(m: Message, state: FSMContext):
    await state.clear()
    text, kb = cart_view(m.from_user.id, lang_of(m.from_user))
    await m.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("add:"))
async def cb_add(c: CallbackQuery):
    lang = lang_of(c.from_user)
    pid = c.data[4:]
    if int(pid) not in catalog.products:
        await c.answer(t(lang, "item_gone"), show_alert=True)
        return
    qty = change_qty(c.from_user.id, pid, +1)
    await c.answer(t(lang, "added", n=qty))
    text, kb = product_card(catalog.products[int(pid)], c.from_user.id, lang)
    try:
        await c.message.edit_reply_markup(reply_markup=kb)
    except Exception:
        pass


@router.callback_query(F.data.startswith(("inc:", "dec:")))
async def cb_qty(c: CallbackQuery):
    change_qty(c.from_user.id, c.data[4:], +1 if c.data.startswith("inc") else -1)
    text, kb = cart_view(c.from_user.id, lang_of(c.from_user))
    await c.message.edit_text(text, reply_markup=kb)
    await c.answer()


@router.callback_query(F.data == "clear")
async def cb_clear(c: CallbackQuery):
    clear_cart(c.from_user.id)
    await c.message.edit_text(t(lang_of(c.from_user), "cart_cleared"))
    await c.answer()
