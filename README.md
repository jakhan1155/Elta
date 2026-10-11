# Telegram-бот магазина ELTA

Каталог берётся из канала https://t.me/elta_uz: все посты с ценой («💰Цена - …$») становятся товарами вместе с фото и описанием.
Интерфейс — на узбекском и русском (выбор при /start, смена — /til). Описания товаров — как в канале.

## Мини-приложение (Web App)
Кнопка **«🛍 Магазин»** слева от поля ввода (и кнопки «Открыть магазин» в чате) открывает магазин прямо внутри Telegram:
интро, поиск, категории, бренды, витрина с фото, карточка товара с галереей, корзина, нижнее меню и оформление заказа
(имя, телефон одной кнопкой, доставка/самовывоз, комментарий). Заказ проверяется по подписи Telegram,
приходит в группу заказов и подтверждается покупателю в чате.

Для Telegram приложению нужен **https-адрес**:
- на этом компьютере бот сам поднимает временный адрес через `cloudflared` (адрес меняется при перезапуске, кнопка обновляется автоматически);
- для постоянной работы разместите бота на сервере (`deploy/setup.sh`) или укажите `WEBAPP_URL=https://ваш-домен` в `backend/.env`.

## Что умеет бот
- 🛍 **Каталог** по категориям + раздел «🆕 Новинки»
- Карточка товара: альбом фото, полное описание, артикул, цена, ссылка на пост в канале
- 🛒 **Корзина**: + / − количество, итоговая сумма
- ⚡ **Купить сейчас** и **оформление заказа**: имя → телефон (одной кнопкой) → адрес/самовывоз → подтверждение
- Заказ сразу приходит в группу заказов и сохраняется в базе Neon (копия — `backend/data/orders.json`)
- 🔎 **Поиск** по названию, бренду, артикулу (можно просто написать боту слово)
- 📞 Контакты, кнопка «Спросить у менеджера»
- Новые посты из канала подтягиваются **автоматически** (каждые 6 ч) или командой `/update`

## Запуск
1. Установите библиотеки: `pip install -r backend/requirements.txt`
2. Скопируйте `backend/.env.example` в `backend/.env` и заполните (`BOT_TOKEN`, `ADMIN_IDS`, `ORDER_CHAT_ID`, `DATABASE_URL`).
3. Запустите: `python backend/src/main.py`

## Автозапуск на этом компьютере
- Ярлык **«ELTA bot»** в автозагрузке Windows запускает `scripts/start_elta_bot.vbs` → `scripts/run_bot.ps1` (скрыто, без окна).
- `run_bot.ps1` ждёт интернет, запускает бота и перезапускает его через 10 сек, если он остановился.
- Бот сам следит за туннелем мини-приложения: если адрес перестал открываться, поднимает новый и обновляет кнопку «Магазин».
- Запустить вручную: двойной щелчок по `scripts/start_elta_bot.vbs`. Остановить: `scripts/stop_elta_bot.bat`.
- Журнал работы: `logs/bot.log` (предыдущий запуск — `logs/bot.prev.log`).

## Команды администратора
- `/admin` — справка
- `/update` — сразу загрузить новые товары из канала
- `/orders` — последние 10 заказов

## Как править каталог
- Новый товар: просто опубликуйте пост в канале в обычном формате (фото + описание + `💰Цена - 50$`).
- Изменить название, категорию или цену, скрыть товар — `backend/data/overrides.json` (ключ — номер поста), затем `/update`.
- Если товар опубликован повторно, бот показывает только самый свежий пост.

## Структура
```
ELTA-bot/
├── backend/                         # бот + сервер мини-приложения (Python, aiogram)
│   ├── src/
│   │   ├── config/settings.py       # настройки и пути (.env)
│   │   ├── core/                    # bot.py — бот и меню, server.py — веб-сервер, tunnel.py — https-адрес
│   │   ├── database/                # connection.py — Neon (PostgreSQL), json_store.py — копии в файлах
│   │   ├── models/                  # catalog, cart, order, user (язык)
│   │   ├── controllers/             # start, catalog, cart, checkout, order, admin, webapp
│   │   ├── routes/                  # bot_routes.py — все обработчики бота, web_routes.py — адреса сервера
│   │   ├── middlewares/             # auth (админ, подпись Telegram), cache
│   │   ├── utils/                   # keyboards, texts (ru/uz), formatting, photos, logger, channel_scraper
│   │   └── main.py                  # запуск
│   ├── data/                        # catalog.json, overrides.json, photos/, копии заказов и корзин
│   ├── .env / .env.example
│   └── requirements.txt
├── frontend/                        # мини-приложение (HTML/CSS/JS без сборки)
│   ├── src/
│   │   ├── app/                     # page.js — запуск и события, navigation.js — страницы
│   │   ├── components/
│   │   │   ├── ui/                  # MainButton, Toast
│   │   │   ├── features/            # Intro, ProductCard, Catalog, CategoryTiles, BrandMenu, ProductPage, CartList, CheckoutForm, OrderDone
│   │   │   └── layout/              # Header, BottomNavigation, Footer
│   │   ├── hooks/useTelegram.js     # Telegram WebApp
│   │   ├── lib/                     # api, utils, i18n (ru/uz), introSound
│   │   ├── providers/TelegramProvider.js
│   │   ├── store/                   # appStore, cartStore
│   │   └── styles/globals.css
│   └── public/                      # index.html, images/ (логотип, круги категорий)
├── scripts/                         # автозапуск и остановка на Windows
├── deploy/setup.sh                  # установка на сервер Ubuntu
└── logs/
```
