// Страница корзины
function renderCart(pg) {
  const items = Object.entries(cart).filter(([id]) => byId[id]);
  if (!items.length) {
    pg.innerHTML = bar(L("cart")) + `<div class="empty" style="padding-top:90px"><b>${L("cart_empty")}</b>${L("cart_empty_sub")}</div>`;
    setMain(L("back_catalog"), goHome);
    return;
  }
  pg.innerHTML = bar(L("cart")) + `<div class="page-in">` + items.map(([id, q]) => {
    const p = byId[id];
    return `<div class="c-item">
      <div class="ph" data-open="${p.id}"><img src="${esc(p.thumb)}" alt=""></div>
      <div class="mid"><div class="t" data-open="${p.id}">${esc(p.title)}</div><div class="u">${money(p.price)} ${L("per_pc")}</div>
        <div class="bottom"><div class="stepper"><button data-dec="${p.id}" aria-label="${L("less")}">−</button><span>${q}</span><button data-inc="${p.id}" aria-label="${L("more")}">+</button></div>
        <span class="sum">${money(p.price * q)}</span></div></div></div>`;
  }).join("") + `<div class="total"><span>${L("total")}</span><b>${money(cartTotal())}</b></div>
    <div class="note"><div class="note-ttl">${L("note_ttl")}</div>
      <div class="step"><span class="n">1</span><div><b>${L("s1")}</b><span>${L("s1d")}</span></div></div>
      <div class="step"><span class="n">2</span><div><b>${L("s2")}</b><span>${L("s2d")}</span></div></div>
      <div class="step"><span class="n">3</span><div><b>${L("s3")}</b><span>${L("s3d")}</span></div></div></div></div>`;
  setMain(`${L("checkout")} · ${money(cartTotal())}`, () => openPage({ v: "checkout" }));
}
