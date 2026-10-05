document.documentElement.classList.add("js");
(function () {
  var t = document.querySelector(".nav-toggle"), n = document.querySelector(".nav");
  if (t && n) t.addEventListener("click", function () {
    var open = n.classList.toggle("open");
    t.setAttribute("aria-expanded", open);
  });
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
    onScroll(); window.addEventListener("scroll", onScroll, { passive: true });
  }
})();

// Scroll reveal: a gentle fade-up as things enter the viewport. Skipped for visitors who prefer
// reduced motion, without IntersectionObserver, and in the editor preview.
(function () {
  var calm = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var off = document.body.classList.contains("motion-none"); // the site owner turned animation off
  if (calm || off || !("IntersectionObserver" in window) || document.querySelector("[data-section-id]")) return;
  var SELECTORS = ".s .section-head,.hero-copy>*,.hero-media,.s .item,.post-card,.plan,.quote-item,.gallery figure,.contact-info,.contact-form,.faq details,.video,.map,.prose,.post header,.post-hero";
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
  document.querySelectorAll(".s").forEach(function (section) {
    var seen = 0;
    section.querySelectorAll(SELECTORS).forEach(function (el) {
      if (el.closest(".reveal")) return; // never nest reveals
      el.classList.add("reveal");
      if (el.matches(".hero-media,.post-hero,.gallery figure,.s .item img")) el.classList.add("reveal-image");
      el.style.setProperty("--d", Math.min(seen++, 6) * 70 + "ms"); // light stagger within a section
      io.observe(el);
    });
  });
})();
// YouTube: nothing is requested from YouTube until the visitor clicks play (privacy + speed).
document.querySelectorAll(".yt[data-yt]").forEach(function (box) {
  var link = box.querySelector(".yt-link");
  if (!link) return;
  link.addEventListener("click", function (e) {
    e.preventDefault();
    var f = document.createElement("iframe");
    f.src = "https://www.youtube-nocookie.com/embed/" + box.getAttribute("data-yt") + "?autoplay=1&rel=0";
    f.allow = "autoplay; encrypted-media; picture-in-picture";
    f.allowFullscreen = true;
    f.title = link.textContent.trim();
    box.innerHTML = "";
    box.appendChild(f);
  });
});

// Hero cover video: a muted, looping YouTube player behind the text. It starts after the page has
// loaded, never for visitors who prefer reduced motion or have data saver on, and never in the editor
// preview. The picture stays visible as the poster until the video is ready.
(function () {
  var holders = document.querySelectorAll(".cover-video[data-yt-bg]");
  if (!holders.length || document.querySelector("[data-section-id]")) return;
  var calm = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var saver = navigator.connection && navigator.connection.saveData;
  if (calm || saver) return;
  function start() {
    holders.forEach(function (holder) {
      var id = holder.getAttribute("data-yt-bg");
      var f = document.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&mute=1&loop=1&playlist=" + id +
        "&controls=0&playsinline=1&modestbranding=1&rel=0&disablekb=1&iv_load_policy=3&enablejsapi=1";
      f.allow = "autoplay; encrypted-media";
      f.tabIndex = -1;
      f.setAttribute("aria-hidden", "true");
      f.title = "";
      f.addEventListener("load", function () { setTimeout(function () { holder.classList.add("on"); }, 600); });
      holder.appendChild(f);
      var toggle = holder.closest(".hero-cover").querySelector(".cover-toggle");
      if (!toggle) return;
      var paused = false;
      toggle.hidden = false;
      toggle.addEventListener("click", function () {
        paused = !paused;
        f.contentWindow.postMessage(JSON.stringify({ event: "command", func: paused ? "pauseVideo" : "playVideo", args: "" }), "*");
        toggle.classList.toggle("paused", paused);
        var label = toggle.getAttribute(paused ? "data-play" : "data-pause");
        toggle.setAttribute("aria-label", label);
      });
    });
  }
  if (document.readyState === "complete") start(); else window.addEventListener("load", start);
})();

// Before/after slider: the range input drives the --pos custom property.
document.querySelectorAll("[data-compare]").forEach(function (box) {
  var r = box.querySelector(".cmp-range");
  if (!r) return;
  var set = function () { box.style.setProperty("--pos", r.value + "%"); };
  r.addEventListener("input", set); set();
});

// Stats count-up: "1,200+" -> animate the number part when scrolled into view. Skipped for reduced
// motion, without IntersectionObserver, and in the editor preview (the final value is always in the HTML).
(function () {
  var els = document.querySelectorAll(".stat-value[data-count]");
  var calm = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!els.length || calm || document.body.classList.contains("motion-none") || !("IntersectionObserver" in window) || document.querySelector("[data-section-id]")) return;
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      run(e.target);
    });
  }, { threshold: 0.4 });
  function run(el) {
    var text = el.textContent, m = text.match(/^(\D*?)([\d][\d,.\s]*)(.*)$/);
    if (!m) return;
    var digits = m[2].replace(/[^\d]/g, ""), target = parseInt(digits, 10);
    if (!target || m[2].indexOf(".") > -1) return; // decimals: leave as written
    var sep = /,/.test(m[2]) ? "," : "", t0 = null, dur = 1100;
    function fmt(n) { var s = String(n); return sep ? s.replace(/\B(?=(\d{3})+(?!\d))/g, sep) : s; }
    function tick(t) {
      if (t0 === null) t0 = t;
      var p = Math.min((t - t0) / dur, 1), eased = 1 - Math.pow(1 - p, 3);
      el.textContent = m[1] + fmt(Math.round(target * eased)) + m[3];
      if (p < 1) requestAnimationFrame(tick); else el.textContent = text;
    }
    requestAnimationFrame(tick);
  }
  els.forEach(function (el) { io.observe(el); });
})();

// Gallery lightbox: click a picture to see it large; arrows/Esc work, focus is trapped by <dialog>.
// Without JS the picture is a plain link to the full image.
(function () {
  var galleries = document.querySelectorAll(".gallery[data-lb-close]");
  if (!galleries.length || typeof HTMLDialogElement === "undefined") return;
  var dlg = document.createElement("dialog");
  dlg.className = "lightbox";
  dlg.innerHTML = '<button type="button" class="lb-x"></button><button type="button" class="lb-prev"></button>' +
    '<figure><img alt=""><figcaption></figcaption></figure><button type="button" class="lb-next"></button>';
  document.body.appendChild(dlg);
  var img = dlg.querySelector("img"), cap = dlg.querySelector("figcaption");
  var items = [], at = 0;
  function show(i) {
    at = (i + items.length) % items.length;
    var a = items[at], pic = a.querySelector("img"), fig = a.closest("figure").querySelector("figcaption");
    img.src = a.getAttribute("href"); img.alt = pic ? pic.alt : "";
    cap.textContent = fig ? fig.textContent : "";
    dlg.classList.toggle("single", items.length < 2);
  }
  galleries.forEach(function (g) {
    var links = Array.prototype.slice.call(g.querySelectorAll("a[data-lb]"));
    dlg.querySelector(".lb-x").setAttribute("aria-label", g.getAttribute("data-lb-close"));
    dlg.querySelector(".lb-prev").setAttribute("aria-label", g.getAttribute("data-lb-prev"));
    dlg.querySelector(".lb-next").setAttribute("aria-label", g.getAttribute("data-lb-next"));
    links.forEach(function (a, i) {
      a.addEventListener("click", function (e) {
        e.preventDefault(); items = links; show(i); dlg.showModal();
      });
    });
  });
  dlg.querySelector(".lb-x").addEventListener("click", function () { dlg.close(); });
  dlg.querySelector(".lb-prev").addEventListener("click", function () { show(at - 1); });
  dlg.querySelector(".lb-next").addEventListener("click", function () { show(at + 1); });
  dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });
  dlg.addEventListener("keydown", function (e) {
    var rtl = document.documentElement.dir === "rtl";
    if (e.key === "ArrowRight") show(at + (rtl ? -1 : 1));
    if (e.key === "ArrowLeft") show(at + (rtl ? 1 : -1));
  });
})();
