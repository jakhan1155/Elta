"""
Тексты бота для покупателей на двух языках. Тексты товаров (из канала) не переводятся — остаются на русском.
Сообщения администратору и в группу заказов — только на русском.
"""
T = {
    # кнопки меню
    "btn_catalog": {"ru": "🛍 Каталог", "uz": "🛍 Katalog"},
    "btn_cart": {"ru": "🛒 Корзина", "uz": "🛒 Savat"},
    "btn_search": {"ru": "🔎 Поиск", "uz": "🔎 Qidiruv"},
    "btn_contacts": {"ru": "📞 Контакты", "uz": "📞 Aloqa"},
    "btn_lang": {"ru": "🌐 Язык", "uz": "🌐 Til"},
    "btn_cancel": {"ru": "❌ Отмена", "uz": "❌ Bekor qilish"},
    # приветствие и язык
    "choose_lang": {"ru": "🌐 Tilni tanlang / Выберите язык", "uz": "🌐 Tilni tanlang / Выберите язык"},
    "lang_set": {"ru": "✅ Язык: русский", "uz": "✅ Til: o'zbekcha"},
    "welcome": {
        "ru": "👋 Здравствуйте, {name}!\n\n<b>ELTA | Ready for Anything</b> ⛰️\n"
              "Премиальное снаряжение для экстремальных условий.\nКемпинг · Охота · Походы\n\n"
              "Здесь можно посмотреть весь каталог с фото, собрать корзину и оформить заказ — "
              "менеджер свяжется с вами для подтверждения.",
        "uz": "👋 Assalomu alaykum, {name}!\n\n<b>ELTA | Ready for Anything</b> ⛰️\n"
              "Ekstremal sharoitlar uchun premium jihozlar.\nKemping · Ov · Sayohat\n\n"
              "Bu yerda butun katalogni rasmlari bilan ko'rishingiz, savatni to'ldirib, buyurtma berishingiz mumkin — "
              "menejer tasdiqlash uchun siz bilan bog'lanadi.",
    },
    "shop_prompt": {"ru": "👇 Откройте наш магазин — витрина, фото, корзина и заказ в одном окне.",
                    "uz": "👇 Do'konimizni oching — vitrina, rasmlar, savat va buyurtma bitta oynada."},
    "shop_open": {"ru": "🛍 Открыть магазин", "uz": "🛍 Do'konni ochish"},
    "shop_open_app": {"ru": "🛍 Открыть магазин-приложение", "uz": "🛍 Do'kon ilovasini ochish"},
    "open_in_shop": {"ru": "🛍 Открыть в магазине", "uz": "🛍 Do'konda ochish"},
    "cancelled": {"ru": "Отменено.", "uz": "Bekor qilindi."},
    "main_menu": {"ru": "Главное меню", "uz": "Asosiy menyu"},
    # каталог
    "catalog_empty": {"ru": "Каталог пока пуст. Загляните позже!", "uz": "Katalog hozircha bo'sh. Keyinroq kiring!"},
    "catalog_title": {"ru": "🛍 <b>Каталог ELTA</b> — {n} товаров\nВыберите категорию:",
                      "uz": "🛍 <b>ELTA katalogi</b> — {n} ta tovar\nBo'limni tanlang:"},
    "catalog_changed": {"ru": "Каталог обновился, откройте его заново", "uz": "Katalog yangilandi, uni qaytadan oching"},
    "new": {"ru": "🆕 Новинки", "uz": "🆕 Yangi tovarlar"},
    "all_cats": {"ru": "⬅️ Все категории", "uz": "⬅️ Barcha bo'limlar"},
    "choose_product": {"ru": "Выберите товар:", "uz": "Tovarni tanlang:"},
    # карточка товара
    "article": {"ru": "🏷 Артикул", "uz": "🏷 Artikul"},
    "price": {"ru": "💰 Цена", "uz": "💰 Narxi"},
    "add_cart": {"ru": "➕ В корзину", "uz": "➕ Savatga"},
    "in_cart": {"ru": " (в корзине: {n})", "uz": " (savatda: {n} ta)"},
    "buy_now": {"ru": "⚡ Купить сейчас", "uz": "⚡ Darhol buyurtma berish"},
    "ask_manager": {"ru": "💬 Спросить у менеджера", "uz": "💬 Menejerdan so'rash"},
    "channel_post": {"ru": "📢 Пост в канале", "uz": "📢 Kanaldagi post"},
    "back": {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga"},
    "item_gone": {"ru": "Этот товар больше не доступен.", "uz": "Bu tovar endi mavjud emas."},
    "added": {"ru": "✅ Добавлено в корзину (шт.: {n})", "uz": "✅ Savatga qo'shildi ({n} ta)"},
    # корзина
    "cart_empty": {"ru": "🛒 Корзина пуста.\nОткройте «🛍 Каталог», чтобы выбрать товары.",
                   "uz": "🛒 Savat bo'sh.\nTovar tanlash uchun «🛍 Katalog»ni oching."},
    "cart_empty_short": {"ru": "Корзина пуста", "uz": "Savat bo'sh"},
    "cart_title": {"ru": "🛒 <b>Ваша корзина</b>\n", "uz": "🛒 <b>Savatingiz</b>\n"},
    "total": {"ru": "Итого", "uz": "Jami"},
    "clear": {"ru": "🗑 Очистить", "uz": "🗑 Tozalash"},
    "checkout": {"ru": "✅ Оформить заказ", "uz": "✅ Buyurtma berish"},
    "cart_cleared": {"ru": "🛒 Корзина очищена.", "uz": "🛒 Savat tozalandi."},
    # контакты и поиск
    "contacts": {"ru": "<b>ELTA</b> — снаряжение для кемпинга, охоты и походов\n\n{phones}\n💬 Менеджер: @{m}\n📢 Канал: {ch}",
                 "uz": "<b>ELTA</b> — kemping, ov va sayohat uchun jihozlar\n\n{phones}\n💬 Menejer: @{m}\n📢 Kanal: {ch}"},
    "write_manager": {"ru": "💬 Написать менеджеру", "uz": "💬 Menejerga yozish"},
    "open_channel": {"ru": "📢 Открыть канал", "uz": "📢 Kanalni ochish"},
    "search_prompt": {"ru": "🔎 Введите название, бренд или артикул.\nНапример: <i>палатка</i>, <i>KAILAS</i>, <i>фонарь</i>",
                      "uz": "🔎 Tovar nomi, brendi yoki artikulini yozing.\nTovar nomlari rus tilida, masalan: "
                            "<i>палатка</i>, <i>KAILAS</i>, <i>фонарь</i>"},
    "not_found": {"ru": "По запросу «{q}» ничего не нашлось 😔\nПопробуйте другое слово или спросите менеджера @{m}",
                  "uz": "«{q}» bo'yicha hech narsa topilmadi 😔\nBoshqa so'z bilan qidiring yoki menejerdan so'rang: @{m}"},
    "found": {"ru": "🔎 Найдено: {n}", "uz": "🔎 Topildi: {n} ta"},
    # оформление заказа
    "co_name": {"ru": "📝 <b>Оформление заказа</b>\n\nКак к вам обращаться? Напишите имя.",
                "uz": "📝 <b>Buyurtma berish</b>\n\nSizga qanday murojaat qilaylik? Ismingizni yozing."},
    "co_phone": {"ru": "📱 Отправьте номер телефона кнопкой ниже или напишите его.",
                 "uz": "📱 Telefon raqamingizni pastdagi tugma orqali yuboring yoki yozing."},
    "send_my_number": {"ru": "📱 Отправить мой номер", "uz": "📱 Raqamimni yuborish"},
    "bad_phone": {"ru": "Похоже, номер неполный. Напишите в формате +998 XX XXX XX XX",
                  "uz": "Raqam to'liq emasga o'xshaydi. +998 XX XXX XX XX ko'rinishida yozing"},
    "co_address": {"ru": "🚚 Укажите город/адрес доставки или напишите «самовывоз».\nМожно добавить комментарий (размер, цвет и т.п.).",
                   "uz": "🚚 Yetkazib berish shahri va manzilini yozing yoki «olib ketaman» deb yozing.\n"
                         "Izoh ham qo'shishingiz mumkin (o'lcham, rang va h.k.)."},
    "pickup": {"ru": "Самовывоз", "uz": "Olib ketaman"},
    "check_order": {"ru": "Проверьте заказ 👇", "uz": "Buyurtmani tekshiring 👇"},
    "confirm": {"ru": "✅ Подтвердить", "uz": "✅ Tasdiqlash"},
    "cancel_inline": {"ru": "❌ Отмена", "uz": "❌ Bekor qilish"},
    "order_cancelled": {"ru": "Заказ отменён. Товары остались в корзине.",
                        "uz": "Buyurtma bekor qilindi. Tovarlar savatda qoldi."},
    "order_ok": {"ru": "✅ <b>Заказ принят!</b>\n\n{items}\n\n💰 Итого: <b>{total}</b>{address}\n\n"
                       "Менеджер скоро свяжется с вами для подтверждения. Спасибо, что выбрали ELTA! ⛰️",
                 "uz": "✅ <b>Buyurtma qabul qilindi!</b>\n\n{items}\n\n💰 Jami: <b>{total}</b>{address}\n\n"
                       "Menejer tez orada tasdiqlash uchun siz bilan bog'lanadi. ELTA'ni tanlaganingiz uchun rahmat! ⛰️"},
    # ошибки при заказе из магазина (сервер)
    "err_request": {"ru": "Некорректный запрос", "uz": "Noto'g'ri so'rov"},
    "err_auth": {"ru": "Не удалось подтвердить данные Telegram. Откройте магазин через бота",
                 "uz": "Telegram ma'lumotlarini tasdiqlab bo'lmadi. Do'konni bot orqali oching"},
    "err_open_bot": {"ru": "Откройте магазин через кнопку в боте", "uz": "Do'konni botdagi tugma orqali oching"},
    "err_session": {"ru": "Сессия устарела — закройте и снова откройте магазин",
                    "uz": "Sessiya eskirgan — do'konni yopib, qaytadan oching"},
    "err_wait": {"ru": "Заказ уже отправлен, подождите несколько секунд", "uz": "Buyurtma yuborildi, bir necha soniya kuting"},
    "err_empty": {"ru": "Корзина пуста или товары больше не доступны", "uz": "Savat bo'sh yoki tovarlar endi mavjud emas"},
    "err_name": {"ru": "Укажите имя", "uz": "Ismingizni yozing"},
    "err_phone": {"ru": "Укажите номер телефона полностью", "uz": "Telefon raqamini to'liq yozing"},
    "err_address": {"ru": "Укажите адрес доставки", "uz": "Yetkazib berish manzilini yozing"},
}

# названия категорий (сами категории в каталоге — на русском)
CATEGORIES_UZ = {
    "Одежда": "Kiyim", "Обувь": "Poyabzal", "Палатки и сон": "Chodirlar va uyqu", "Кухня и огонь": "Oshxona va olov",
    "Мебель для кемпинга": "Kemping mebeli", "Фонари": "Fonarlar", "Рюкзаки и снаряжение": "Ryukzaklar va jihozlar",
}


def t(lang: str, key: str, **kw) -> str:
    entry = T[key]
    text = entry.get(lang) or entry["ru"]
    return text.format(**kw) if kw else text


def cat_name(category: str, lang: str) -> str:
    """'👕 Одежда' -> '👕 Kiyim' для узбекского; для русского без изменений."""
    if lang != "uz":
        return category
    emoji, _, name = category.partition(" ")
    if name in CATEGORIES_UZ:
        return f"{emoji} {CATEGORIES_UZ[name]}"
    return CATEGORIES_UZ.get(category, category)


def all_variants(key: str) -> set[str]:
    """Все языковые варианты кнопки — чтобы бот понимал нажатие на любом языке."""
    return set(T[key].values())
