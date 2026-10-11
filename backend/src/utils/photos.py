"""
Отправка фото товара альбомом. Загруженные фото запоминаются (file_id), чтобы не отправлять файлы заново.
"""
import logging

from aiogram import Bot
from aiogram.types import FSInputFile, InputMediaPhoto

from src.config.settings import DATA_DIR
from src.database.json_store import file_ids


async def send_photos(bot: Bot, chat_id: int, p: dict):
    photos = [ph for ph in p["photos"] if (DATA_DIR / ph).exists() or ph in file_ids.data][:10]
    if not photos:
        return
    media = [InputMediaPhoto(media=file_ids.data.get(ph) or FSInputFile(DATA_DIR / ph)) for ph in photos]
    try:
        msgs = await bot.send_media_group(chat_id, media)
    except Exception:
        # file_id мог устареть (например, сменили бота) — грузим файлы заново
        for ph in photos:
            file_ids.data.pop(ph, None)
        media = [InputMediaPhoto(media=FSInputFile(DATA_DIR / ph)) for ph in photos if (DATA_DIR / ph).exists()]
        if not media:
            return
        try:
            msgs = await bot.send_media_group(chat_id, media)
        except Exception:
            # битый файл и т.п. — карточку товара всё равно покажем, просто без альбома
            logging.exception("Не удалось отправить фото товара %s", p["id"])
            return
    for ph, m in zip(photos, msgs):
        if m.photo:
            file_ids.data[ph] = m.photo[-1].file_id
    file_ids.save()
