"""
Каталог товаров (data/catalog.json, собирается из канала).
Товар: id, title, article, price, category, description, photos, post_url.
"""
import json

from src.config.settings import CATALOG_FILE, CATEGORY_ORDER


class Catalog:
    def __init__(self):
        self.products: dict[int, dict] = {}
        self.categories: list[str] = []
        self.load()

    def load(self):
        items = json.loads(CATALOG_FILE.read_text(encoding="utf-8")) if CATALOG_FILE.exists() else []
        self.products = {p["id"]: p for p in items}
        cats = {p["category"] for p in items}
        self.categories = [c for c in CATEGORY_ORDER if c in cats] + sorted(cats - set(CATEGORY_ORDER))

    def in_category(self, idx: int) -> list[dict]:
        cat = self.categories[idx]
        return [p for p in self.products.values() if p["category"] == cat]

    def search(self, query: str) -> list[dict]:
        words = query.lower().split()
        res = []
        for p in self.products.values():
            hay = f'{p["title"]} {p.get("article") or ""} {p["description"]}'.lower()
            if all(w in hay for w in words):
                # совпадение в названии — выше
                res.append((0 if all(w in p["title"].lower() for w in words) else 1, p))
        return [p for _, p in sorted(res, key=lambda x: (x[0], -x[1]["id"]))]


catalog = Catalog()


def price_num(p: dict) -> float:
    try:
        return float(p["price"])
    except ValueError:
        return 0.0
