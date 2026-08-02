(function () {
  const thumbs = Array.from(document.querySelectorAll(".gallery img[data-large]"));
  if (thumbs.length === 0) return;

  const overlay = document.createElement("div");
  overlay.className = "lightbox";
  overlay.hidden = true;
  overlay.innerHTML =
    '<button class="lightbox-close" aria-label="Close">&times;</button>' +
    '<button class="lightbox-prev" aria-label="Previous photo">&#10094;</button>' +
    '<img class="lightbox-img" src="" alt="">' +
    '<button class="lightbox-next" aria-label="Next photo">&#10095;</button>';
  document.body.appendChild(overlay);

  const img = overlay.querySelector(".lightbox-img");
  const btnClose = overlay.querySelector(".lightbox-close");
  const btnPrev = overlay.querySelector(".lightbox-prev");
  const btnNext = overlay.querySelector(".lightbox-next");

  let currentIndex = 0;

  function show(index) {
    currentIndex = (index + thumbs.length) % thumbs.length;
    const thumb = thumbs[currentIndex];
    img.src = thumb.getAttribute("data-large");
    img.alt = thumb.alt || "";
    overlay.hidden = false;
    document.body.style.overflow = "hidden";
  }

  function close() {
    overlay.hidden = true;
    img.src = "";
    document.body.style.overflow = "";
  }

  thumbs.forEach((thumb, index) => {
    thumb.style.cursor = "zoom-in";
    thumb.addEventListener("click", () => show(index));
  });

  btnClose.addEventListener("click", close);
  btnPrev.addEventListener("click", () => show(currentIndex - 1));
  btnNext.addEventListener("click", () => show(currentIndex + 1));

  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) close();
  });

  document.addEventListener("keydown", (e) => {
    if (overlay.hidden) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowLeft") show(currentIndex - 1);
    if (e.key === "ArrowRight") show(currentIndex + 1);
  });
})();
