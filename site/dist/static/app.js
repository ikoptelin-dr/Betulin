/* Без внешних запросов. Отметки приёма хранятся только в браузере. */
(function () {
  var KEY = "betula-tracker";
  var boxes = document.querySelectorAll(".tracker input[type=checkbox]");

  function read() {
    try { return JSON.parse(localStorage.getItem(KEY) || "[]"); } catch (e) { return []; }
  }
  function write(list) {
    try { localStorage.setItem(KEY, JSON.stringify(list)); } catch (e) { /* без хранилища работает на странице */ }
  }

  var saved = read();
  boxes.forEach(function (b) {
    b.checked = saved.indexOf(b.getAttribute("data-day")) !== -1;
    b.addEventListener("change", function () {
      var list = [];
      boxes.forEach(function (x) { if (x.checked) list.push(x.getAttribute("data-day")); });
      write(list);
    });
  });

  var reset = document.getElementById("tracker-reset");
  if (reset) {
    reset.addEventListener("click", function () {
      boxes.forEach(function (b) { b.checked = false; });
      write([]);
    });
  }

  /* Метка источника из ссылки ?s=... попадает в заявку */
  var src = document.getElementById("f-source");
  if (src) {
    var m = /[?&]s=([a-z0-9_-]{1,40})/i.exec(location.search);
    var val = m ? m[1] : "";
    try {
      if (val) sessionStorage.setItem("betula-source", val);
      else val = sessionStorage.getItem("betula-source") || "";
    } catch (e) { /* без хранилища метка не сохранится */ }
    src.value = val;
  }

  /* Свой счётчик: какая кнопка нажата и до куда прокрутили. Без cookie, IP и данных о человеке. */
  function source() {
    try { return sessionStorage.getItem("betula-source") || ""; } catch (e) { return ""; }
  }
  var endpoint = (document.querySelector("form[action$='/order']") || {}).action;
  endpoint = endpoint ? endpoint.replace(/\/order$/, "/e") : "";
  function send(ev) {
    if (!endpoint || !navigator.sendBeacon) return;
    var body = new Blob(["ev=" + encodeURIComponent(ev) + "&s=" + encodeURIComponent(source())], { type: "application/x-www-form-urlencoded" });
    try { navigator.sendBeacon(endpoint, body); } catch (e) { /* счётчик не важнее страницы */ }
  }
  document.addEventListener("click", function (e) {
    var el = e.target.closest ? e.target.closest("[data-cta]") : null;
    if (el) send("cta:" + el.getAttribute("data-cta"));
  });
  /* Кнопка «Выбрать» на карточке набора отмечает набор в форме */
  document.querySelectorAll("[data-pack]").forEach(function (a) {
    a.addEventListener("click", function () {
      var r = document.querySelector('input[name="pack"][value="' + a.getAttribute("data-pack") + '"]');
      if (r) r.checked = true;
      var ph = document.getElementById("f-phone");
      if (ph) setTimeout(function () { ph.focus({ preventScroll: true }); }, 400);
    });
  });

  var marks = [25, 50, 75, 100], sent = {};
  function onScroll() {
    var h = document.documentElement.scrollHeight - window.innerHeight;
    if (h <= 0) return;
    var pct = Math.round(window.scrollY / h * 100);
    marks.forEach(function (m) { if (pct >= m && !sent[m]) { sent[m] = 1; send("scroll:" + m); } });
  }
  window.addEventListener("scroll", onScroll, { passive: true });
})();
