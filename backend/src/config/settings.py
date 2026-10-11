"""
Настройки бота: пути к папкам и значения из backend/.env (образец — .env.example).
"""
import shutil
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]      # ELTA-bot/backend
PROJECT_DIR = BACKEND_DIR.parent                       # ELTA-bot
DATA_DIR = BACKEND_DIR / "data"                        # каталог, фото, копии заказов и корзин
PHOTOS_DIR = DATA_DIR / "photos"
CATALOG_FILE = DATA_DIR / "catalog.json"
OVERRIDES_FILE = DATA_DIR / "overrides.json"           # ручные правки товаров (название, цена, скрыть)
FRONTEND_DIR = PROJECT_DIR / "frontend"                # мини-приложение
DATA_DIR.mkdir(exist_ok=True)


def load_env(path: Path) -> dict:
    env = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


ENV = load_env(BACKEND_DIR / ".env")
BOT_TOKEN = ENV.get("BOT_TOKEN", "")
ADMIN_IDS = {int(x) for x in ENV.get("ADMIN_IDS", "").replace(" ", "").split(",") if x}
ORDER_CHAT_ID = int(ENV["ORDER_CHAT_ID"]) if ENV.get("ORDER_CHAT_ID") else next(iter(ADMIN_IDS), None)
ADMIN_USERNAME = ENV.get("ADMIN_USERNAME", "Jakhan_11")
CHANNEL = "elta_uz"
CHANNEL_URL = ENV.get("CHANNEL_URL", f"https://t.me/{CHANNEL}")
PHONES = [p.strip() for p in ENV.get("PHONES", "+998(33)003-22-77,+998(93)516-05-38").split(",")]
AUTO_UPDATE_HOURS = float(ENV.get("AUTO_UPDATE_HOURS", "6"))
DATABASE_URL = ENV.get("DATABASE_URL", "")  # Neon (PostgreSQL): заказы, корзины, языки; пусто — только файлы
PAGE_SIZE = 8

# Мини-приложение (Web App)
WEB_HOST = ENV.get("WEB_HOST") or "127.0.0.1"
WEB_PORT = int(ENV.get("WEB_PORT", "8080"))
TUNNEL = ENV.get("TUNNEL", "auto").lower()  # auto — временный адрес через cloudflared, off — не поднимать
CLOUDFLARED = (ENV.get("CLOUDFLARED_PATH") or shutil.which("cloudflared")
               or r"C:\Program Files (x86)\cloudflared\cloudflared.exe")
# Адрес магазина: постоянный из .env или временный от туннеля (меняется во время работы — читать как settings.webapp_url)
webapp_url = ENV.get("WEBAPP_URL", "").rstrip("/")

CATEGORY_ORDER = ["👕 Одежда", "🥾 Обувь", "⛺ Палатки и сон", "🔥 Кухня и огонь",
                  "🪑 Мебель для кемпинга", "🔦 Фонари", "🎒 Рюкзаки и снаряжение"]
