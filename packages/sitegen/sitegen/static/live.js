/* Interactive editor preview: the site behaves as published; page links ask the editor to switch
   page. Injected into preview HTML, never into exported sites. */
(function () {
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]");
    if (!a) return;
    var href = a.getAttribute("href") || "";
    var page = /^#pg:([^:]+):(.+)$/.exec(href);
    if (page) {
      e.preventDefault();
      parent.postMessage({ type: "navigate", page: page[1], lang: page[2] }, "*");
    } else if (href === "#") {
      e.preventDefault(); // a link the preview cannot follow
    } else if (/^https?:/i.test(href)) {
      e.preventDefault();
      window.open(href, "_blank", "noopener"); // never navigate the preview frame away
    }
  });
  document.addEventListener("submit", function (e) { e.preventDefault(); }, true); // nothing is sent from a preview
  parent.postMessage({ type: "preview-ready" }, "*");
})();
