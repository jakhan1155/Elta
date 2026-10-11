// Нижнее меню и лист «Разделы»
function setTab(k) { [...$("#tabbar").children].forEach(b => b.classList.toggle("on", b.dataset.tab === k)); }
function openSheet() {  // «Разделы»: все категории списком
  $("#sheetIn").innerHTML = `<div class="sheet-grip"></div><h3>${L("tab_cats")}</h3>` + sectionList().map(c => {
    const special = c === "all" || c === "fav";
    const n = c === "all" ? DATA.products.length : DATA.products.filter(p => c === "fav" ? isFav(p.id) : p.category === c).length;
    const known = !special && CAT_CIRCLES[stripEmoji(c)];
    const first = !special && DATA.products.find(p => p.category === c);
    const im = c === "all" ? $('[data-tab="cats"] svg').outerHTML : c === "fav" ? `<span class="heart">${ICON.heart}</span>`
      : `<img src="${known ? `images/brand/cut-${known[1]}.png` : esc(first.thumb)}" alt="">`;
    const name = c === "all" ? L("all") : c === "fav" ? L("favs") : catLabel(c);
    return `<button class="sheet-cat${c === cat ? " on" : ""}" data-sheet-cat="${esc(c)}"><span class="im">${im}</span>${esc(name)}<em>${n}</em></button>`;
  }).join("");
  $("#sheet").classList.add("open"); setTab("cats");
}
function closeSheet() { $("#sheet").classList.remove("open"); setTab("home"); }

// Листаем вниз (смотрим товары) — меню уезжает вниз; чуть вверх или у самого верха — возвращается
(() => {
  let lastY = scrollY;
  addEventListener("scroll", () => {
    const y = scrollY, dy = y - lastY;
    if (Math.abs(dy) < 8 && y > 120) return;  // мелкое дрожание пальца не считаем
    document.body.classList.toggle("nav-hidden", dy > 0 && y > 120);
    lastY = y;
  }, { passive: true });
})();
