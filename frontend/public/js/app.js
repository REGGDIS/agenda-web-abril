document.addEventListener("DOMContentLoaded", () => {
  console.info("Agenda Abril: frontend base cargado.");

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

    if (startsAt instanceof Date && !Number.isNaN(startsAt.getTime())) {
      const refreshCountdown = () => {
        nextActivityCountdown.textContent = formatRemainingTime(startsAt);
      };

      refreshCountdown();
      window.setInterval(refreshCountdown, 30000);
    }
  }
});
