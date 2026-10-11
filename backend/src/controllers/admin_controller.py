"""
Команды администратора: /update, /orders, /stats, /admin. Автообновление каталога из канала.
"""
import asyncio
import html
import logging
from datetime import timedelta

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from src.config.settings import AUTO_UPDATE_HOURS
from src.middlewares.auth_middleware import is_admin
from src.models.catalog import catalog
from src.models.order import recent_orders
from src.models.visit import all_users, stats_since, today
from src.utils.channel_scraper import update_catalog
from src.utils.formatting import fmt_money

router = Router(name="admin")


async def run_update() -> int:
    await asyncio.to_thread(update_catalog, logging.info)
    catalog.load()
    return len(catalog.products)


async def auto_update_loop():
    while AUTO_UPDATE_HOURS > 0:
        await asyncio.sleep(AUTO_UPDATE_HOURS * 3600)
        try:
            n = await run_update()
            logging.info("Автообновление каталога: %s товаров", n)
        except Exception:
            logging.exception("Автообновление не удалось")


@router.message(Command("update"), F.func(is_admin))
async def adm_update(m: Message):
    await m.answer("⏳ Обновляю каталог из канала…")
    try:
        n = await run_update()
        await m.answer(f"✅ Каталог обновлён: {n} товаров.")
    except Exception as e:
        logging.exception("update failed")
        await m.answer(f"❌ Ошибка обновления: {html.escape(str(e))}")


@router.message(Command("orders"), F.func(is_admin))
async def adm_orders(m: Message):
    last = await recent_orders(10)
    if not last:
        await m.answer("Заказов пока нет.")
        return
    lines = [f'№{o["number"]} {o["time"]} — {html.escape(o["name"])}, {html.escape(o["phone"])}, '
             f'{fmt_money(o["total"])}' for o in last]
    await m.answer("<b>Последние заказы:</b>\n" + "\n".join(lines))


@router.message(Command("stats"), F.func(is_admin))
async def adm_stats(m: Message):
    day0 = today()
    blocks = []
    for title, days in (("Сегодня", 1), ("7 дней", 7), ("30 дней", 30)):
        s = await stats_since(day0 - timedelta(days=days - 1))
        blocks.append(f"<b>{title}</b>\n"
                      f"👥 {s['people']} чел. (бот {s['bot']} · магазин {s['app']})\n"
                      f"🛒 {s['orders']} заказ(ов) · {fmt_money(s['total'])}"
                      + (f" (из магазина {s['orders_app']})" if s["orders"] else ""))
    await m.answer("📊 <b>Статистика ELTA</b>\n\n" + "\n\n".join(blocks)
                   + f"\n\nВсего покупателей: {await all_users()}"
                   "\n<i>Посещения считаются с 11.10.2026, администраторы не учитываются.</i>")


@router.message(Command("admin"), F.func(is_admin))
async def adm_help(m: Message):
    await m.answer("<b>Команды администратора</b>\n"
                   "/update — загрузить новые товары из канала\n"
                   "/orders — последние 10 заказов\n"
                   "/stats — посетители и заказы за день, неделю, месяц\n"
                   f"\nВ каталоге сейчас {len(catalog.products)} товаров. "
                   f"Автообновление: {'каждые ' + str(AUTO_UPDATE_HOURS) + ' ч' if AUTO_UPDATE_HOURS else 'выключено'}.")
