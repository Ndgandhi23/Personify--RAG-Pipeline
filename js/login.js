//Accessing our three forms.
const registerForm = document.querySelector(".form-box.register");
const loginForm = document.querySelector(".form-box.login");
const forgotPasswordForm = document.querySelector(".form-box.forgot-password");

//Toggling between the login, register, and forgot-password forms through the toggle box on the left.
function toggleForms() {
  registerForm.classList.toggle("active");
  loginForm.classList.toggle("active");
  forgotPasswordForm.classList.toggle("active");
}

const forgotLink = document.querySelector(".forgot-link"); //Fetching the forgot link to redirect to forgot password form.
forgotLink.addEventListener("click", (e) => {
  //Make forgotPassword active and login and register form to be inactive to only display the forgot password form.
  e.preventDefault();
  loginForm.classList.remove("active");
  registerForm.classList.remove("active");
  forgotPasswordForm.classList.add("active");
});

document.querySelectorAll(".toggle-panel button").forEach((button) => {
  button.addEventListener("click", () => {
    const container = document.querySelector(".container");
    container.classList.toggle("active");
    //Switching between login and register in the container.
    if (!forgotPasswordForm.classList.contains("active")) {
      loginForm.classList.toggle("active");
      registerForm.classList.toggle("active");
    }
  });
});

//Set functionality for the forgot password button and page.
const forgotPasswordBtn = document.querySelector(".forgot-password-button");
const forgotPasswordPage = document.querySelector(".forgot-password-form");

//Add cooldown tracking at the top of file
let lastMessageTime = 0;
const COOLDOWN_PERIOD = 10000; //10 seconds in milliseconds

//Function that displays a message in the login system.
const displayMessage = (container, message, type = "error") => {
  // Check if enough time has passed since last message
  const currentTime = Date.now();
  if (currentTime - lastMessageTime < COOLDOWN_PERIOD) {
    return;
  }
  //Remove any existing messages first
  const existingMessages = container.querySelectorAll(".message");
  existingMessages.forEach((msg) => msg.remove());

  //Create and style new message
  const messageElement = document.createElement("p");
  messageElement.className = `message ${type}`;
  messageElement.style.cssText = `
        color: ${type === "error" ? "red" : "green"};
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
        margin: 10px 0;
        opacity: 1;
        transition: opacity 0.5s ease;
    `;
  messageElement.textContent = message;

  //Insert it before a new position.
  container.insertBefore(messageElement, container.children[5]);
  lastMessageTime = currentTime;

  //Auto-remove after 5 seconds
  setTimeout(() => {
    messageElement.style.opacity = "0";
    setTimeout(() => {
      messageElement.remove();
    }, 500);
  }, 8000);
};

//Regex for validating email and password.
const isValidEmail = (email) => {
  const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.(com)$/;
  return emailRegex.test(email);
};

const isValidPassword = (password) => {
  const passwordRegex = /^(?=.*[!@#?])(?!.*[!@#?]{2})[a-zA-Z0-9!@#?]{8,128}$/;
  return passwordRegex.test(password);
};

//Functionality for forgot password form.
const forgotPassword = (e) => {
  e.preventDefault(); // Prevent form submission/page reload, which is default behavior at end of submission event listener method.
  try {
    // Retrieve email field from the forgot-password form
    const emailField = forgotPasswordPage.querySelector('input[type="email"]');
    const newPasswordField = forgotPasswordPage.querySelector(
      'input[type="password"]'
    );
    //Retrieve email and new password values
    const newPassword = newPasswordField.value;
    const email = emailField.value;
    // Validate email and new password formats
    if (!isValidEmail(email)) {
      displayMessage(
        forgotPasswordPage,
        "Please enter a valid email address.",
        "error"
      );
      return;
    } else if (!isValidPassword(newPassword)) {
      displayMessage(
        forgotPasswordPage,
        "Please provide a valid new password, as mentioned in the requirements above.",
        "error"
      );
      return;
    }
    // Make a post request to the forgot password API endpoint
    const sensitive_info = { your_email: email, new_password: newPassword };
    $.ajax({
      url: "http://127.0.0.1:8000/forgot-password",
      type: "POST",
      data: JSON.stringify(sensitive_info),
      contentType: "application/json",
      dataType: "json",
      success: function (data, textStatus, xhr) {
        if (xhr.status >= 200 && xhr.status < 300) {
          displayMessage(
            forgotPasswordPage,
            "Password reset successful!",
            "success"
          );
          // Add slight delay to show success message before redirect
          setTimeout(() => {
            //If successful
            forgotPasswordForm.classList.remove("active");
            loginForm.classList.add("active");
          }, 1500);
        }
      },
      error: function (xhr, status, error) {
        let errorMessage = "An error occurred during password reset.";
        if (xhr.responseJSON?.message) {
          errorMessage = xhr.responseJSON.message;
        }
        displayMessage(forgotPasswordPage, errorMessage, "error");
      },
    });
  } catch (error) {
    setTimeout(() => {
      console.error("Message:", error.message);
      console.error("Line Number:", error.lineNumber);
    }, 1500);
  }
};

forgotPasswordBtn.addEventListener("click", (e) => {
  forgotPassword(e);
});

//Logic for rendering the right content in the toggle box when toggling.
let click = 0; //Switching between login and register message in toggle box.
const togglePanel = {
  1: {
    Header: "Welcome Back!",
    Paragraph: "Already have an account?",
    "Button Name": "Login",
  },
  0: {
    Header: "Hello, Welcome!",
    Paragraph: "Don't have an account?",
    "Button Name": "Register",
  },
};

const togglePanelEl = document.querySelector(".toggle-panel");
const button = document.querySelector(".toggle-panel button");

//Set an event listener for the button to change the content when rendering.
button.addEventListener("click", () => {
  if (click == 0) {
    click = 1;
    loginForm.classList.remove("active");
    registerForm.classList.add("active");
  } else {
    click = 0;
    registerForm.classList.remove("active");
    loginForm.classList.add("active");
  }
  //Change the corresponding fields with a transition
  const toggleFields = togglePanel[click];
  setTimeout(() => {
    //Getting and setting the corresponding fields respectively.
    let header = togglePanelEl.querySelector("h1");
    header.innerHTML = toggleFields["Header"];

    let para = togglePanelEl.querySelector("p");
    para.innerHTML = toggleFields["Paragraph"];

    let buttonName = togglePanelEl.querySelector("button");
    buttonName.innerHTML = toggleFields["Button Name"];
  }, 500);
});

//Function redirecting to the home page after successful login.
const redirectToHome = (email) => {
  // Encode email to safely pass in URL
  localStorage.setItem("email", email);
  const encodedEmail = encodeURIComponent(email);
  window.location.href = `/newhome.html?email=${encodedEmail}`;
};

//Get the login and register pages for error handling.
const loginPage = document.querySelector(".login-form");
const loginBtn = document.querySelector(".login-btn");
const registerPage = document.querySelector(".register-form");
const registerBtn = document.querySelector(".register-button");

//Retrieve login input fields.
const usernameField = loginPage.querySelector('input[type="email"]');
const passwordField = loginPage.querySelector('input[type="password"]');

//Functionality for login and register.
const handleLogin = () => {
  //Retrieve username, email, and password.
  const password = passwordField.value;
  const email = usernameField.value;

  //Validate required fields.
  if (!isValidEmail(email)) {
    let invalidEmailMsg = "Please enter your email in a correct format.";
    //If the email service is off.
    if (
      !(
        email.includes("gmail") ||
        email.includes("hotmail") ||
        email.includes("yahoo")
      )
    ) {
      invalidEmailMsg =
        "Invalid Email Service (Supported types: Gmail, Hotmail, Yahoo)";
    }
    displayMessage(loginPage, invalidEmailMsg, "error");
    return;
  }

  const sensitive_info = { your_email: email, pass: password };
  //Make a post request to the login API endpoint.
  //Asynchronous calls
  $.ajax({
    url: "http://127.0.0.1:8000/login",
    type: "POST", // Explicitly set the method
    data: JSON.stringify(sensitive_info), // Convert payload to JSON string
    contentType: "application/json", // Ensure JSON format
    dataType: "json", // Expect JSON response
    success: function (data, textStatus, xhr) {
      // Check for successful HTTP status codes (200-299)
      if (xhr.status >= 200 && xhr.status < 300) {
        //Redirect to home page after successful login!
        displayMessage(loginPage, "Login successful!", "success");
        // Add slight delay to show success message before redirect
        setTimeout(() => {
          redirectToHome(email);
        }, 1500);
      }
    },
    error: function (xhr, status, error) {
      let errorMessage = "An error occurred during registration.";
      // Handle different error scenarios
      if (xhr.responseJSON?.message) {
        errorMessage = xhr.responseJSON.message;
      } else {
        return;
      }
      //Display an error message for failure in forgot password.
      displayMessage(loginPage, errorMessage, "error");
    },
  });
};

//Retrieve register input fields.
const emailField = registerPage.querySelector('input[type="email"]');
const passField = registerPage.querySelector('input[type="password"]');

//Function to handle registration functionality.
const handleRegistration = () => {
  //Retrieve username, email, and password.
  const password = passField.value;
  const email = emailField.value;

  //Validate required fields.
  if (!isValidEmail(email)) {
    let invalidEmailMsg = "Please enter your email in a correct format.";
    //If not using a valid email service.
    if (
      !(
        email.includes("gmail") ||
        email.includes("hotmail") ||
        email.includes("yahoo")
      )
    ) {
      invalidEmailMsg = "Invalid Email Service";
    }
    displayMessage(registerPage, invalidEmailMsg, "error");
    return;
  } else if (!isValidPassword(password)) {
    displayMessage(
      registerPage,
      "Please provide a valid password, as mentioned in the requirements above.",
      "error"
    );
    return;
  }

  const sensitive_info = { your_email: email, pass: password };
  //Make a post request to the login API endpoint.
  //Asynchronous calls
  $.ajax({
    url: "http://127.0.0.1:8000/registration",
    type: "POST", // Explicitly set the method
    data: JSON.stringify(sensitive_info), // Convert payload to JSON string
    contentType: "application/json", // Ensure JSON format
    dataType: "json", // Expect JSON response
    success: function (data, textStatus, xhr) {
      // Check for successful HTTP status codes (200-299)
      if (xhr.status >= 200 && xhr.status < 300) {
        displayMessage(
          registerPage,
          "Registration successful, you are now a Personify user!",
          "success"
        );
        //Redirect to home page after successful registration!
        displayMessage(registerPage, "Registration successful!", "success");
        setTimeout(() => {
          redirectToHome(email);
        }, 1500);
      }
    },
    error: function (xhr, status, error) {
      let errorMessage = "An error occurred during registration.";
      // Handle different error scenarios
      if (xhr.responseJSON?.message) {
        errorMessage = xhr.responseJSON.message;
      } else {
        return;
      }
      displayMessage(registerPage, errorMessage, "error");
    },
  });
};

// Setting up event listeners for the login and register buttons, preventing a full page reload
// for form submissions.
loginBtn.addEventListener("click", (e) => handleLogin(e));
loginPage.addEventListener("submit", (e) => e.preventDefault());

registerBtn.addEventListener("click", (e) => handleRegistration(e));
registerPage.addEventListener("submit", (e) => e.preventDefault());
