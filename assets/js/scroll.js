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

/* Home: alterna os projetos entre grade e lista. A grade é sempre o padrão:
   ao abrir a home ou clicar no nome no topo, ela volta para a grade. */
(() => {
  const work = document.querySelector(".work[data-view]");
  if (!work) return;
  const buttons = work.querySelectorAll(".view-toggle button");
  const set = (view) => {
    work.dataset.view = view;
    buttons.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.view === view)));
  };
  try { localStorage.removeItem("projetos-view"); } catch (e) {}
  // ao trocar de visualização, os itens da vista nova entram de novo em cascata
  const replay = () => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const items = work.querySelectorAll(
      work.dataset.view === "list" ? ".projects .project" : ".works .work-tile"
    );
    items.forEach((el, i) => {
      el.classList.add(el.classList.contains("work-tile") ? "rv-tile" : "rv-item");
      el.classList.remove("is-in");
      el.style.transitionDelay = `${Math.min(i, 8) * 0.06}s`;
    });
    void work.offsetHeight; // força o navegador a registrar o estado inicial
    requestAnimationFrame(() => items.forEach((el) => el.classList.add("is-in")));
  };
  buttons.forEach((b) => b.addEventListener("click", () => {
    if (work.dataset.view === b.dataset.view) return;
    set(b.dataset.view);
    replay();
  }));
  // voltando pelo botão "voltar" do navegador (página restaurada da memória)
  window.addEventListener("pageshow", (e) => {
    if (e.persisted && work.dataset.view !== "grid") set("grid");
  });
})();

/* Scroll reveal
   - imagens e vídeos abrem como cortina, com um leve zoom saindo
   - textos sobem com fade
   - itens de listas (cores, tipografia, símbolos, carreira) entram em cascata
   Sem JavaScript ou com movimento reduzido, tudo aparece normalmente. */
(() => {
  if (!("IntersectionObserver" in window)) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const MEDIA = "main .media, .media-grid > .media, .logo-hero";
  const TILES = ".work-tile";
  const TEXT = ".section, .ds-head, .case-next, .work-head, .lv-band";
  const STAGGER = ".cs-item, .ts-row, .sym-item, .timeline-item, .project, .pillars > div";

  const io = new IntersectionObserver((entries) => {
    entries.forEach(({ target, isIntersecting }) => {
      if (!isIntersecting) return;
      target.classList.add("is-in");
      io.unobserve(target);
    });
  }, { rootMargin: "0px 0px -10% 0px", threshold: 0.12 });

  // atraso em cascata para elementos lado a lado (mesma linha visual)
  const cascade = (el, step) => {
    const prev = el.previousElementSibling;
    if (!prev || !prev.style.getPropertyValue("--d")) return 0;
    const same = Math.abs(prev.getBoundingClientRect().top - el.getBoundingClientRect().top) < 8;
    return same ? parseFloat(prev.style.getPropertyValue("--d")) + step : 0;
  };

  document.querySelectorAll(MEDIA).forEach((el) => {
    if (el.closest(".media-grid") && el.parentElement.matches(".media-grid") === false) return;
    el.classList.add("rv-media");
    el.style.setProperty("--d", `${cascade(el, 0.12)}s`);
    io.observe(el);
  });
  // cards da home: fade simples e rápido, em cascata na mesma linha
  document.querySelectorAll(TILES).forEach((el) => {
    el.classList.add("rv-tile");
    el.style.setProperty("--d", `${cascade(el, 0.08)}s`);
    io.observe(el);
  });
  document.querySelectorAll(TEXT).forEach((el) => {
    if (el.classList.contains("rv-media")) return;
    el.classList.add("rv-text");
    io.observe(el);
  });
  document.querySelectorAll(STAGGER).forEach((el) => {
    el.classList.add("rv-item");
    // cascata pela ordem dentro do grupo; quebra a cada linha nova
    const i = Array.prototype.indexOf.call(el.parentElement.children, el);
    el.style.setProperty("--d", `${Math.min(i, 8) * 0.07}s`);
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
