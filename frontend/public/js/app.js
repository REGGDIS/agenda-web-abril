document.addEventListener("DOMContentLoaded", () => {
  console.info("Agenda Abril: frontend base cargado.");

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
});
