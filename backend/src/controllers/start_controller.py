"""
Начало работы: /start, выбор языка, отмена, контакты, служебные /myid и /chatid.
"""
import html
import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.config.settings import ADMIN_USERNAME, CHANNEL_URL, PHONES
from src.config import settings
from src.models.user import has_lang, lang_of, set_lang
from src.utils.keyboards import ikb, is_btn, lang_kb, main_kb, shop_button
from src.utils.texts import t

router = Router(name="start")


async def send_welcome(bot: Bot, chat_id: int, user):
    lang = lang_of(user)
    await bot.send_message(chat_id, t(lang, "welcome", name=html.escape(user.first_name or "")),
                           reply_markup=main_kb(lang))
    if settings.webapp_url:
        await bot.send_message(chat_id, t(lang, "shop_prompt"), reply_markup=ikb([[shop_button(lang)]]))


@router.message(CommandStart())
async def start(m: Message, state: FSMContext):
    await state.clear()
    logging.info("/start от id=%s @%s (%s)", m.from_user.id, m.from_user.username, m.from_user.full_name)
    if not has_lang(m.from_user.id):  # первый раз — сначала выбор языка
        await m.answer(t("ru", "choose_lang"), reply_markup=lang_kb())
        return
    await send_welcome(m.bot, m.chat.id, m.from_user)


@router.message(Command("til", "lang", "language"))
@router.message(is_btn("btn_lang"))
async def choose_lang(m: Message, state: FSMContext):
    await state.clear()
    await m.answer(t("ru", "choose_lang"), reply_markup=lang_kb())


@router.callback_query(F.data.startswith("lang:"))
async def cb_lang(c: CallbackQuery, state: FSMContext):
    lang = c.data[5:] if c.data[5:] in ("ru", "uz") else "ru"
    first = not has_lang(c.from_user.id)
    set_lang(c.from_user.id, lang)
    await state.clear()
    await c.answer()
    await c.message.edit_text(t(lang, "lang_set"))
    if first:
        await send_welcome(c.bot, c.message.chat.id, c.from_user)
    else:
        await c.message.answer(t(lang, "main_menu"), reply_markup=main_kb(lang))


@router.message(is_btn("btn_cancel"))
async def cancel(m: Message, state: FSMContext):
    await state.clear()
    lang = lang_of(m.from_user)
    await m.answer(t(lang, "cancelled"), reply_markup=main_kb(lang))


@router.message(is_btn("btn_contacts"))
async def contacts(m: Message):
    lang = lang_of(m.from_user)
    phones = "\n".join(f"📞 {p}" for p in PHONES)
    await m.answer(
        t(lang, "contacts", phones=phones, m=ADMIN_USERNAME, ch=CHANNEL_URL),
        reply_markup=ikb([[{"text": t(lang, "write_manager"), "url": f"https://t.me/{ADMIN_USERNAME}"}],
                          [{"text": t(lang, "open_channel"), "url": CHANNEL_URL}]]),
    )


@router.message(Command("myid"))
async def my_id(m: Message):
    await m.answer(f"Ваш Telegram ID: <code>{m.from_user.id}</code>")


@router.message(Command("chatid"))
async def chat_id(m: Message):  # номер группы для заказов (ORDER_CHAT_ID в .env)
    logging.info("/chatid: чат %s «%s», от %s", m.chat.id, m.chat.title, m.from_user.id)
    await m.answer(f"ID этого чата: <code>{m.chat.id}</code>")
