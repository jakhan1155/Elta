// Заказ принят
function renderDone(pg, s) {
  pg.innerHTML = `<div class="done"><div class="mark">${ICON.check}</div>
    <h2>${L("done")}</h2>
    <p>${L("done_sub")}</p>
    <button class="btn2" style="max-width:280px;margin:0 auto" data-link="${esc(DATA.manager_url)}">${ICON.chat} ${L("write_manager")}</button></div>`;
  if (inTg) tg.BackButton.hide();
  setMain(L("back_catalog"), goHome);
}
