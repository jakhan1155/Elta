// Подвал: «Не нашли нужное?», телефоны и канал
function renderFooter() {
  const channel = DATA.channel_url.replace(/^https?:\/\/t\.me\//, "@");
  $("#foot").innerHTML = `<div class="help"><div class="help-ttl">${L("help_title")}</div>
      <div class="help-sub">${L("help_sub")}</div>
      <button class="help-btn" data-link="${esc(DATA.manager_url)}">${ICON.tg}${L("help_tg")}</button></div>
    <div class="foot-info">${DATA.phones.map(p => `<a href="tel:${esc(p.replace(/[^\d+]/g, ""))}">${esc(p)}</a>`).join(" · ")}<br>
      <a href="#" class="foot-ch" data-link="${esc(DATA.channel_url)}">${L("channel")} ${esc(channel)}</a></div>`;
}
