"""
Заказ: номер, время, источник (чат / приложение), покупатель, контакты, товары, сумма, статус.
Основное хранилище — база Neon (она выдаёт номер), копия — data/orders.json.
"""
import logging
import time

from src.database import connection as db
from src.database.json_store import orders


def full_name(u) -> str:
    return " ".join(x for x in (u.first_name, u.last_name) if x)


def make_order(u, name: str, phone: str, address: str, items: list[dict], total: float,
               comment: str = "", source: str = "чат") -> dict:
    return {
        "number": None,
        "time": time.strftime("%Y-%m-%d %H:%M"),
        "source": source,
        "user_id": u.id, "username": u.username, "tg_name": full_name(u),
        "name": name, "phone": phone, "address": address, "comment": comment,
        "items": items, "total": total, "status": "new",
    }


async def save_order(order: dict) -> dict:
    if db.pool:
        try:
            order["number"] = await db.add_order(order)
        except Exception:
            logging.exception("Neon: заказ не записан в базу — сохраняю только в файл")
    if order["number"] is None:
        order["number"] = max([o["number"] for o in orders.data] or [0]) + 1
    orders.data.append(order)  # копия в data/orders.json
    orders.save()
    return order


async def recent_orders(n: int = 10) -> list[dict]:
    try:
        if db.pool:
            return await db.recent_orders(n)
    except Exception:
        logging.exception("Neon недоступна — показываю заказы из файла")
    return list(reversed(orders.data[-n:]))
