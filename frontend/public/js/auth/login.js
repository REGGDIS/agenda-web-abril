document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#login-form");
  const rutInput = document.querySelector("#rut");
  const rutLimitHelp = document.querySelector("#rut-limit-help");
  const resultNode = document.querySelector("#login-result");
  const submitButton = document.querySelector("#login-submit-button");
  const successActions = document.querySelector("#login-success-actions");

  if (!form || !resultNode) {
    return;
  }

  const hideSuccessActions = () => {
    if (!(successActions instanceof HTMLElement)) {
      return;
    }

    successActions.hidden = true;
  };

  const showSuccessActions = () => {
    if (!(successActions instanceof HTMLElement)) {
      return;
    }

    successActions.hidden = false;
  };

  const hideRutLimitHelp = () => {
    if (
      !(rutInput instanceof HTMLInputElement) ||
      !(rutLimitHelp instanceof HTMLElement)
    ) {
      return;
    }

    rutLimitHelp.hidden = true;
  };

  const showRutLimitHelp = () => {
    if (!(rutLimitHelp instanceof HTMLElement)) {
      return;
    }

    rutLimitHelp.hidden = false;
  };

  const getRutValueAfterInsert = (insertedText) => {
    if (!(rutInput instanceof HTMLInputElement)) {
      return "";
    }

    const selectionStart = rutInput.selectionStart ?? rutInput.value.length;
    const selectionEnd = rutInput.selectionEnd ?? rutInput.value.length;
    return (
      rutInput.value.slice(0, selectionStart) +
      insertedText +
      rutInput.value.slice(selectionEnd)
    );
  };

  const showRutLimitHelpIfExceeded = (nextValue) => {
    if (!(rutInput instanceof HTMLInputElement)) {
      return;
    }

    if (nextValue.length > rutInput.maxLength) {
      showRutLimitHelp();
    } else {
      hideRutLimitHelp();
    }
  };

  if (rutInput instanceof HTMLInputElement) {
    rutInput.addEventListener("beforeinput", (event) => {
      if (!event.data) {
        return;
      }

      showRutLimitHelpIfExceeded(getRutValueAfterInsert(event.data));
    });

    rutInput.addEventListener("paste", (event) => {
      const pastedText = event.clipboardData?.getData("text") || "";
      showRutLimitHelpIfExceeded(getRutValueAfterInsert(pastedText));
    });

    rutInput.addEventListener("input", () => {
      if (rutInput.value.length < rutInput.maxLength) {
        hideRutLimitHelp();
      }
    });
    hideRutLimitHelp();
  }

  const url = new URL(window.location.href);
  const consumeLoginMessage = (paramName, message, state) => {
    if (url.searchParams.get(paramName) !== "1") {
      return false;
    }

    resultNode.textContent = message;
    resultNode.dataset.state = state;
    url.searchParams.delete(paramName);
    window.history.replaceState({}, document.title, url.pathname || "/login");
    return true;
  };

  if (
    !consumeLoginMessage(
      "logout",
      "La sesion fue cerrada correctamente.",
      "success",
    ) &&
    url.searchParams.get("session_expired") === "1"
  ) {
    resultNode.textContent = "La sesion se cerro por inactividad. Ingresa nuevamente.";
    resultNode.dataset.state = "error";
    url.searchParams.delete("session_expired");
    window.history.replaceState({}, document.title, url.pathname || "/login");
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    hideSuccessActions();

    const formData = new FormData(form);
    const payload = {
      rut: (formData.get("rut") || "").toString(),
    };

    resultNode.textContent = "Validando RUT...";
    resultNode.dataset.state = "pending";
    if (submitButton instanceof HTMLButtonElement) {
      submitButton.disabled = true;
      submitButton.textContent = "Validando...";
    }

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
      if (data.success && data.status === "session_created") {
        showSuccessActions();
      }
    } catch (error) {
      resultNode.textContent =
        "No fue posible validar el RUT en este momento.";
      resultNode.dataset.state = "error";
      console.error("Agenda Abril auth error:", error);
    } finally {
      if (submitButton instanceof HTMLButtonElement) {
        submitButton.disabled = false;
        submitButton.textContent = "Validar ingreso";
      }
    }
  });
});
