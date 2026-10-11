"""
Посещения для статистики: кто и в какой день пользовался ботом (source="bot") или открывал магазин ("app").
Один человек считается один раз в день для каждого источника. Администраторы не считаются.
"""
import asyncio
import logging
from datetime import date, datetime, timedelta, timezone

from src.config.settings import ADMIN_IDS
from src.database import connection as db
from src.database.json_store import orders, visits

TASHKENT = timezone(timedelta(hours=5))  # в Узбекистане нет перехода на летнее время
_seen: set[tuple[date, int, str]] = set()  # уже записанные сегодня — чтобы не писать в базу на каждое нажатие


def today() -> date:
    return datetime.now(TASHKENT).date()


def record_visit(user_id: int, source: str) -> None:
    if user_id in ADMIN_IDS:
        return
    key = (today(), user_id, source)
    if key in _seen:
        return
    _seen.add(key)
    if db.pool:
        asyncio.get_running_loop().create_task(db.add_visit(key[0], user_id, source))
    else:
        day = visits.data.setdefault(key[0].isoformat(), {})
        ids = day.setdefault(source, [])
        if user_id not in ids:
            ids.append(user_id)
            visits.save()


def _file_stats(since: date) -> dict:
    bot, app = set(), set()
    for d, by_source in visits.data.items():
        if date.fromisoformat(d) >= since:
            bot.update(by_source.get("bot", []))
            app.update(by_source.get("app", []))
    recent = [o for o in orders.data if o["time"][:10] >= since.isoformat()]
    return {"people": len(bot | app), "bot": len(bot), "app": len(app), "orders": len(recent),
            "total": sum(o["total"] for o in recent), "orders_app": sum(o.get("source") == "приложение" for o in recent)}


async def stats_since(since: date) -> dict:
    if db.pool:
        try:
            return await db.stats_since(since)
        except Exception:
            logging.exception("Neon недоступна — статистика из файлов")
    return _file_stats(since)


async def all_users() -> int:
    if db.pool:
        try:
            return await db.all_users()
        except Exception:
            pass
    return len({u for day in visits.data.values() for ids in day.values() for u in ids})
