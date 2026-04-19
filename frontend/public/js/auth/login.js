document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#login-form");
  const resultNode = document.querySelector("#login-result");

  if (!form || !resultNode) {
    return;
  }

  const url = new URL(window.location.href);
  if (url.searchParams.get("session_expired") === "1") {
    resultNode.textContent = "La sesion se cerro por inactividad. Ingresa nuevamente.";
    resultNode.dataset.state = "error";
    url.searchParams.delete("session_expired");
    window.history.replaceState({}, document.title, url.pathname || "/login");
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(form);
    const payload = {
      rut: (formData.get("rut") || "").toString(),
    };

    resultNode.textContent = "Validando RUT...";
    resultNode.dataset.state = "pending";

    try {
      const response = await fetch("/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      resultNode.textContent = data.message;
      resultNode.dataset.state = data.success ? "success" : "error";
    } catch (error) {
      resultNode.textContent =
        "No fue posible validar el RUT en este momento.";
      resultNode.dataset.state = "error";
      console.error("Agenda Abril auth error:", error);
    }
  });
});
