// Выбор бренда
// меню брендов: только бренды выбранной категории, с числом товаров
function openBrandMenu() {
  const inCat = DATA.products.filter(inSection);
  const counts = {};
  inCat.forEach(p => { const b = brandOf(p); if (b) counts[b] = (counts[b] || 0) + 1; });
  const list = [["all", L("all_brands"), inCat.length], ...Object.entries(counts).sort((a, b) => b[1] - a[1]).map(([b, n]) => [b, b, n])];
  const m = $("#brandMenu");
  m.innerHTML = list.map(([v, label, n]) => `<button class="${v === brand ? "on" : ""}" data-brand="${esc(v)}">${esc(label)}<i>${n}</i></button>`).join("");
  m.classList.add("open");
}
$("#brandBtn").onclick = e => { e.stopPropagation(); haptic(); $("#brandMenu").classList.contains("open") ? $("#brandMenu").classList.remove("open") : openBrandMenu(); };
$("#brandMenu").addEventListener("click", e => {
  const b = e.target.closest("[data-brand]"); if (!b) return;
  e.stopPropagation(); haptic(); brand = b.dataset.brand; $("#brandMenu").classList.remove("open"); renderGrid();
});
document.addEventListener("click", e => { if (!e.target.closest(".brand-wrap")) $("#brandMenu").classList.remove("open"); });
