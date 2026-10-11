// Telegram WebApp: объект tg, вибрация, цвет шапки, ссылки, сообщения
const tg = window.Telegram && window.Telegram.WebApp;
const inTg = !!(tg && tg.initData);

const haptic = (t = "light") => { try { tg.HapticFeedback.impactOccurred(t); } catch (e) {} };
const hapticOk = () => { try { tg.HapticFeedback.notificationOccurred("success"); } catch (e) {} };

const tgColors = c => { try { tg.setHeaderColor(c); tg.setBackgroundColor(c); } catch (e) {} };

function alertMsg(msg) { if (inTg) tg.showAlert(msg); else alert(msg); }
function openLink(url) {
  if (inTg && url.startsWith("https://t.me/")) tg.openTelegramLink(url);
  else if (inTg) tg.openLink(url);
  else window.open(url, "_blank");
}
