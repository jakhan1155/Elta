"""
Оформление заказа в чате: имя → телефон → адрес → подтверждение.
"""
import html

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, KeyboardButton, Message, ReplyKeyboardRemove

from src.controllers.order_controller import place_order
from src.models.cart import change_qty, clear_cart, get_cart, order_summary
from src.models.catalog import catalog
from src.models.user import lang_of
from src.utils.formatting import fmt_money, items_text
from src.utils.keyboards import cancel_kb, ikb, main_kb
from src.utils.texts import all_variants, t

router = Router(name="checkout")


class Checkout(StatesGroup):
    name = State()
    phone = State()
    address = State()
    confirm = State()


@router.callback_query(F.data.startswith("buy:"))
async def cb_buy(c: CallbackQuery, state: FSMContext):
    pid = c.data[4:]
    if int(pid) not in catalog.products:
        await c.answer(t(lang_of(c.from_user), "item_gone"), show_alert=True)
        return
    if not get_cart(c.from_user.id).get(pid):
        change_qty(c.from_user.id, pid, +1)
    await begin_checkout(c, state)


@router.callback_query(F.data == "checkout")
async def begin_checkout(c: CallbackQuery, state: FSMContext):
    lang = lang_of(c.from_user)
    if not get_cart(c.from_user.id):
        await c.answer(t(lang, "cart_empty_short"), show_alert=True)
        return
    await c.answer()
    data = await state.get_data()
    await state.set_state(Checkout.name)
    name_hint = data.get("name") or c.from_user.full_name
    await c.message.answer(t(lang, "co_name"), reply_markup=cancel_kb(lang, [KeyboardButton(text=name_hint[:60])]))


@router.message(Checkout.name, F.text)
async def co_name(m: Message, state: FSMContext):
    lang = lang_of(m.from_user)
    await state.update_data(name=m.text.strip()[:100])
    await state.set_state(Checkout.phone)
    await m.answer(t(lang, "co_phone"), reply_markup=cancel_kb(
        lang, [KeyboardButton(text=t(lang, "send_my_number"), request_contact=True)]))


@router.message(Checkout.phone, F.contact | F.text)
async def co_phone(m: Message, state: FSMContext):
    lang = lang_of(m.from_user)
    phone = m.contact.phone_number if m.contact else m.text.strip()
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) < 9:
        await m.answer(t(lang, "bad_phone"))
        return
    await state.update_data(phone=phone)
    await state.set_state(Checkout.address)
    await m.answer(t(lang, "co_address"), reply_markup=cancel_kb(lang, [KeyboardButton(text=t(lang, "pickup"))]))


@router.message(Checkout.address, F.text)
async def co_address(m: Message, state: FSMContext):
    lang = lang_of(m.from_user)
    address = m.text.strip()[:500]
    if address in all_variants("pickup"):
        address = "Самовывоз"  # в группе заказов — по-русски
    await state.update_data(address=address)
    data = await state.get_data()
    items, total = order_summary(m.from_user.id)
    if not items:
        await state.clear()
        await m.answer(t(lang, "cart_empty_short"), reply_markup=main_kb(lang))
        return
    await state.set_state(Checkout.confirm)
    await m.answer(t(lang, "check_order"), reply_markup=ReplyKeyboardRemove())
    shown = t(lang, "pickup") if address == "Самовывоз" else address
    await m.answer(
        f"{items_text(items)}\n\n💰 <b>{t(lang, 'total')}: {fmt_money(total)}</b>\n\n"
        f'👤 {html.escape(data["name"])}\n📱 {html.escape(data["phone"])}\n🚚 {html.escape(shown)}',
        reply_markup=ikb([[{"text": t(lang, "confirm"), "callback_data": "co_ok"},
                           {"text": t(lang, "cancel_inline"), "callback_data": "co_cancel"}]]),
    )


@router.callback_query(Checkout.confirm, F.data == "co_cancel")
async def co_cancel(c: CallbackQuery, state: FSMContext):
    lang = lang_of(c.from_user)
    await state.clear()
    await c.message.edit_text(t(lang, "order_cancelled"))
    await c.message.answer(t(lang, "main_menu"), reply_markup=main_kb(lang))
    await c.answer()


@router.callback_query(Checkout.confirm, F.data == "co_ok")
async def co_ok(c: CallbackQuery, state: FSMContext):
    lang = lang_of(c.from_user)
    data = await state.get_data()
    items, total = order_summary(c.from_user.id)
    if not items:
        await state.clear()
        await c.answer(t(lang, "cart_empty_short"), show_alert=True)
        return
    await state.clear()
    await place_order(c.bot, c.from_user, data["name"], data["phone"], data["address"],
                      items, total, source="чат")
    clear_cart(c.from_user.id)
    # номер заказа — только в группе заказов, покупателю не показываем
    await c.message.edit_text(t(lang, "order_ok", items=items_text(items), total=fmt_money(total), address=""))
    await c.message.answer(t(lang, "main_menu"), reply_markup=main_kb(lang))
    await c.answer()
