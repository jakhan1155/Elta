// Помощники: поиск элементов, экранирование, формат цены, иконки, категории, бренды
const $ = (s, el = document) => el.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const money = n => (Math.round(n * 100) / 100).toLocaleString("ru-RU").replace(/ /g, " ") + "$";
const stripEmoji = s => s.replace(/^[^\p{L}\p{N}]+/u, "").trim();
const ICON = {
  plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
  back: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg>',
  chat: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M4 5h16v11H9l-5 4V5Z"/></svg>',
  tg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="m21 4-18 7 6 2 2 6 3-4 5 4 2-15Z"/></svg>',
  check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 5 5 9-10"/></svg>',
  heart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 20.5S3.5 15.4 3.5 9.3A4.6 4.6 0 0 1 12 6.8a4.6 4.6 0 0 1 8.5 2.5c0 6.1-8.5 11.2-8.5 11.2Z"/></svg>',
};
// круги категорий: короткое название + товар из канала, вырезанный без фона (images/brand/cut-*.png)
const CAT_CIRCLES = {
  "Одежда": ["Одежда", "odezhda"], "Обувь": ["Обувь", "obuv"], "Палатки и сон": ["Палатки", "palatki"],
  "Кухня и огонь": ["Кухня", "kuhnya"], "Мебель для кемпинга": ["Мебель", "mebel"], "Фонари": ["Фонари", "fonari2"],
  "Рюкзаки и снаряжение": ["Рюкзаки", "ryukzaki2"],
};

// бренды узнаём по названию товара (добавьте сюда новый бренд, когда он появится в канале)
const BRANDS = ["KAILAS", "Naturehike", "TOREAD", "Olight", "STANLEY", "Sea to Summit", "Mountain Hardwear", "Deerland", "ARB", "Camel", "Longsinger", "FOCUS"];
const brandOf = p => BRANDS.find(b => p.title.toLowerCase().includes(b.toLowerCase())) || null;
