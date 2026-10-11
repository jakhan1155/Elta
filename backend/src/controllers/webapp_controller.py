"""
Мини-приложение: страница магазина, каталог, язык покупателя и приём заказа.
"""
import html
import json
import logging
import re
import time

from aiogram import Bot
from aiohttp import web

from src.config.settings import ADMIN_USERNAME, CHANNEL_URL, DATA_DIR, FRONTEND_DIR, PHONES
from src.controllers.order_controller import place_order
from src.middlewares.auth_middleware import webapp_user
from src.models.cart import order_item
from src.models.catalog import catalog, price_num
from src.models.user import has_lang, lang_of
from src.models.visit import record_visit
from src.utils.formatting import fmt_money, items_text
from src.utils.texts import t

last_order_at: dict[int, float] = {}  # защита от двойного нажатия «Подтвердить»


def json_response(data: dict, status: int = 200) -> web.Response:
    return web.json_response(data, status=status, dumps=lambda o: json.dumps(o, ensure_ascii=False))


def json_error(text: str, status: int = 400) -> web.Response:
    return json_response({"ok": False, "error": text}, status)


def thumb_for(p: dict) -> str:
    if not p["photos"]:
        return ""
    name = p["photos"][0].rsplit("/", 1)[-1]
    return f"photos/thumbs/{name}" if (DATA_DIR / "photos" / "thumbs" / name).exists() else p["photos"][0]


async def web_index(request: web.Request) -> web.FileResponse:
    return web.FileResponse(FRONTEND_DIR / "public" / "index.html")


async def web_health(request: web.Request) -> web.Response:
    return web.Response(text="ok")


async def web_catalog(request: web.Request) -> web.Response:
    products = [{**p, "thumb": thumb_for(p)} for p in sorted(catalog.products.values(), key=lambda p: -p["id"])]
    return json_response({"products": products, "categories": catalog.categories, "phones": PHONES,
                          "manager_url": f"https://t.me/{ADMIN_USERNAME}", "channel_url": CHANNEL_URL})


async def web_lang(request: web.Request) -> web.Response:
    """Язык покупателя для мини-приложения (по подписанным данным Telegram)."""
    try:
        body = await request.json()
        user, _ = webapp_user(str(body.get("initData", "")))
    except Exception:
        user = None
    if user:
        record_visit(user.id, "app")  # магазин открыт — для /stats
    return web.json_response({"lang": lang_of(user) if user else None})


async def web_order(request: web.Request) -> web.Response:
    try:
        body = await request.json()
    except Exception:
        return json_error(t("ru", "err_request"))
    lang = body.get("lang") if body.get("lang") in ("ru", "uz") else "ru"
    u, err = webapp_user(str(body.get("initData", "")))
    if err:
        return json_error(t(lang, err), 401)
    lang = lang_of(u) if has_lang(u.id) else lang
    if time.time() - last_order_at.get(u.id, 0) < 10:
        return json_error(t(lang, "err_wait"), 429)

    items, total = [], 0.0
    for it in (body.get("items") or [])[:50]:
        try:
            pid, qty = int(it["id"]), int(it["qty"])
        except (KeyError, TypeError, ValueError):
            continue
        p = catalog.products.get(pid)
        if not p or not 1 <= qty <= 99:
            continue
        items.append(order_item(p, qty))
        total += price_num(p) * qty
    if not items:
        return json_error(t(lang, "err_empty"))

    name = str(body.get("name", "")).strip()[:100]
    phone = str(body.get("phone", "")).strip()[:40]
    pickup = body.get("delivery") == "pickup"
    address = "Самовывоз" if pickup else str(body.get("address", "")).strip()[:500]
    comment = str(body.get("comment", "")).strip()[:500]
    if len(name) < 2:
        return json_error(t(lang, "err_name"))
    if len(re.sub(r"\D", "", phone)) < 9:
        return json_error(t(lang, "err_phone"))
    if len(address) < 3:
        return json_error(t(lang, "err_address"))

    last_order_at[u.id] = time.time()
    bot: Bot = request.app["bot"]
    await place_order(bot, u, name, phone, address, items, total, comment, source="приложение")
    try:
        shown = t(lang, "pickup") if pickup else address
        await bot.send_message(u.id, t(lang, "order_ok", items=items_text(items), total=fmt_money(total),
                                       address=f"\n🚚 {html.escape(shown)}"))
    except Exception:
        logging.warning("Не удалось отправить подтверждение пользователю %s", u.id)
    return web.json_response({"ok": True, "total": total})  # без номера заказа — покупателю он не нужен
