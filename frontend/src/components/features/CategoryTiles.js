// Круги категорий
// разделы: «все», «❤️ избранное» (если что-то отмечено) и категории, где есть товары
function sectionList() {
  const favCount = DATA.products.filter(p => isFav(p.id)).length;
  return ["all", ...(favCount ? ["fav"] : []), ...DATA.categories.filter(c => DATA.products.some(p => p.category === c))];
}
function renderTiles() {  // круги категорий с зелёным кольцом, как истории в Instagram
  const list = sectionList();
  $("#tiles").innerHTML = list.map((c, i) => {
    let label, inner;
    if (c === "all") { label = L("all_short"); inner = `<span class="txt">${L("all_circle")}</span>`; }
    else if (c === "fav") { label = L("favs"); inner = `<span class="heart">${ICON.heart}</span>`; }
    else {
      const known = CAT_CIRCLES[stripEmoji(c)];
      const first = DATA.products.find(p => p.category === c);  // новая категория — фото её первого товара
      label = LANG === "uz" ? (window.ELTA_CIRCLES_UZ[stripEmoji(c)] || catLabel(c)) : known ? known[0] : stripEmoji(c);
      inner = `<img src="${known ? `images/brand/cut-${known[1]}.png` : esc(first.thumb)}" alt="">`;
    }
    return `<button class="tile${c === cat ? " on" : ""}" data-tile="${esc(c)}" style="animation-delay:${i * 35}ms">
      <span class="ring"><span class="im">${inner}</span></span><b>${esc(label)}</b></button>`;
  }).join("");
}
function renderChips() {  // подсветка выбранного круга категории
  [...$("#tiles").children].forEach(t => t.classList.toggle("on", t.dataset.tile === cat));
}

function selectCat(c, noScroll) {
  cat = c; brand = "all";
  if (query) { query = ""; $("#q").value = ""; $("#searchBox").classList.remove("has"); }
  renderChips(); renderGrid(); if (!noScroll) scrollToCatalog();
}
