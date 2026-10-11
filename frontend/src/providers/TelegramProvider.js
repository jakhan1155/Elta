// Подготовка окна Telegram: развернуть, цвета, кнопка «Назад»
/* ---------- Telegram ---------- */
if (tg) {
  tg.ready();
  tg.expand();
  try { tg.setHeaderColor("#13231b"); tg.setBackgroundColor("#13231b"); } catch (e) {}
  try { tg.setBottomBarColor && tg.setBottomBarColor("#13231b"); } catch (e) {}
  try { tg.disableVerticalSwipes && tg.disableVerticalSwipes(); } catch (e) {}
  tg.BackButton.onClick(() => closePage());
}
if (inTg) document.documentElement.classList.add("in-tg");
