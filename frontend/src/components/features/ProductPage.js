// Страница товара
function formatDesc(text) {
  const lines = text.split("\n").map(l => l.trim()).filter(Boolean).slice(1)   // 1-я строка — заголовок поста
    .filter(l => !/готов к любым испытаниям/i.test(l));
  let out = "", list = [];
  const flush = () => { if (list.length) { out += "<ul>" + list.map(x => `<li>${x}</li>`).join("") + "</ul>"; list = []; } };
  for (let l of lines) {
    const bullet = l.match(/^(?:✅|☑️|✔️|•|-|—|▪️|🔹|🔸)\s*(.+)$/u);
    const body = bullet ? bullet[1] : l;
    const kv = body.match(/^([^:]{2,42}):\s*(.+)$/);
    const html = kv ? `<b>${esc(kv[1])}:</b> ${esc(kv[2])}` : esc(body);
    if (bullet) { list.push(html); continue; }
    flush();
    if (/:\s*$/.test(l) && l.length < 60) out += `<h4>${esc(l.replace(/:\s*$/, ""))}</h4>`;
    else out += `<p>${html}</p>`;
  }
  flush();
  return out;
}

function renderProduct(pg, p, soft) {
  if (!p) { closePage(); return; }
  const q = cart[p.id] || 0;
  if (!soft) {
    const photos = p.photos.length ? p.photos : [p.thumb];
    pg.innerHTML = bar(L("product")) + `<div class="page-in">
      <div class="gallery"><div class="slides" id="slides">${photos.map((u, i) => `<img src="${esc(u)}" alt="${esc(p.title)} — ${L("photo")} ${i + 1}" ${i ? 'loading="lazy"' : ""}>`).join("")}</div>
        ${photos.length > 1 ? `<span class="counter" id="counter">1 / ${photos.length}</span><div class="dots" id="dots">${photos.map((_, i) => `<i class="${i ? "" : "on"}"></i>`).join("")}</div>` : ""}</div>
      ${photos.length > 1 ? `<div class="thumbs" id="thumbs">${photos.map((u, i) => `<button class="${i ? "" : "on"}" data-slide="${i}" aria-label="${L("photo")} ${i + 1}"><img src="${esc(u)}" alt="" loading="lazy"></button>`).join("")}</div>` : ""}
      <div class="p-body">
        <div class="p-cat">${esc(catLabel(p.category))}</div>
        <h1 class="p-title">${esc(p.title)}</h1>
        <div class="p-meta"><span class="p-price">${money(p.price)}</span>${p.article ? `<button class="art" data-copy="${esc(p.article)}">${L("art")} ${esc(p.article)}</button>` : ""}${favButton(p.id, " big")}</div>
        <div id="incart"></div>
        <div class="p-actions">
          <button class="btn2" data-link="${esc(DATA.manager_url)}">${ICON.chat} ${L("ask")}</button>
          <button class="btn2" data-link="${esc(p.post_url)}">${ICON.tg} ${L("post")}</button>
        </div>
        <div class="desc">${formatDesc(p.description)}</div>
      </div></div>`;
    const slides = $("#slides", pg);
    if (slides && photos.length > 1) slides.addEventListener("scroll", () => {
      const i = Math.round(slides.scrollLeft / slides.clientWidth);
      $("#counter", pg).textContent = `${i + 1} / ${photos.length}`;
      [...$("#dots", pg).children].forEach((d, k) => d.classList.toggle("on", k === i));
      [...$("#thumbs", pg).children].forEach((d, k) => d.classList.toggle("on", k === i));
    }, { passive: true });
  }
  $("#incart", pg).innerHTML = q ? `<div class="incart"><span>${L("in_cart")}</span><div class="stepper"><button data-dec="${p.id}">−</button><span>${q}</span><button data-inc="${p.id}">+</button></div></div>` : "";
  if (q) setMain(`${L("go_cart")} · ${money(cartTotal())}`, () => openPage({ v: "cart" }));
  else setMain(`${L("to_cart")} · ${money(p.price)}`, () => { setQty(p.id, 1); haptic("medium"); toast(L("added")); });
}
