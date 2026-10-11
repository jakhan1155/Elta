// Запросы к серверу бота.
// Магазин может открываться с Vercel — тогда данные и фото берём с сервера бота (Render);
// если страницу отдаёт сам сервер бота (Render или компьютер) — запросы идут туда же.
const BOT_SERVER = "https://elta-6e7e.onrender.com/";
const API_BASE = /onrender\.com$|^127\.0\.0\.1$|^localhost$|trycloudflare\.com$/.test(location.hostname) ? "" : BOT_SERVER;
const apiUrl = path => API_BASE + path;

async function fetchCatalog() {  // товары, категории, контакты (ошибка сети — исключение)
  const r = await fetch(apiUrl("api/catalog"), { cache: "no-store" });
  const data = await r.json();
  if (API_BASE) data.products.forEach(p => {  // фото лежат на сервере бота
    p.thumb = p.thumb && apiUrl(p.thumb);
    p.photos = p.photos.map(apiUrl);
  });
  return data;
}

async function postOrder(order) {  // → { ok, total } или { ok: false, error }
  const r = await fetch(apiUrl("api/order"), {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ initData: tg.initData, lang: LANG, ...order }),
  });
  const res = await r.json().catch(() => ({}));
  if (!r.ok || !res.ok) throw new Error(res.error || L("send_fail"));
  return res;
}

async function fetchLang() {  // язык, выбранный в боте (кнопка меню «Магазин» открывается без ?lang=)
  if (!inTg) return;
  try {
    const r = await fetch(apiUrl("api/lang"), { method: "POST", headers: { "Content-Type": "application/json" },
                                                body: JSON.stringify({ initData: tg.initData }) });
    const res = await r.json();
    if (res.lang === "uz" || res.lang === "ru") LANG = res.lang;
  } catch (e) {}
  try { localStorage.setItem("elta_lang", LANG); } catch (e) {}
}
