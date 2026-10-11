// Шапка: поиск и корзина
function updateBadge() {
  const b = $("#badge"), n = cartCount();
  b.textContent = n; b.classList.toggle("on", n > 0);
  b.classList.remove("bump"); void b.offsetWidth; if (n) b.classList.add("bump");
  const tb = $("#tabBadge"); tb.textContent = n; tb.classList.toggle("on", n > 0);
}

$("#cartBtn").onclick = () => { haptic(); openPage({ v: "cart" }); };
function scrollToCatalog() { window.scrollTo({ top: $("#catalog").offsetTop - 76, behavior: "smooth" }); }
function setSearch(v) { query = v; $("#q").value = v; $("#searchBox").classList.toggle("has", !!v); if (v) { cat = "all"; brand = "all"; renderChips(); } renderGrid(); }

$("#q").addEventListener("input", e => {
  const first = !query && e.target.value;
  setSearch(e.target.value);
  // начали печатать — показываем результаты в каталоге (с задержкой: браузер сам двигает экран при фокусе на поле)
  if (first) setTimeout(scrollToCatalog, 120);
});
$("#q").addEventListener("keydown", e => { if (e.key === "Enter") { e.target.blur(); if (query) scrollToCatalog(); } });
$("#qClear").onclick = () => setSearch("");
addEventListener("scroll", () => $("#topbar").classList.toggle("scrolled", scrollY > 10), { passive: true });
