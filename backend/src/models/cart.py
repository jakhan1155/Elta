"""
Корзина покупателя в чате бота: {product_id: qty}. Файл-копия + база Neon.
(В мини-приложении корзина живёт в браузере и приходит вместе с заказом.)
"""
import asyncio

from src.database import connection as db
from src.database.json_store import carts
from src.models.catalog import catalog, price_num


def get_cart(user_id: int) -> dict:
    return carts.data.get(str(user_id), {})


def save_cart(user_id: int) -> None:
    """Корзина: файл-копия сразу, в базу Neon — в фоне (если подключена)."""
    carts.save()
    if db.pool:
        asyncio.get_running_loop().create_task(db.save_cart(user_id, get_cart(user_id)))


def change_qty(user_id: int, pid: str, delta: int) -> int:
    cart = carts.data.setdefault(str(user_id), {})
    qty = max(0, cart.get(pid, 0) + delta)
    if qty:
        cart[pid] = qty
    else:
        cart.pop(pid, None)
    save_cart(user_id)
    return qty


def clear_cart(user_id: int) -> None:
    carts.data.pop(str(user_id), None)
    save_cart(user_id)


def order_item(p: dict, qty: int) -> dict:
    return {"id": p["id"], "title": p["title"], "article": p.get("article"),
            "price": price_num(p), "qty": qty, "post_url": p["post_url"]}


def order_summary(user_id: int) -> tuple[list[dict], float]:
    items, total = [], 0.0
    for pid, qty in get_cart(user_id).items():
        p = catalog.products.get(int(pid))
        if not p:
            continue
        items.append(order_item(p, qty))
        total += price_num(p) * qty
    return items, total
