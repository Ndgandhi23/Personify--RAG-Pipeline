// Add cooldown tracking at the top of file
let lastMessageTime = 0;
const COOLDOWN_PERIOD = 5010; // 5 seconds in milliseconds

// Function that displays a message in the login system.
const displayMessage = ($container, message, type = 'error') => {
  // Check if enough time has passed since last message
  const currentTime = Date.now();
  if (currentTime - lastMessageTime < COOLDOWN_PERIOD) {
    return;
  }
  // Remove any existing messages first
  $container.find('.message').remove();
  // Create and style new message
  const $messageElement = $('<p></p>', {
    class: `message ${type}`,
    text: message,
    css: {
      color: type === 'error' ? 'red' : 'green',
      padding: '0 10px', // Vertically center the message through padding on top + bottom!
      borderRadius: '5px',
      fontWeight: 'bold',
      margin: '0',
      opacity: 1,
      transition: 'opacity 0.5s ease',
      display: 'inline-block',
      verticalAlign: 'middle', // Vertically center the message
    },
  });

  // Ensure the container has proper alignment
  $container.css({
    position: 'relative',
    display: 'flex-col',
    alignItems: 'center', // Vertically center content inside the container
  });

  $container.append($messageElement);
  lastMessageTime = currentTime;

  // Auto-remove after 5 seconds
  setTimeout(() => {
    $messageElement.css('opacity', '0');
    setTimeout(() => {
      $messageElement.remove();
    }, 500);
  }, 5000);
};

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

  // Handle event logic when clicking outside the following elements
  $(document).click(function (event) {
    // New Question Form
    const $form = $("#newQuestionForm");
    const $button = $("#addQuestionButton");
    if (
      !$form.is(event.target) &&
      $form.has(event.target).length === 0 &&
      !$button.is(event.target)
    ) {
      $form.fadeOut(300, function () {
        $form.addClass("hidden"); // Add the hidden class after fade-out animation
      });
    }
  });
});

//Function that sends an email when you click on the submit button.
const sendEmail = (person_name, email, subj, msg) => {
  const tempDiv = document.getElementById('status');
   //Basic validation of contact page fields.
   if (subj === ''){
    const invalidSubjectMsg = '<p style="color: red; padding: 10px; border-radius: 5px; font-weight: bold;">' +
    'Please provide a subject.' +
    '</p>';
    tempDiv.innerHTML = invalidSubjectMsg;
    return;
  } else if (msg === ''){
      const invalidMsg = '<p style="color: red; padding: 10px; border-radius: 5px; font-weight: bold;">' +
      'Please provide a message.' +
      '</p>';
      tempDiv.innerHTML = invalidMsg;
      return;
  }

  //Preparing the email data for communicating the api to send the email.
  const emailData = {
    name: person_name, 
    email: email, 
    subject: subj, 
    message: msg
  }

  //Make a post request to the contact endpoint.
  $.ajax({
    url: 'http://127.0.0.1:5000/send_email',
    type: 'POST',
    data: JSON.stringify(emailData),
    contentType: 'application/json',
    success: function (response) {
      // Clear the fields (variables + input fields)
      $('#personName').val('');
      $('#emailAddress').val('');
      $('#subject').val('');
      $('#message').val('');

      // Add a success message using displayMessage
      displayMessage($(".contact-form"), 'You will receive an email back within 1-2 business days. Thank you for contacting us!', 'success');
    },
    error: function (xhr, status, error) {
      console.log("Error: " + error);
      // Have an email message prepared just in case the email doesn't get sent.
      displayMessage($(".contact-form"), 'Unexpected email submission error, please try again.', 'error');
    }
  });
};

// Event listener for contact form submissions
$(".send-message").on("click", function () {
  //Retrieve the basic/necessary fields for making contact form submissions.
  const personName = $(".profile-pic .name").text(); //Get name = text of name field
  const emailAddress = $(".profile-pic .email").text();
  const subject = $("#subject").val(); //Get value of subject input field
  const message = $("#message").val();

  sendEmail(personName, emailAddress, subject, message);
});