// Страницы поверх витрины: открыть, закрыть, обновить
function refresh() {
  renderGrid();
  const top = stack[stack.length - 1];
  document.body.classList.toggle("paged", !!top);
  if (top) renderPage(top, true);
  else setMain("", null);  // на витрине корзина — во вкладке нижнего меню
}

/* ---------- страницы ---------- */
function openPage(state) {
  closeSheet();
  stack.push(state);
  document.body.classList.add("paged");
  renderPage(state);
  const pg = $("#page");
  pg.scrollTop = 0;
  requestAnimationFrame(() => pg.classList.add("open"));
  if (inTg) tg.BackButton.show();
}
function closePage() {
  stack.pop();
  if (!stack.length) {
    $("#page").classList.remove("open");
    if (inTg) tg.BackButton.hide();
    refresh();
  } else {
    renderPage(stack[stack.length - 1]);
    $("#page").scrollTop = 0;
  }
}
function goHome() { stack.length = 0; $("#page").classList.remove("open"); if (inTg) tg.BackButton.hide(); refresh(); }
function bar(title) { return `<div class="page-bar"><button class="back" data-back aria-label="${L("back")}">${ICON.back}</button><h3>${esc(title)}</h3></div>`; }

function renderPage(s, soft) {
  const pg = $("#page");
  if (s.v === "product") return renderProduct(pg, byId[s.id], soft);
  if (s.v === "cart") return renderCart(pg);
  if (s.v === "checkout") return renderCheckout(pg, soft);
  if (s.v === "done") return renderDone(pg, s);
}
