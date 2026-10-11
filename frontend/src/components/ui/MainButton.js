// Главная кнопка внизу (в Telegram — MainButton, в браузере — своя)
let mainHandler = null;
function setMain(text, handler) {
  if (introActive) { pendingMain = [text, handler]; return; }
  mainHandler = handler;
  if (inTg) {
    if (!text) { tg.MainButton.hide(); return; }
    tg.MainButton.setParams({ text, color: "#f1efe2", text_color: "#13231b", is_active: true, is_visible: true });
  } else {
    $("#mainbar").classList.toggle("on", !!text);
    $("#mainbarBtn").textContent = text || "";
  }
}
if (inTg) tg.MainButton.onClick(() => mainHandler && mainHandler());
$("#mainbarBtn").onclick = () => mainHandler && mainHandler();
