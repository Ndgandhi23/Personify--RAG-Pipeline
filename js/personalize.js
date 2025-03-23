$(document).ready(function () {
  // Tab switching logic
  const $tabButtons = $(".sidebar-button, .mobile-menu-button, .tab-button");
  const $tabContents = $(".tab-content");

  function showTab(tabId) {
    $tabContents.addClass("hidden");
    $("#" + tabId + "Section").removeClass("hidden");

    $(".sidebar-button").each(function () {
      if ($(this).attr("data-tab") === tabId) {
        $(this).addClass("bg-blue-500 text-white");
      } else {
        $(this).removeClass("bg-blue-500 text-white");
      }
    });
  }

  $tabButtons.on("click", function () {
    const tab = $(this).attr("data-tab");
    if (tab) {
      showTab(tab);
      $("#mobileMenu").addClass("hidden");
    }
  });

  // Initial tab (FAQ)
  showTab("faq");

  // Mobile menu toggling
  $("#mobileMenuButton").on("click", function () {
    $("#mobileMenu").toggleClass("hidden");
  });

  // FAQ toggle logic
  $(".faq-question").on("click", function () {
    const $answer = $(this).next();
    if ($answer.hasClass("hidden")) {
      $answer.removeClass("hidden");
      $(this).find(".faq-toggle").text("-");
    } else {
      $answer.addClass("hidden");
      $(this).find(".faq-toggle").text("+");
    }
  });

  // Settings toggle logic
  $(".settings-toggle").on("click", function () {
    const currentText = $.trim($(this).text());
    $(this).text(currentText === "Off" ? "On" : "Off");
  });

  // Add New Question Button: Toggle new question form
  $("#addQuestionButton").on("click", function () {
    $("#newQuestionForm").toggleClass("hidden");
  });

  // Submit New Question: Append a new FAQ item
  $("#submitQuestionButton").click(function () {
    const questionText = $("#newQuestionInput").val().trim();
    if (questionText !== "") {
      // Create new FAQ item; no answer provided initially.
      const $newFAQ = $(`
        <div class="faq-item border p-4 rounded">
          <div class="faq-question cursor-pointer flex justify-between">
            <span class="font-semibold">${questionText}</span>
            <span class="faq-toggle">+</span>
          </div>
          <div class="faq-answer hidden mt-2">
            Answer not provided.
          </div>
        </div>
      `);
      // Make a POST request to /addquestion endpoint
      $.ajax({
        url: "http://127.0.0.1:5000/addquestion",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({ question: questionText }),
        success: function (response) {
          console.log("Question added successfully:", response);
        },
        error: function (xhr, status, error) {
          console.error("Error adding question:", error);
        },
      });
      $("#faqList").append($newFAQ);
      // Reset the input and hide the form.
      $("#newQuestionInput").val("");
      $("#newQuestionForm").addClass("hidden");
      // Attach toggle event to the new FAQ question.
      $newFAQ.find(".faq-question").on("click", function () {
        const $ans = $(this).next();
        if ($ans.hasClass("hidden")) {
          $ans.removeClass("hidden");
          $(this).find(".faq-toggle").text("-");
        } else {
          $ans.addClass("hidden");
          $(this).find(".faq-toggle").text("+");
        }
      });
    }
  });
});

// Handle event logic when clicking outside newQuestionForm
$(document).click(function (event) {
  const $form = $("#newQuestionForm");
  const $button = $("#addQuestionButton");
  if (!$form.is(event.target) && $form.has(event.target).length === 0 && !$button.is(event.target)) {
    $form.addClass("hidden"); //Add or remove classes
  }
});