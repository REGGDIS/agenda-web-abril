document.addEventListener("DOMContentLoaded", () => {
  const storedTheme = window.localStorage.getItem("agenda-abril-theme");

  if (storedTheme) {
    document.documentElement.setAttribute("data-theme", storedTheme);
  }
});

