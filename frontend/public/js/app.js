document.addEventListener("DOMContentLoaded", () => {
  console.info("Agenda Abril: frontend base cargado.");
  const alertWindowInMilliseconds = 60 * 60 * 1000;

  const parseLocalDateTime = (value) => {
    if (typeof value !== "string" || value.length < 16) {
      return null;
    }

    const [datePart, timePart] = value.split("T");
    if (!datePart || !timePart) {
      return null;
    }

    const [year, month, day] = datePart.split("-").map(Number);
    const [hour, minute, second = 0] = timePart.split(":").map(Number);
    if ([year, month, day, hour, minute, second].some(Number.isNaN)) {
      return null;
    }

    return new Date(year, month - 1, day, hour, minute, second);
  };

  const formatRemainingTime = (targetDate) => {
    const differenceInMilliseconds = targetDate.getTime() - Date.now();
    if (differenceInMilliseconds <= 0) {
      return "La actividad ya puede comenzar.";
    }

    const totalMinutes = Math.floor(differenceInMilliseconds / 60000);
    if (totalMinutes < 1) {
      return "Comienza en menos de un minuto.";
    }

    const days = Math.floor(totalMinutes / 1440);
    const hours = Math.floor((totalMinutes % 1440) / 60);
    const minutes = totalMinutes % 60;
    const parts = [];

    if (days > 0) {
      parts.push(days === 1 ? "1 dia" : `${days} dias`);
    }
    if (hours > 0) {
      parts.push(hours === 1 ? "1 hora" : `${hours} horas`);
    }
    if (minutes > 0) {
      parts.push(minutes === 1 ? "1 minuto" : `${minutes} minutos`);
    }

    if (parts.length === 1) {
      const prefix = parts[0].startsWith("1 ") ? "Falta" : "Faltan";
      return `${prefix} ${parts[0]}.`;
    }
    if (parts.length === 2) {
      return `Faltan ${parts[0]} y ${parts[1]}.`;
    }

    return `Faltan ${parts[0]}, ${parts[1]} y ${parts[2]}.`;
  };

  const isAlertWindowActive = (targetDate) => {
    const differenceInMilliseconds = targetDate.getTime() - Date.now();
    return differenceInMilliseconds > 0 && differenceInMilliseconds <= alertWindowInMilliseconds;
  };

  const featuredActivityModal = document.querySelector("#featured-activity-modal");
  if (featuredActivityModal instanceof HTMLElement) {
    const closeFeaturedActivityModal = () => {
      featuredActivityModal.hidden = true;
      featuredActivityModal.setAttribute("aria-hidden", "true");
      featuredActivityModal.classList.add("is-hidden");
    };

    document.querySelectorAll("[data-calendar-popup-close]").forEach((button) => {
      button.addEventListener("click", () => {
        closeFeaturedActivityModal();
      });
    });
  }

  const nextActivityCountdown = document.querySelector("[data-next-activity-countdown]");
  if (nextActivityCountdown instanceof HTMLElement) {
    const startsAt = parseLocalDateTime(
      nextActivityCountdown.dataset.startsAt ?? "",
    );
    const nextActivityCard = document.querySelector(".next-activity-card");
    const nextActivityAlertBanner = document.querySelector("[data-next-activity-alert-visual]");
    const nextActivityAlertMessage = nextActivityAlertBanner?.querySelector("span");
    const nextActivityAlertAudio = document.querySelector("[data-next-activity-alert-audio]");
    const initialAlertMessage = nextActivityAlertMessage?.textContent ?? "";
    let alertAlreadyPlayed = false;
    let alertRetryRegistered = false;

    const syncAlertVisualState = (alertIsActive) => {
      if (nextActivityCard instanceof HTMLElement) {
        nextActivityCard.classList.toggle("alert-active", alertIsActive);
      }

      if (nextActivityAlertBanner instanceof HTMLElement) {
        nextActivityAlertBanner.hidden = !alertIsActive;
        nextActivityAlertBanner.setAttribute("aria-hidden", String(!alertIsActive));
        nextActivityAlertBanner.classList.toggle("is-hidden", !alertIsActive);
      }

      if (nextActivityAlertMessage instanceof HTMLElement && alertIsActive) {
        nextActivityAlertMessage.textContent = initialAlertMessage;
      }
    };

    const registerAlertRetryOnInteraction = () => {
      if (alertRetryRegistered || alertAlreadyPlayed) {
        return;
      }

      alertRetryRegistered = true;
      const retryEvents = ["click", "keydown", "touchstart"];
      const retryPlayback = () => {
        alertRetryRegistered = false;
        retryEvents.forEach((eventName) => {
          document.removeEventListener(eventName, retryPlayback);
        });
        attemptAlertPlayback();
      };

      retryEvents.forEach((eventName) => {
        document.addEventListener(eventName, retryPlayback, { once: true });
      });
    };

    const attemptAlertPlayback = async () => {
      if (
        !(startsAt instanceof Date) ||
        Number.isNaN(startsAt.getTime()) ||
        alertAlreadyPlayed ||
        !isAlertWindowActive(startsAt) ||
        !(nextActivityAlertAudio instanceof HTMLAudioElement)
      ) {
        return;
      }

      try {
        nextActivityAlertAudio.currentTime = 0;
        await nextActivityAlertAudio.play();
        alertAlreadyPlayed = true;
        if (nextActivityAlertMessage instanceof HTMLElement) {
          nextActivityAlertMessage.textContent = initialAlertMessage;
        }
      } catch {
        if (nextActivityAlertMessage instanceof HTMLElement) {
          nextActivityAlertMessage.textContent = "El navegador puede requerir una interaccion para reproducir el sonido.";
        }
        registerAlertRetryOnInteraction();
      }
    };

    if (startsAt instanceof Date && !Number.isNaN(startsAt.getTime())) {
      const refreshCountdown = () => {
        nextActivityCountdown.textContent = formatRemainingTime(startsAt);
        const alertIsActive = isAlertWindowActive(startsAt);
        syncAlertVisualState(alertIsActive);
        if (alertIsActive) {
          void attemptAlertPlayback();
        }
      };

      refreshCountdown();
      window.setInterval(refreshCountdown, 30000);
    }
  }

  const body = document.body;
  const sessionMonitorEnabled = body?.dataset.sessionMonitorEnabled === "true";

  if (!sessionMonitorEnabled || !(body instanceof HTMLBodyElement)) {
    return;
  }

  const sessionActivityUrl = body.dataset.sessionActivityUrl ?? "";
  const sessionExpireUrl = body.dataset.sessionExpireUrl ?? "";
  const sessionExpiredLoginUrl = body.dataset.sessionExpiredLoginUrl ?? "/login?session_expired=1";
  const inactivityTimeoutMs = Number.parseInt(
    body.dataset.sessionInactivityTimeoutMs ?? "",
    10,
  );
  const activityThrottleMs = Number.parseInt(
    body.dataset.sessionActivityThrottleMs ?? "",
    10,
  );

  if (
    !sessionActivityUrl ||
    !sessionExpireUrl ||
    Number.isNaN(inactivityTimeoutMs) ||
    Number.isNaN(activityThrottleMs)
  ) {
    console.warn("Agenda Abril: configuracion incompleta del monitor de sesion.");
    return;
  }

  let expirationTimerId = 0;
  let lastActivitySentAt = 0;
  let activityRequestInFlight = false;
  let sessionClosureTriggered = false;

  const redirectToExpiredLogin = () => {
    if (sessionClosureTriggered) {
      return;
    }

    sessionClosureTriggered = true;
    window.location.assign(sessionExpiredLoginUrl);
  };

  const processSessionResponse = async (response) => {
    let data = null;

    try {
      data = await response.json();
    } catch {
      data = null;
    }

    if (
      !response.ok &&
      data &&
      typeof data.status === "string" &&
      ["cookie_missing", "session_not_found", "session_inactive", "session_expired"].includes(data.status)
    ) {
      redirectToExpiredLogin();
    }
  };

  const sendActivityPing = async () => {
    if (activityRequestInFlight || sessionClosureTriggered) {
      return;
    }

    activityRequestInFlight = true;
    lastActivitySentAt = Date.now();

    try {
      const response = await fetch(sessionActivityUrl, {
        method: "POST",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
        credentials: "same-origin",
      });
      await processSessionResponse(response);
    } catch (error) {
      console.warn("Agenda Abril session activity error:", error);
    } finally {
      activityRequestInFlight = false;
    }
  };

  const expireSession = async () => {
    if (sessionClosureTriggered) {
      return;
    }

    try {
      await fetch(sessionExpireUrl, {
        method: "POST",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
        credentials: "same-origin",
        keepalive: true,
      });
    } catch (error) {
      console.warn("Agenda Abril session expiration error:", error);
    } finally {
      redirectToExpiredLogin();
    }
  };

  const resetExpirationTimer = () => {
    if (expirationTimerId) {
      window.clearTimeout(expirationTimerId);
    }
    expirationTimerId = window.setTimeout(() => {
      void expireSession();
    }, inactivityTimeoutMs);
  };

  const registerUserActivity = () => {
    if (sessionClosureTriggered) {
      return;
    }

    resetExpirationTimer();

    if (Date.now() - lastActivitySentAt >= activityThrottleMs) {
      void sendActivityPing();
    }
  };

  ["click", "keydown", "mousemove", "scroll"].forEach((eventName) => {
    window.addEventListener(eventName, registerUserActivity, { passive: true });
  });

  resetExpirationTimer();
});
