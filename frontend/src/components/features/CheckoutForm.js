// Оформление заказа
const form = { name: "", phone: "", delivery: "delivery", address: "", comment: "" };
(() => {
  const u = tg && tg.initDataUnsafe && tg.initDataUnsafe.user;
  if (u) form.name = [u.first_name, u.last_name].filter(Boolean).join(" ");
  try { Object.assign(form, JSON.parse(localStorage.getItem("elta_form") || "{}")); } catch (e) {}
})();
function saveForm() { try { localStorage.setItem("elta_form", JSON.stringify(form)); } catch (e) {} }

function renderCheckout(pg, soft) {
  const items = Object.entries(cart).filter(([id]) => byId[id]);
  if (!items.length) { goHome(); return; }
  const canShare = inTg && typeof tg.requestContact === "function" && tg.isVersionAtLeast && tg.isVersionAtLeast("6.9");
  if (!soft) {
    pg.innerHTML = bar(L("co_title")) + `<div class="page-in"><div class="form">
      <div class="field" id="f-name"><label for="name">${L("name")}</label><input id="name" autocomplete="name" value="${esc(form.name)}" placeholder="${L("name_ph")}"><div class="hint">${L("err_name")}</div></div>
      <div class="field" id="f-phone"><label for="phone">${L("phone")}</label><input id="phone" type="tel" inputmode="tel" autocomplete="tel" value="${esc(form.phone)}" placeholder="+998 __ ___ __ __"><div class="hint">${L("err_phone")}</div>
        ${canShare ? `<button class="share-phone" id="sharePhone">${L("tg_phone")}</button>` : ""}</div>
      <div class="field"><label>${L("receive")}</label><div class="seg" id="seg">
        <button data-del="delivery" class="${form.delivery === "delivery" ? "on" : ""}">${L("delivery")}</button>
        <button data-del="pickup" class="${form.delivery === "pickup" ? "on" : ""}">${L("pickup")}</button></div></div>
      <div class="field" id="f-address" ${form.delivery === "pickup" ? 'style="display:none"' : ""}><label for="address">${L("address")}</label><textarea id="address" rows="2" placeholder="${L("address_ph")}">${esc(form.address)}</textarea><div class="hint">${L("err_address")}</div></div>
      <div class="field"><label for="comment">${L("comment")} <span style="font-weight:500">${L("optional")}</span></label><textarea id="comment" rows="2" placeholder="${L("comment_ph")}">${esc(form.comment)}</textarea></div>
      <div class="summary">${items.map(([id, q]) => `<div><span>${esc(byId[id].title)} × ${q}</span><span>${money(byId[id].price * q)}</span></div>`).join("")}
        <div class="tot"><span>${L("total")}</span><span>${money(cartTotal())}</span></div></div>
    </div></div>`;
    ["name", "phone", "address", "comment"].forEach(k => $("#" + k, pg).addEventListener("input", e => {
      form[k] = e.target.value; saveForm(); e.target.closest(".field").classList.remove("err");
    }));
    $("#seg", pg).addEventListener("click", e => {
      const b = e.target.closest("[data-del]"); if (!b) return;
      form.delivery = b.dataset.del; saveForm(); haptic();
      [...$("#seg", pg).children].forEach(x => x.classList.toggle("on", x === b));
      $("#f-address", pg).style.display = form.delivery === "pickup" ? "none" : "";
    });
    const sp = $("#sharePhone", pg);
    if (sp) sp.onclick = () => tg.requestContact((ok, res) => {
      const ph = ok && res && res.responseUnsafe && res.responseUnsafe.contact && res.responseUnsafe.contact.phone_number;
      if (ph) { form.phone = ph.startsWith("+") ? ph : "+" + ph; $("#phone", pg).value = form.phone; saveForm(); $("#f-phone", pg).classList.remove("err"); }
    });
  }
  setMain(L("confirm"), submitOrder);
}

let sending = false;
async function submitOrder() {
  if (sending) return;
  const pg = $("#page");
  const bad = [];
  if (form.name.trim().length < 2) bad.push("f-name");
  if (form.phone.replace(/\D/g, "").length < 9) bad.push("f-phone");
  if (form.delivery === "delivery" && form.address.trim().length < 3) bad.push("f-address");
  pg.querySelectorAll(".field").forEach(f => f.classList.toggle("err", bad.includes(f.id)));
  if (bad.length) { try { tg.HapticFeedback.notificationOccurred("error"); } catch (e) {} $("#" + bad[0], pg).scrollIntoView({ behavior: "smooth", block: "center" }); return; }
  if (!inTg) { alertMsg(L("only_tg")); return; }
  sending = true;
  tg.MainButton.showProgress(false);
  try {
    const res = await postOrder({ items: Object.entries(cart).map(([id, qty]) => ({ id: +id, qty })), ...form });
    cart = {}; saveCart(); updateBadge(); renderGrid();
    hapticOk();
    stack.length = 0; openPage({ v: "done", total: res.total });
  } catch (e) {
    alertMsg(e.message + L("try_again"));
  } finally {
    sending = false;
    tg.MainButton.hideProgress();
  }
}
