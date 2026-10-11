// Избранное (❤️): id товаров. Хранится в браузере и в облаке Telegram — видно на всех устройствах покупателя
const cloud = tg && tg.CloudStorage && tg.isVersionAtLeast && tg.isVersionAtLeast("6.9") ? tg.CloudStorage : null;

function loadFavs() {
  try { return new Set(JSON.parse(localStorage.getItem("elta_favs") || "[]").map(String)); } catch (e) { return new Set(); }
}
function saveFavs() {
  const json = JSON.stringify([...favs]);
  try { localStorage.setItem("elta_favs", json); } catch (e) {}
  if (cloud) try { cloud.setItem("favs", json); } catch (e) {}
}
function syncFavsFromCloud() {  // избранное с другого телефона/компьютера добавляется к здешнему
  if (!cloud) return Promise.resolve();
  return new Promise(resolve => {
    try {
      cloud.getItem("favs", (err, val) => {
        if (!err && val) try { JSON.parse(val).forEach(id => favs.add(String(id))); } catch (e) {}
        resolve();
      });
    } catch (e) { resolve(); }
    setTimeout(resolve, 1500);  // облако не ответило — не ждём
  });
}
function isFav(id) { return favs.has(String(id)); }
function toggleFav(id) {
  id = String(id);
  favs.has(id) ? favs.delete(id) : favs.add(id);
  saveFavs();
  return favs.has(id);
}

let favs = loadFavs();
