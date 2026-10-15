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
