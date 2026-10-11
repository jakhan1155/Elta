// Решает до отрисовки, показывать ли интро
// Полное интро — при первом открытии за день; по ссылке на конкретный товар — сразу товар.
// ?intro=1 в адресе — показать интро принудительно (для проверки).
(function () {
  var d = new Date(), day = d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate();
  var w = window.Telegram && window.Telegram.WebApp, sp = (w && w.initDataUnsafe && w.initDataUnsafe.start_param) || "";
  var seen = null;
  try { seen = localStorage.getItem("elta_intro_v14"); } catch (e) {}
  var deep = /[?&]p=\d+/.test(location.search) || /^p_\d+$/.test(sp);
  var force = /[?&]intro=1/.test(location.search);
  window.ELTA_DAY = day;
  if (!force && (seen === day || deep)) document.getElementById("intro").remove();
})();
