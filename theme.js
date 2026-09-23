(() => {
  const root = document.documentElement;
  const button = document.querySelector("[data-theme-toggle]");
  const navButton = document.querySelector("[data-nav-toggle]");
  const header = document.querySelector(".site-header");

  if (navButton && header) {
    navButton.addEventListener("click", () => {
      const open = header.classList.toggle("nav-open");
      navButton.setAttribute("aria-expanded", String(open));
    });
  }

  if (!button) return;

  const key = "axiom-theme";
  const modes = ["system", "light", "dark"];
  const media = window.matchMedia("(prefers-color-scheme: dark)");
  const themeMeta = document.querySelector('meta[name="theme-color"]');
  let mode = localStorage.getItem(key);
  if (!modes.includes(mode)) mode = "system";

  const resolved = () => mode === "system" ? (media.matches ? "dark" : "light") : mode;

  const apply = () => {
    if (mode === "system") root.removeAttribute("data-theme");
    else root.dataset.theme = mode;
    if (themeMeta) themeMeta.content = resolved() === "dark" ? "#06111f" : "#edf7ff";
    const next = modes[(modes.indexOf(mode) + 1) % modes.length];
    button.dataset.mode = mode;
    button.setAttribute("aria-label", `Theme: ${mode}. Activate for ${next}.`);
    button.setAttribute("title", `Theme: ${mode}`);
    button.querySelector("[data-theme-label]").textContent =
      mode === "light" ? "☀" : mode === "dark" ? "☾" : "◐";
  };

  button.addEventListener("click", () => {
    mode = modes[(modes.indexOf(mode) + 1) % modes.length];
    localStorage.setItem(key, mode);
    apply();
  });

  media.addEventListener?.("change", () => { if (mode === "system") apply(); });
  apply();
})();