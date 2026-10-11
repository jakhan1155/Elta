// Корзина: хранится в браузере (localStorage)
/* ---------- корзина ---------- */
function loadCart() { try { return JSON.parse(localStorage.getItem("elta_cart") || "{}") || {}; } catch (e) { return {}; } }
function saveCart() { try { localStorage.setItem("elta_cart", JSON.stringify(cart)); } catch (e) {} }
function cartCount() { return Object.values(cart).reduce((a, b) => a + b, 0); }
function cartTotal() { return Object.entries(cart).reduce((s, [id, q]) => s + (byId[id] ? byId[id].price * q : 0), 0); }
function setQty(id, q) {
  id = String(id);
  if (q > 0) cart[id] = Math.min(q, 99); else delete cart[id];
  saveCart(); updateBadge(); refresh();
}

let cart = loadCart();
