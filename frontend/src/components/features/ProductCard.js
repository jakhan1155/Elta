// Карточка товара в сетке
function favButton(id, extra = "") {  // сердечко «в избранное» (и в карточке, и на странице товара)
  return `<button class="fav${isFav(id) ? " on" : ""}${extra}" data-fav="${id}" aria-label="${L("favs")}">${ICON.heart}</button>`;
}
function cardHtml(p, i) {
  const q = cart[p.id] || 0;
  const ctl = q
    ? `<div class="qty-pill"><button data-dec="${p.id}" aria-label="${L("less")}">−</button><span>${q}</span><button data-inc="${p.id}" aria-label="${L("more")}">+</button></div>`
    : `<button class="add" data-inc="${p.id}" aria-label="${L("to_cart")}">${ICON.plus}</button>`;
  return `<article class="card" data-open="${p.id}" style="animation-delay:${Math.min(i, 12) * 30}ms">
    <div class="ph"><img src="${esc(p.thumb)}" alt="${esc(p.title)}" loading="lazy"></div>
    ${p.isNew ? '<span class="new">NEW</span>' : ""}
    ${favButton(p.id)}
    <div class="info"><h3 class="t">${esc(p.title)}</h3>
      <div class="row"><span class="price">${money(p.price)}</span>${ctl}</div></div>
  </article>`;
}
