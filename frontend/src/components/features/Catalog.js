// Витрина: фильтр и сетка товаров
/* ---------- витрина ---------- */
// товар в выбранном разделе: «все», «❤️ избранное» или категория
const inSection = p => cat === "all" || (cat === "fav" ? isFav(p.id) : p.category === cat);

function filtered() {
  const words = query.toLowerCase().split(/\s+/).filter(Boolean);
  return DATA.products.filter(p => {
    if (!inSection(p)) return false;
    if (brand !== "all" && brandOf(p) !== brand) return false;
    if (!words.length) return true;
    const hay = (p.title + " " + (p.article || "") + " " + p.description).toLowerCase();
    return words.every(w => hay.includes(w));
  });
}

function renderGrid() {
  const list = filtered();
  $("#secTitle").textContent = query ? L("search") : cat === "all" ? L("all") : cat === "fav" ? L("favs") : catLabel(cat);
  $("#shown").textContent = list.length + " " + L("pcs");
  const bb = $("#brandBtn");
  bb.textContent = (brand === "all" ? L("brand") : brand) + " ▾";
  bb.classList.toggle("on", brand !== "all");
  $("#grid").innerHTML = list.length ? list.map(cardHtml).join("") :
    `<div class="empty"><b>${L("nothing")}</b>${L("nothing_sub")}</div>`;
}
