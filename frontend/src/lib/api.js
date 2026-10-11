// Запросы к серверу бота
async function fetchCatalog() {  // товары, категории, контакты (ошибка сети — исключение)
  const r = await fetch("api/catalog", { cache: "no-store" });
  return r.json();
}

async function postOrder(order) {  // → { ok, total } или { ok: false, error }
  const r = await fetch("api/order", {
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
    const r = await fetch("api/lang", { method: "POST", headers: { "Content-Type": "application/json" },
                                        body: JSON.stringify({ initData: tg.initData }) });
    const res = await r.json();
    if (res.lang === "uz" || res.lang === "ru") LANG = res.lang;
  } catch (e) {}
  try { localStorage.setItem("elta_lang", LANG); } catch (e) {}
}
