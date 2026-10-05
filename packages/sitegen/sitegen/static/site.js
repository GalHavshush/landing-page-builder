document.documentElement.classList.add("js");
(function () {
  var t = document.querySelector(".nav-toggle"), n = document.querySelector(".nav");
  if (t && n) t.addEventListener("click", function () {
    var open = n.classList.toggle("open");
    t.setAttribute("aria-expanded", open);
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
