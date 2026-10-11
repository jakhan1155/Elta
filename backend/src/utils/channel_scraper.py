"""
Собирает товары из публичного канала t.me/elta_uz в data/catalog.json + папку data/photos/.

Запуск вручную (из папки backend):  python -m src.utils.channel_scraper
Повторный запуск обновляет каталог (новые посты добавятся, фото не качаются заново).
"""
import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from src.config.settings import CATALOG_FILE as CATALOG, CHANNEL, OVERRIDES_FILE as OVERRIDES, PHOTOS_DIR as PHOTOS

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
PRICE_RE = re.compile(r"Цена\s*[-–—:]?\s*([\d\s.,]+)\s*\$", re.I)
ARTICLE_RE = re.compile(r"артикул[:\s]*([A-Za-z0-9\-]+)", re.I)
BG_RE = re.compile(r"url\(['\"]?(.*?)['\"]?\)")

# Категория определяется по ключевым словам в названии/описании (первое совпадение)
CATEGORIES = [
    ("👕 Одежда", ["куртк", "брюк", "штаны", "футболк", "кофт", "флис", "жилет", "термобел",
                  "толстовк", "шорты", "рубашк", "пуховик", "худи", "ветровк", "перчат",
                  "шапк", "бафф", "носки", "кепк", "панам"]),
    ("🥾 Обувь", ["кроссовк", "ботинк", "обув", "сапог", "сандал", "тапоч"]),
    ("⛺ Палатки и сон", ["палатк", "тент", "спальн", "коврик", "гамак", "подушк", "матрас", "шатер", "шатёр"]),
    ("🎒 Рюкзаки и сумки", ["рюкзак", "сумк", "гермомеш", "чехол", "поясн"]),
    ("🔥 Кухня и огонь", ["гриль", "мангал", "горелк", "газ", "котел", "котелок", "посуд", "кофе",
                         "чайник", "кружк", "термос", "плитк", "печ", "кастрюл", "сковород",
                         "фляг", "бутыл", "столов", "ложк", "нож"]),
    ("🔦 Фонари", ["фонар", "лампа", "налобн"]),
    ("🪑 Мебель для кемпинга", ["стул", "кресл", "стол", "раскладуш"]),
]
OTHER = "🎒 Рюкзаки и снаряжение"


def category_for(text: str) -> str:
    low = text.lower()
    # по заголовку точнее, поэтому сначала ищем в первой строке
    first = low.split("\n", 1)[0]
    for source in (first, low):
        for name, words in CATEGORIES:
            if any(w in source for w in words):
                return name
    return OTHER


def bg_url(el) -> str | None:
    m = BG_RE.search(el.get("style", ""))
    return m.group(1) if m else None


def parse_page(html: str):
    soup = BeautifulSoup(html, "html.parser")
    posts = []
    for msg in soup.select(".tgme_widget_message[data-post]"):
        post_id = int(msg["data-post"].split("/")[1])
        text_el = msg.select_one(".tgme_widget_message_text")
        if not text_el:
            continue
        for br in text_el.find_all("br"):
            br.replace_with("\n")
        text = text_el.get_text().strip()
        # только настоящие фото: превью видео в карточке товара непонятно, такие посты пропускаем
        photos = [u for u in (bg_url(a) for a in msg.select(".tgme_widget_message_photo_wrap")) if u]
        posts.append({"id": post_id, "text": text, "photos": photos})
    more = soup.select_one("a.tme_messages_more[data-before]")
    before = int(more["data-before"]) if more else None
    return posts, before


def clean_description(text: str) -> str:
    """Убираем из описания строки с ценой/контактом — бот покажет их сам."""
    lines = []
    for line in text.split("\n"):
        s = line.strip()
        if PRICE_RE.search(s) or s.startswith("💬") or s in ("Админ",):
            continue
        lines.append(line.rstrip())
    out = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", out).strip()


def make_title(text: str) -> str:
    first = text.split("\n", 1)[0].strip()
    first = re.sub(r"\(?\s*(арт\.|артикул)[^)]*\)?", "", first, flags=re.I)
    if first.count("(") > first.count(")"):  # "Фляга (600 мл" -> "Фляга (600 мл)"
        first = first.rstrip(" /") + ")"
    first = re.sub(r"^[^\wА-Яа-яЁё]+", "", first)  # эмодзи в начале
    return first.strip(" /")[:120]


def is_image(head: bytes) -> bool:
    """JPEG / PNG / WebP по первым байтам (а не страница ошибки сервера)."""
    return head[:3] == b"\xff\xd8\xff" or head[:8] == b"\x89PNG\r\n\x1a\n" or (head[:4] == b"RIFF" and head[8:12] == b"WEBP")


def download_image(session: requests.Session, url: str, tries: int = 3) -> bytes | None:
    for attempt in range(tries):
        try:
            r = session.get(url, timeout=30)
            if r.ok and is_image(r.content[:12]):
                return r.content
        except requests.RequestException:
            pass
        time.sleep(1 + attempt)
    return None


def ensure_thumb(photo: Path, size: int = 480) -> None:
    """Уменьшенная копия фото для витрины мини-приложения (photos/thumbs/)."""
    thumb = PHOTOS / "thumbs" / photo.name
    if thumb.exists() or not photo.exists():
        return
    try:
        from PIL import Image
    except ImportError:
        return  # без Pillow витрина просто покажет полные фото
    thumb.parent.mkdir(exist_ok=True)
    with Image.open(photo) as im:
        im = im.convert("RGB")
        im.thumbnail((size, size))
        im.save(thumb, "JPEG", quality=80, optimize=True, progressive=True)


def update_catalog(log=print) -> list[dict]:
    PHOTOS.mkdir(exist_ok=True)
    overrides = {}
    if OVERRIDES.exists():
        overrides = json.loads(OVERRIDES.read_text(encoding="utf-8"))
    session = requests.Session()
    session.headers.update(HEADERS)

    all_posts, before, pages = {}, None, 0
    while True:
        url = f"https://t.me/s/{CHANNEL}" + (f"?before={before}" if before else "")
        r = session.get(url, timeout=30)
        r.raise_for_status()
        posts, new_before = parse_page(r.text)
        for p in posts:
            all_posts[p["id"]] = p
        pages += 1
        log(f"страница {pages}: {len(posts)} постов, всего {len(all_posts)}")
        if not new_before or new_before == before or not posts:
            break
        before = new_before
        time.sleep(0.7)

    products, seen = [], set()
    for pid in sorted(all_posts, reverse=True):  # новые сверху
        p = all_posts[pid]
        m = PRICE_RE.search(p["text"])
        if not m:
            continue  # не товар (новость, приветствие и т.п.)
        ov = overrides.get(str(pid), {})
        if ov.get("hidden"):
            continue
        if not p["photos"]:  # пост только с видео — в магазин не берём
            log(f"  пост {pid}: нет фото (только видео) — пропущен")
            continue
        price = m.group(1).replace(" ", "").replace(",", ".").strip(".")
        art = ARTICLE_RE.search(p["text"])

        # Повторная публикация того же товара: оставляем самый свежий пост (актуальная цена)
        key = art.group(1).upper() if art else p["text"].split("\n", 1)[0].strip().lower()
        if key in seen:
            continue
        seen.add(key)

        files = []
        for i, url in enumerate(p["photos"][:10]):  # в альбоме Telegram максимум 10
            f = PHOTOS / f"{pid}_{i}.jpg"
            if not (f.exists() and is_image(f.read_bytes()[:12])):  # нет файла или он битый
                data = download_image(session, url)
                if not data:
                    log(f"  ! не скачал фото {pid}_{i} — пропускаю")
                    f.unlink(missing_ok=True)
                    continue
                f.write_bytes(data)
            files.append(f"photos/{f.name}")
            if i == 0:
                ensure_thumb(f)

        products.append({
            "id": pid,
            "title": ov.get("title") or make_title(p["text"]),
            "article": art.group(1) if art else None,
            "price": str(ov.get("price") or price),
            "category": ov.get("category") or category_for(p["text"]),
            "description": clean_description(p["text"]),
            "photos": files,
            "post_url": f"https://t.me/{CHANNEL}/{pid}",
        })

    tmp = CATALOG.with_suffix(".tmp")
    tmp.write_text(json.dumps(products, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(CATALOG)
    log(f"Готово: {len(products)} товаров -> {CATALOG.name}")
    return products


def main():
    products = update_catalog()
    counts = {}
    for p in products:
        counts[p["category"]] = counts.get(p["category"], 0) + 1
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
