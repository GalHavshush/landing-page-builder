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
  if (calm || !("IntersectionObserver" in window) || document.querySelector("[data-section-id]")) return;
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
