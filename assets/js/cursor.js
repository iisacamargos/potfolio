/* Cursor personalizado: um ponto que segue o mouse, vira anel sobre links
   e mostra um rótulo (data-cursor) sobre os projetos. Só em mouse/trackpad. */
(() => {
  if (!window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const cursor = document.createElement("div");
  cursor.className = "cursor";
  cursor.setAttribute("aria-hidden", "true");
  cursor.innerHTML = '<div class="cursor-dot"><span class="cursor-label"></span></div>';
  document.body.appendChild(cursor);
  document.documentElement.classList.add("has-cursor");

  const label = cursor.querySelector(".cursor-label");
  let x = 0;
  let y = 0;
  let cx = 0;
  let cy = 0;
  let visible = false;

  window.addEventListener("mousemove", (e) => {
    x = e.clientX;
    y = e.clientY;
    if (!visible) {
      cx = x;
      cy = y;
      visible = true;
      cursor.classList.add("is-visible");
    }
  }, { passive: true });

  document.addEventListener("mouseleave", () => {
    visible = false;
    cursor.classList.remove("is-visible");
  });

  window.addEventListener("mousedown", () => cursor.classList.add("is-down"));
  window.addEventListener("mouseup", () => cursor.classList.remove("is-down"));

  document.addEventListener("mouseover", (e) => {
    const target = e.target.closest("[data-cursor], a, button");
    const text = target ? target.dataset.cursor || "" : "";
    label.textContent = text;
    cursor.classList.toggle("is-label", Boolean(text));
    cursor.classList.toggle("is-link", Boolean(target) && !text);
  });

  const ease = reduceMotion ? 1 : 0.22;
  const tick = () => {
    cx += (x - cx) * ease;
    cy += (y - cy) * ease;
    cursor.style.transform = `translate3d(${cx}px, ${cy}px, 0)`;
    requestAnimationFrame(tick);
  };
  tick();
})();
