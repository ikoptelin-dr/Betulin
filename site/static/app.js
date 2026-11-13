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
})();
