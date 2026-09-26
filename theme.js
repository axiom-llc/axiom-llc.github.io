(() => {
  const root = document.documentElement;
  const button = document.querySelector("[data-theme-toggle]");
  const navButton = document.querySelector("[data-nav-toggle]");
  const header = document.querySelector(".site-header");
  const key = "axiom-theme";
  const modes = ["system", "light", "dark"];
  const media = window.matchMedia("(prefers-color-scheme: dark)");
  const themeMeta = document.querySelector('meta[name="theme-color"]');

  if (navButton && header) {
    navButton.addEventListener("click", () => {
      const open = header.classList.toggle("nav-open");
      navButton.setAttribute("aria-expanded", String(open));
    });
    header.querySelectorAll("nav a").forEach((link) => link.addEventListener("click", () => {
      header.classList.remove("nav-open");
      navButton.setAttribute("aria-expanded", "false");
    }));
  }

  if (!button) return;

  let mode;
  try { mode = localStorage.getItem(key); } catch (_) { mode = null; }
  if (!modes.includes(mode)) mode = "system";

  const resolved = () => mode === "system" ? (media.matches ? "dark" : "light") : mode;
  const apply = () => {
    if (mode === "system") root.removeAttribute("data-theme");
    else root.dataset.theme = mode;
    if (themeMeta) themeMeta.content = resolved() === "dark" ? "#03090e" : "#edf7ff";
    const next = modes[(modes.indexOf(mode) + 1) % modes.length];
    button.dataset.mode = mode;
    button.setAttribute("aria-label", "Theme: " + mode + ". Activate for " + next + ".");
    button.setAttribute("title", "Theme: " + mode);
    const label = button.querySelector("[data-theme-label]");
    if (label) label.textContent = mode === "light" ? "☀" : mode === "dark" ? "☾" : "◐";
  };

  button.addEventListener("click", () => {
    mode = modes[(modes.indexOf(mode) + 1) % modes.length];
    try { localStorage.setItem(key, mode); } catch (_) {}
    apply();
  });

  media.addEventListener?.("change", () => { if (mode === "system") apply(); });
  apply();
})();
