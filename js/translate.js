// When document is ready to load, set default language to English.
$(document).ready(() => {
  if (!localStorage.getItem("language")) {
    localStorage.setItem("language", "en");
  }

  // Configuration setup for the i18next library.
  i18next
    .use(i18nextHttpBackend) // Load translations via HTTPS
    .use(i18nextBrowserLanguageDetector) // Detect user language
    .init(
      {
        fallbackLng: "en", // Default language
        debug: true, // Enable debug mode
        backend: {
          loadPath: "https://your-secure-domain.com/locales/{{lng}}.json", // Secure HTTPS path to translation files
        },
        lng: localStorage.getItem("language") || "en", // Load saved language or default to English
      },
      (err, t) => {
        if (err) return console.error(err);
        updateContent(); // Update content after initialization
      }
    );

  // Function to update content dynamically
  function updateContent() {
    $("[class], [id]").each(function () {
      const keyClass = $(this).attr("class");
      const keyId = $(this).attr("id");
      if (keyClass && i18next.exists(keyClass)) {
        $(this).text(i18next.t(keyClass)); // Translate using class key
      } else if (keyId && i18next.exists(keyId)) {
        $(this).text(i18next.t(keyId)); // Translate using id key
      }
    });
  }

  // Event listener for language change
  var selectLang = $("#languageSelector");
  if($("#languageSelector").length == 0){
    $("#languageSelector").on("change", (e) => {
      const selectedLanguage = $(e.target).val();
      i18next.changeLanguage(selectedLanguage, () => {
        switch (selectedLanguage) {
          case "English":
            selectedLanguage = "en";
            break;
          case "Spanish":
            selectedLanguage = "es";
            break;
          case "French":
            selectedLanguage = "fr";
            break;
          case "German":
            selectedLanguage = "de";
            break;
          case "Chinese":
            selectedLanguage = "zh";
            break;
          default:
            selectedLanguage = "en"; // Default to English if no match
            break;
        }
        localStorage.setItem("language", selectedLanguage); // Save selected language
        updateContent();
      });
    });
  }
});