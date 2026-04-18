document.addEventListener("DOMContentLoaded", () => {
  const themeStorageKey = "agenda-abril-theme";
  const root = document.documentElement;
  const themeToggleButton = document.querySelector("[data-theme-toggle]");
  const themeToggleState = document.querySelector("[data-theme-toggle-state]");
  const themeToggleIcon = document.querySelector("[data-theme-toggle-icon]");

  const fallbackTheme = root.dataset.themePreference === "dark" ? "dark" : "light";

  const readStoredTheme = () => {
    try {
      const storedTheme = window.localStorage.getItem(themeStorageKey);
      return storedTheme === "dark" || storedTheme === "light" ? storedTheme : null;
    } catch {
      return null;
    }
  };

  const persistTheme = (theme) => {
    try {
      window.localStorage.setItem(themeStorageKey, theme);
    } catch {
      console.warn("Agenda Abril: no se pudo persistir el tema en localStorage.");
    }
  };

  const resolveTheme = () => {
    const currentTheme = root.getAttribute("data-theme");
    if (currentTheme === "dark" || currentTheme === "light") {
      return currentTheme;
    }

    return readStoredTheme() ?? fallbackTheme;
  };

  const applyTheme = (theme) => {
    root.setAttribute("data-theme", theme);

    if (themeToggleButton instanceof HTMLButtonElement) {
      themeToggleButton.setAttribute("aria-pressed", String(theme === "dark"));
      themeToggleButton.setAttribute(
        "title",
        theme === "dark"
          ? "Cambiar a modo claro"
          : "Cambiar a modo oscuro",
      );
    }

    if (themeToggleState instanceof HTMLElement) {
      themeToggleState.textContent = theme === "dark" ? "Oscuro" : "Claro";
    }

    if (themeToggleIcon instanceof HTMLElement) {
      themeToggleIcon.textContent = theme === "dark" ? "O" : "C";
    }
  };

  applyTheme(resolveTheme());

  if (themeToggleButton instanceof HTMLButtonElement) {
    themeToggleButton.addEventListener("click", () => {
      const nextTheme = resolveTheme() === "dark" ? "light" : "dark";
      applyTheme(nextTheme);
      persistTheme(nextTheme);
    });
  }
});
