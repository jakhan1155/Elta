// Запуск магазина: тексты, события, загрузка каталога
function applyStaticTexts() {
  document.documentElement.lang = LANG;
  $("#q").placeholder = L("search"); $("#q").setAttribute("aria-label", L("search_aria"));
  $("#qClear").setAttribute("aria-label", L("clear_search")); $("#cartBtn").setAttribute("aria-label", L("cart"));
  ["home", "cats", "cart", "manager"].forEach(k => { $(`[data-tab="${k}"] span`).textContent = L("tab_" + k); });
}

/* ---------- события ---------- */
document.addEventListener("click", e => {
  const t = e.target;
  let el;
  if ((el = t.closest("[data-fav]"))) { onFavClick(el); return; }  // раньше data-open: сердечко лежит на карточке
  if ((el = t.closest("[data-inc]"))) { const id = el.dataset.inc; setQty(id, (cart[id] || 0) + 1); haptic(); if (!stack.length && cart[id] === 1) toast(L("added")); return; }
  if ((el = t.closest("[data-dec]"))) { const id = el.dataset.dec; setQty(id, (cart[id] || 0) - 1); haptic(); return; }
  if ((el = t.closest("[data-open]"))) { haptic(); const id = +el.dataset.open; const top = stack[stack.length - 1];
    if (top && top.v === "product" && top.id === id) return; openPage({ v: "product", id }); return; }
  if ((el = t.closest("[data-back]"))) { closePage(); return; }
  if ((el = t.closest("[data-link]"))) { e.preventDefault(); openLink(el.dataset.link); return; }
  if ((el = t.closest("[data-slide]"))) { const s = $("#slides"); s.scrollTo({ left: s.clientWidth * +el.dataset.slide, behavior: "smooth" }); return; }
  if ((el = t.closest("[data-copy]"))) { try { navigator.clipboard.writeText(el.dataset.copy); toast(L("copied")); } catch (err) {} return; }
  if ((el = t.closest("[data-tile]"))) { haptic(); selectCat(el.dataset.tile); return; }  // плитка категории → раздел в каталоге
  if ((el = t.closest("[data-sheet-cat]"))) { haptic(); closeSheet(); selectCat(el.dataset.sheetCat); return; }
  if ((el = t.closest("[data-sheet-close]"))) { closeSheet(); return; }
  if ((el = t.closest("[data-tab]"))) {
    haptic();
    const k = el.dataset.tab;
    if (k === "home") { closeSheet(); if (cat !== "all" || query || brand !== "all") selectCat("all", true); window.scrollTo({ top: 0, behavior: "smooth" }); }
    if (k === "cats") $("#sheet").classList.contains("open") ? closeSheet() : openSheet();
    if (k === "cart") openPage({ v: "cart" });
    if (k === "manager") openLink(DATA.manager_url);
    return;
  }
});

function onFavClick(el) {
  const on = toggleFav(el.dataset.fav);
  haptic(on ? "medium" : "light");
  document.querySelectorAll(`[data-fav="${el.dataset.fav}"]`).forEach(b => b.classList.toggle("on", on));
  toast(L(on ? "fav_added" : "fav_removed"));
  const wasFav = cat === "fav";
  if (wasFav && !DATA.products.some(p => isFav(p.id))) cat = "all";  // убрали последнее — к «Все товары»
  renderTiles();
  if (wasFav && !stack.length) renderGrid();  // в разделе «Избранное» снятый товар сразу исчезает
}

async function load() {
  applyStaticTexts();
  try {
    [DATA] = await Promise.all([fetchCatalog(), fetchLang(), syncFavsFromCloud()]);
    applyStaticTexts();
  } catch (e) {
    $("#grid").innerHTML = `<div class="empty"><b>${L("load_err")}</b>${L("load_err_sub")}</div>`;
    introCatalogReady();
    return;
  }
  introCatalogReady();
  const newest = [...DATA.products].sort((a, b) => b.id - a.id).slice(0, 6).map(p => p.id);
  DATA.products.forEach(p => { p.price = parseFloat(p.price) || 0; p.isNew = newest.includes(p.id); byId[p.id] = p; });
  Object.keys(cart).forEach(id => { if (!byId[id]) delete cart[id]; });
  saveCart();

  renderTiles();
  renderFooter();
  renderChips(); updateBadge(); refresh();

  // открыть конкретный товар: кнопка из чата (?p=123) или ссылка t.me/bot?startapp=p_123
  const sp = (tg && tg.initDataUnsafe && tg.initDataUnsafe.start_param) || "";
  const pid = new URLSearchParams(location.search).get("p") || (sp.match(/^p_(\d+)$/) || [])[1];
  if (pid && byId[pid]) openPage({ v: "product", id: +pid });
}

load();
