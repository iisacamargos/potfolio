/* Rolagem suave com Lenis. Âncoras internas também deslizam até a seção,
   descontando a altura do topo fixo. Desligado para quem pede menos movimento. */
(() => {
  if (!window.Lenis) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const lenis = new Lenis({ lerp: 0.1, wheelMultiplier: 1 });

  const raf = (time) => {
    lenis.raf(time);
    requestAnimationFrame(raf);
  };
  requestAnimationFrame(raf);

  const topbar = document.querySelector(".topbar");

  document.addEventListener("click", (e) => {
    const link = e.target.closest('a[href*="#"]');
    if (!link) return;
    const url = new URL(link.href);
    if (url.pathname !== location.pathname || !url.hash) return;
    const target = document.querySelector(url.hash);
    if (!target) return;
    e.preventDefault();
    lenis.scrollTo(target, { offset: -(topbar ? topbar.offsetHeight : 0) });
    history.pushState(null, "", url.hash);
  });
})();

/* Vídeos dos cases: tocam só quando estão na tela; quem pede menos
   movimento vê apenas o quadro final (poster). */
(() => {
  const videos = document.querySelectorAll("video.autoplay");
  if (!videos.length) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const io = new IntersectionObserver((entries) => {
    entries.forEach(({ target, isIntersecting }) => {
      if (isIntersecting) {
        target.play().catch(() => {});
      } else {
        target.pause();
      }
    });
  }, { threshold: 0.25 });
  videos.forEach((v) => io.observe(v));
})();

/* Home: alterna os projetos entre grade e lista e lembra a escolha. */
(() => {
  const work = document.querySelector(".work[data-view]");
  if (!work) return;
  const buttons = work.querySelectorAll(".view-toggle button");
  const set = (view) => {
    work.dataset.view = view;
    buttons.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.view === view)));
  };
  try {
    const saved = localStorage.getItem("projetos-view");
    if (saved === "list" || saved === "grid") set(saved);
  } catch (e) {}
  buttons.forEach((b) => b.addEventListener("click", () => {
    set(b.dataset.view);
    try { localStorage.setItem("projetos-view", b.dataset.view); } catch (e) {}
  }));
})();

/* Revela blocos com um leve deslize conforme entram na tela.
   Sem JavaScript ou com movimento reduzido, tudo aparece normalmente. */
(() => {
  if (!("IntersectionObserver" in window)) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const els = document.querySelectorAll(
    ".work-tile, .section, .media, .media-grid, .ds, .lv-band, .logo-hero, .case-next"
  );
  const io = new IntersectionObserver((entries) => {
    entries.forEach(({ target, isIntersecting }) => {
      if (!isIntersecting) return;
      target.classList.add("is-in");
      io.unobserve(target);
    });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
  els.forEach((el) => {
    el.classList.add("reveal");
    // cards lado a lado entram em cascata
    if (el.classList.contains("work-tile")) {
      const prev = el.previousElementSibling;
      const sameRow = prev && Math.abs(prev.getBoundingClientRect().top - el.getBoundingClientRect().top) < 4;
      el.style.setProperty("--d", sameRow ? `${(parseFloat(prev.style.getPropertyValue("--d")) || 0) + 0.12}s` : "0s");
    }
    io.observe(el);
  });
})();

/* Seletor de idioma: fecha ao clicar fora ou apertar Esc. */
(() => {
  const lang = document.querySelector("details.lang");
  if (!lang) return;
  document.addEventListener("click", (e) => {
    if (lang.open && !lang.contains(e.target)) lang.open = false;
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && lang.open) {
      lang.open = false;
      lang.querySelector("summary").focus();
    }
  });
})();
