/* Editor-only script. Injected into preview HTML, never into exported sites.
   Talks to the editor (parent window) via postMessage. */
(function () {
  var style = document.createElement("style");
  style.textContent =
    "[data-section-id]{position:relative}" +
    "[data-section-id].pv-hover{outline:2px dashed #f2600f;outline-offset:-2px;cursor:pointer}" +
    "[data-section-id].pv-selected{outline:3px solid #f2600f;outline-offset:-3px}" +
    ".pv-empty{margin-block:1rem;padding:1.5rem;border:2px dashed #b9b4a8;border-radius:10px;text-align:center;font:14px/1.4 system-ui,sans-serif;color:#5d5951;background:rgb(255 255 255 / .6)}";
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
    var nav = e.target.closest && e.target.closest("[data-page-id]");
    if (nav) { parent.postMessage({ type: "page-click", id: nav.getAttribute("data-page-id") }, "*"); return; }
    var s = sectionOf(e.target);
    parent.postMessage({ type: "section-click", id: s ? s.getAttribute("data-section-id") : null }, "*");
  }, true);
  document.addEventListener("submit", function (e) { e.preventDefault(); }, true);

  var ticking = false;
  window.addEventListener("scroll", function () {
    if (ticking) return; ticking = true;
    requestAnimationFrame(function () { ticking = false; parent.postMessage({ type: "scroll", y: window.scrollY }, "*"); });
  });

  window.addEventListener("message", function (e) {
    var m = e.data || {};
    if (m.type === "restore-scroll") {
      document.documentElement.style.scrollBehavior = "auto";
      window.scrollTo(0, m.y || 0);
      document.documentElement.style.scrollBehavior = "";
    }
    if (m.type === "select") { var el = select(m.id); if (el && m.scroll) el.scrollIntoView({ behavior: "smooth", block: "center" }); }
  });
  parent.postMessage({ type: "preview-ready" }, "*");
})();
