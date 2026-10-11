"""
Покупатель: выбранный язык интерфейса (ru / uz). Хранится в файле и в базе Neon.
"""
import asyncio

from src.database import connection as db
from src.database.json_store import langs


def lang_of(u) -> str:
    """Выбранный язык; если ещё не выбран — по языку Telegram."""
    saved = langs.data.get(str(u.id))
    if saved:
        return saved
    return "uz" if (getattr(u, "language_code", "") or "").startswith("uz") else "ru"


def has_lang(user_id: int) -> bool:
    return str(user_id) in langs.data


def set_lang(user_id: int, lang: str) -> None:
    langs.data[str(user_id)] = lang
    langs.save()
    if db.pool:
        asyncio.get_running_loop().create_task(db.save_lang(user_id, lang))
