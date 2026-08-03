(function () {
  const thumbs = Array.from(document.querySelectorAll("img[data-large]"));
  if (thumbs.length === 0) return;

  const overlay = document.createElement("div");
  overlay.className = "lightbox";
  overlay.hidden = true;
  overlay.innerHTML =
    '<button class="lightbox-close" aria-label="Close">&times;</button>' +
    '<button class="lightbox-prev" aria-label="Previous photo">&#10094;</button>' +
    '<div class="lightbox-stage"><img class="lightbox-img" src="" alt=""></div>' +
    '<button class="lightbox-next" aria-label="Next photo">&#10095;</button>';
  document.body.appendChild(overlay);

  const stage = overlay.querySelector(".lightbox-stage");
  const img = overlay.querySelector(".lightbox-img");
  const btnClose = overlay.querySelector(".lightbox-close");
  const btnPrev = overlay.querySelector(".lightbox-prev");
  const btnNext = overlay.querySelector(".lightbox-next");

  const ZOOM_FACTOR = 3.5;
  let currentIndex = 0;

  function resetZoom() {
    img.classList.remove("zoomed");
    img.style.width = "";
    img.style.height = "";
    stage.scrollLeft = 0;
    stage.scrollTop = 0;
  }

  function show(index) {
    currentIndex = (index + thumbs.length) % thumbs.length;
    const thumb = thumbs[currentIndex];
    resetZoom();
    img.src = thumb.getAttribute("data-large");
    img.alt = thumb.alt || "";
    overlay.hidden = false;
    document.body.style.overflow = "hidden";
  }

  function close() {
    overlay.hidden = true;
    img.src = "";
    resetZoom();
    document.body.style.overflow = "";
  }

  function toggleZoom(e) {
    if (!img.classList.contains("zoomed")) {
      const rect = img.getBoundingClientRect();
      const xRatio = (e.clientX - rect.left) / rect.width;
      const yRatio = (e.clientY - rect.top) / rect.height;
      const fittedWidth = rect.width;
      const fittedHeight = rect.height;

      img.classList.add("zoomed");
      img.style.width = fittedWidth * ZOOM_FACTOR + "px";
      img.style.height = fittedHeight * ZOOM_FACTOR + "px";

      requestAnimationFrame(() => {
        const stageRect = stage.getBoundingClientRect();
        stage.scrollLeft = fittedWidth * ZOOM_FACTOR * xRatio - stageRect.width / 2;
        stage.scrollTop = fittedHeight * ZOOM_FACTOR * yRatio - stageRect.height / 2;
      });
    } else {
      resetZoom();
    }
  }

  thumbs.forEach((thumb, index) => {
    thumb.style.cursor = "zoom-in";
    thumb.addEventListener("click", () => show(index));
  });

  img.addEventListener("click", (e) => {
    e.stopPropagation();
    toggleZoom(e);
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
