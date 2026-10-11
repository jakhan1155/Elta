// Интро: логотип загорается и улетает в шапку
/* ---------- интро ---------- */
const introEl = document.getElementById("intro");
let introActive = !!introEl, introMinDone = false, catalogReady = false, pendingMain = null, introSound = null;

function finishIntro() {
  if (!introActive) return;
  introActive = false;
  try { localStorage.setItem("elta_intro_v14", window.ELTA_DAY); } catch (e) {}
  if (introSound) introSound.finale();  // «фчик» под полёт логотипа
  tgColors("#13231b");
  // логотип улетает точно в логотип в шапке магазина
  const word = introEl.querySelector(".intro-word"), target = document.querySelector(".logo img");
  window.scrollTo(0, 0);
  const a = word.getBoundingClientRect(), b = target.getBoundingClientRect();
  introEl.classList.add("out");
  if (a.height && b.height) {
    const s = b.height / a.height;
    const dx = b.left + b.width / 2 - (a.left + a.width / 2), dy = b.top + b.height / 2 - (a.top + a.height / 2);
    word.style.transform = `translate(${dx}px, ${dy}px) scale(${s})`;
  }
  setTimeout(() => {  // логотип приземлился в шапку — открываем магазин
    document.body.classList.remove("intro-on");
    introEl.classList.add("gone");
    document.body.classList.add("reveal");
    haptic("soft");
    if (pendingMain) { setMain(...pendingMain); pendingMain = null; }
    setTimeout(() => introEl.remove(), 500);
  }, 1010);
}
function introCatalogReady() { catalogReady = true; if (introMinDone) finishIntro(); }
if (introEl) {
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  tgColors("#0d1c14");  // шапка Telegram в цвет интро
  document.body.classList.add("intro-on");
  const start = () => {
    if (introEl.classList.contains("go")) return;
    introEl.classList.add("go");
    introSound = createIntroSound();
    if (introSound) introSound.play();
    setTimeout(() => {  // удар баса: буквы вспыхивают, сияние, вибрация
      if (!introActive) return;
      introEl.classList.add("hit");
      haptic("heavy");
    }, 850);
    setTimeout(() => { introMinDone = true; if (catalogReady) finishIntro(); }, reduced ? 900 : 2900);
    setTimeout(finishIntro, 8000);  // медленный интернет — не держим интро дольше 8 сек
  };
  // ждём картинки логотипа, чтобы буквы появлялись целиком
  const imgs = [...introEl.querySelectorAll("img")].map(i => i.decode ? i.decode().catch(() => {}) : null);
  Promise.race([Promise.all(imgs), new Promise(r => setTimeout(r, 900))]).then(start, start);
  introEl.addEventListener("click", finishIntro);
} else {
  document.body.classList.add("reveal");
}
