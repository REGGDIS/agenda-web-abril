(() => {
  const emojiInput = document.querySelector("[data-emoji-input]");
  const categorySelect = document.querySelector("[data-category-select]");
  const emojiSuggestionSelect = document.querySelector(
    "[data-emoji-suggestion-select]"
  );

  if (
    !(emojiInput instanceof HTMLInputElement)
    || !(categorySelect instanceof HTMLSelectElement)
    || !(emojiSuggestionSelect instanceof HTMLSelectElement)
  ) {
    return;
  }

  const emojiSuggestionsByCategory = {
    trabajo: ["📌", "💼", "🗂️", "📞"],
    estudio: ["📚", "🧠", "📝", "🎓"],
    personal: ["🏡", "☕", "🎉", "🛒"],
    salud: ["💪", "🏥", "💊", "🚶"],
  };

  const fallbackSuggestions = ["📌", "✅", "🗓️", "⭐"];

  const normalizeCategoryLabel = (label) =>
    label
      .trim()
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");

  const resolveSuggestions = () => {
    const selectedOption = categorySelect.selectedOptions[0];
    if (!(selectedOption instanceof HTMLOptionElement) || !selectedOption.value) {
      return [];
    }

    const normalizedLabel = normalizeCategoryLabel(selectedOption.textContent ?? "");
    return emojiSuggestionsByCategory[normalizedLabel] ?? fallbackSuggestions;
  };

  const createSuggestionOption = (emoji, label) => {
    const option = document.createElement("option");
    option.value = emoji;
    option.textContent = label;
    return option;
  };

  const renderSuggestions = () => {
    const suggestions = resolveSuggestions();
    emojiSuggestionSelect.replaceChildren();

    emojiSuggestionSelect.append(
      createSuggestionOption("", suggestions.length > 0 ? "Sugeridos" : "Sin sugerencias")
    );
    emojiSuggestionSelect.value = "";
    emojiSuggestionSelect.disabled = suggestions.length === 0;

    suggestions.forEach((emoji) => {
      emojiSuggestionSelect.append(createSuggestionOption(emoji, emoji));
    });
  };

  categorySelect.addEventListener("change", renderSuggestions);
  emojiSuggestionSelect.addEventListener("change", () => {
    if (emojiSuggestionSelect.value) {
      emojiInput.value = emojiSuggestionSelect.value;
      emojiInput.focus();
      emojiSuggestionSelect.value = "";
    }
  });

  renderSuggestions();
})();
