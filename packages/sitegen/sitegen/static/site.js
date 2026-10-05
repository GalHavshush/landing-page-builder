document.documentElement.classList.add("js");
(function () {
  var t = document.querySelector(".nav-toggle"), n = document.querySelector(".nav");
  if (t && n) t.addEventListener("click", function () {
    var open = n.classList.toggle("open");
    t.setAttribute("aria-expanded", open);
  });
})();
