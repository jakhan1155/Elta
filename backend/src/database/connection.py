"""
Подключение к PostgreSQL (Neon): заказы, корзины, языки покупателей. Адрес базы — DATABASE_URL в .env.
Без DATABASE_URL бот работает только на файлах data/*.json (см. json_store.py).
"""
import json
import logging
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import asyncpg

pool: asyncpg.Pool | None = None

SCHEMA = """
create table if not exists orders (
    number      serial primary key,
    created_at  timestamptz not null default now(),
    source      text,
    user_id     bigint,
    username    text,
    tg_name     text,
    name        text,
    phone       text,
    address     text,
    comment     text,
    items       jsonb not null,
    total       numeric(12, 2) not null,
    status      text not null default 'new'
);
create table if not exists carts (
    user_id     bigint primary key,
    items       jsonb not null,
    updated_at  timestamptz not null default now()
);
create table if not exists user_langs (
    user_id     bigint primary key,
    lang        text not null
);
create table if not exists visits (
    day         date not null,
    user_id     bigint not null,
    source      text not null,
    primary key (day, user_id, source)
);
"""


def _clean_url(url: str) -> str:
    # asyncpg не знает параметр libpq channel_binding — убираем его, шифрование остаётся (sslmode=require)
    parts = urlsplit(url)
    query = urlencode([(k, v) for k, v in parse_qsl(parts.query) if k != "channel_binding"])
    return urlunsplit(parts._replace(query=query))


async def init(url: str, local_orders: list, local_carts: dict) -> None:
    """Подключается, создаёт таблицы и один раз переносит старые заказы/корзины из файлов."""
    global pool
    pool = await asyncpg.create_pool(_clean_url(url), min_size=1, max_size=3, command_timeout=20,
                                     max_inactive_connection_lifetime=60)  # Neon «засыпает» — старые соединения не держим
    async with pool.acquire() as c:
        await c.execute(SCHEMA)
        if not await c.fetchval("select count(*) from orders") and local_orders:
            for o in local_orders:
                await c.execute(
                    "insert into orders (number, created_at, source, user_id, username, tg_name, name, phone, address,"
                    " comment, items, total, status) values ($1, to_timestamp($2, 'YYYY-MM-DD HH24:MI'), $3, $4, $5, $6,"
                    " $7, $8, $9, $10, $11, $12, $13)",
                    o["number"], o["time"], o.get("source"), o["user_id"], o.get("username"), o.get("tg_name"),
                    o["name"], o["phone"], o["address"], o.get("comment", ""), json.dumps(o["items"], ensure_ascii=False),
                    o["total"], o.get("status", "new"))
            await c.execute("select setval('orders_number_seq', (select max(number) from orders))")
            logging.info("Neon: перенесено заказов из файла: %s", len(local_orders))
        if not await c.fetchval("select count(*) from carts") and local_carts:
            for uid, items in local_carts.items():
                if items:
                    await c.execute("insert into carts (user_id, items) values ($1, $2) on conflict do nothing",
                                    int(uid), json.dumps(items))
    logging.info("Neon: база подключена")


async def load_carts() -> dict:
    rows = await pool.fetch("select user_id, items from carts")
    return {str(r["user_id"]): json.loads(r["items"]) for r in rows}


async def save_cart(user_id: int, items: dict) -> None:
    try:
        if items:
            await pool.execute(
                "insert into carts (user_id, items, updated_at) values ($1, $2, now())"
                " on conflict (user_id) do update set items = excluded.items, updated_at = now()",
                int(user_id), json.dumps(items))
        else:
            await pool.execute("delete from carts where user_id = $1", int(user_id))
    except Exception:
        logging.exception("Neon: не удалось сохранить корзину %s", user_id)


async def load_langs() -> dict:
    rows = await pool.fetch("select user_id, lang from user_langs")
    return {str(r["user_id"]): r["lang"] for r in rows}


async def save_lang(user_id: int, lang: str) -> None:
    try:
        await pool.execute("insert into user_langs (user_id, lang) values ($1, $2)"
                           " on conflict (user_id) do update set lang = excluded.lang", int(user_id), lang)
    except Exception:
        logging.exception("Neon: не удалось сохранить язык %s", user_id)


async def add_visit(day, user_id: int, source: str) -> None:
    try:
        await pool.execute("insert into visits (day, user_id, source) values ($1, $2, $3) on conflict do nothing",
                           day, int(user_id), source)
    except Exception:
        logging.exception("Neon: не удалось записать посещение %s", user_id)


async def stats_since(day) -> dict:
    """Посетители (всего / в боте / в магазине) и заказы начиная с дня day (по ташкентскому времени)."""
    v = await pool.fetchrow(
        "select count(distinct user_id) as people,"
        " count(distinct user_id) filter (where source = 'bot') as bot,"
        " count(distinct user_id) filter (where source = 'app') as app"
        " from visits where day >= $1", day)
    o = await pool.fetchrow(
        "select count(*) as orders, coalesce(sum(total), 0) as total, count(*) filter (where source = 'приложение') as app"
        " from orders where (created_at at time zone 'Asia/Tashkent')::date >= $1", day)
    return {"people": v["people"], "bot": v["bot"], "app": v["app"],
            "orders": o["orders"], "total": float(o["total"]), "orders_app": o["app"]}


async def all_users() -> int:
    return await pool.fetchval("select count(distinct user_id) from visits")


async def add_order(o: dict) -> int:
    """Сохраняет заказ и возвращает его номер."""
    return await pool.fetchval(
        "insert into orders (source, user_id, username, tg_name, name, phone, address, comment, items, total)"
        " values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) returning number",
        o["source"], o["user_id"], o["username"], o["tg_name"], o["name"], o["phone"], o["address"],
        o["comment"], json.dumps(o["items"], ensure_ascii=False), o["total"])


async def recent_orders(n: int = 10) -> list[dict]:
    rows = await pool.fetch(
        "select number, to_char(created_at at time zone 'Asia/Tashkent', 'YYYY-MM-DD HH24:MI') as time, name, phone, total"
        " from orders order by number desc limit $1", n)
    return [dict(r) | {"total": float(r["total"])} for r in rows]
