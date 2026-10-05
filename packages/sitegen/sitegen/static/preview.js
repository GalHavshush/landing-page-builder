/* Editor-only script. Injected into preview HTML, never into exported sites.
   Talks to the editor (parent window) via postMessage. */
(function () {
  var style = document.createElement("style");
  style.textContent =
    "[data-section-id]{position:relative}" +
    "[data-section-id].pv-hover{outline:2px dashed #6366f1;outline-offset:-2px;cursor:pointer}" +
    "[data-section-id].pv-selected{outline:3px solid #6366f1;outline-offset:-3px}";
  document.head.appendChild(style);

  function sectionOf(el) { return el.closest && el.closest("[data-section-id]"); }
  function select(id) {
    document.querySelectorAll(".pv-selected").forEach(function (n) { n.classList.remove("pv-selected"); });
    var el = id && document.querySelector('[data-section-id="' + id + '"]');
    if (el) el.classList.add("pv-selected");
    return el;
  }

  document.addEventListener("mouseover", function (e) {
    document.querySelectorAll(".pv-hover").forEach(function (n) { n.classList.remove("pv-hover"); });
    var s = sectionOf(e.target); if (s) s.classList.add("pv-hover");
  });
  document.addEventListener("click", function (e) {
    e.preventDefault(); // links and forms must not navigate inside the preview
    var s = sectionOf(e.target);
    parent.postMessage({ type: "section-click", id: s ? s.getAttribute("data-section-id") : null }, "*");
  }, true);
  document.addEventListener("submit", function (e) { e.preventDefault(); }, true);

  window.addEventListener("message", function (e) {
    var m = e.data || {};
    if (m.type === "select") { var el = select(m.id); if (el && m.scroll) el.scrollIntoView({ behavior: "smooth", block: "center" }); }
  });
  parent.postMessage({ type: "preview-ready" }, "*");
})();
