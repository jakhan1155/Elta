"""
Файловое хранилище data/*.json: копии корзин, заказов и языков (на случай, если база недоступна).
"""
import json
from pathlib import Path

from src.config.settings import DATA_DIR


class JsonStore:
    def __init__(self, path: Path, default):
        self.path = path
        self.data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else default

    def save(self):
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)


carts = JsonStore(DATA_DIR / "carts.json", {})        # {user_id: {product_id: qty}}
orders = JsonStore(DATA_DIR / "orders.json", [])      # список заказов
langs = JsonStore(DATA_DIR / "langs.json", {})        # {user_id: "ru" | "uz"}
visits = JsonStore(DATA_DIR / "visits.json", {})      # без базы: {"2026-10-11": {"bot": [id…], "app": [id…]}}
file_ids = JsonStore(DATA_DIR / "file_ids.json", {})  # кэш загруженных в Telegram фото: путь -> file_id
