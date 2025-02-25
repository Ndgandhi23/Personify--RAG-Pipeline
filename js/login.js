const registerForm = document.querySelector('.form-box.register');
const loginForm = document.querySelector('.form-box.login');

function toggleForms() {
    registerForm.classList.toggle('active');
    loginForm.classList.toggle('active');
}

document.querySelectorAll('.toggle-panel button').forEach(button => {
    button.addEventListener('click', () => {
        document.querySelector('.container').classList.toggle('active');
    });
});


let click = 0 //Switching between login and register message in toggle box.
const togglePanel = {
    1: {
        "Header": "Welcome Back!",
        "Paragraph": "Already have an account?",
        "Button Name": "Login"
    },
    0:{
        "Header": "Hello, Welcome!",
        "Paragraph": "Don't have an account?",
        "Button Name": "Register"
    }
}

const togglePanelEl = document.querySelector('.toggle-panel');
const button = document.querySelector('.toggle-panel button');
//Set an event listener for the button to change the content when rendering.
button.addEventListener('click', () => {
    if (click == 0){
        click = 1;
    }else{
        click = 0;
    }
    //Change the corresponding fields with a transition
    const toggleFields = togglePanel[click];
    setTimeout(() => {
        //Getting and retrieving the corresponding fields respectively.
        let header = togglePanelEl.querySelector("h1");
        header.innerHTML = toggleFields["Header"];

        let para = togglePanelEl.querySelector("p");
        para.innerHTML = toggleFields["Paragraph"];

        let buttonName = togglePanelEl.querySelector("button");
        buttonName.innerHTML = toggleFields["Button Name"];
    }, 500);
})

//Retrieve login input fields.
const usernameField = document.querySelector('.login-form input[type="email"]');
const passwordField = document.querySelector('.login-form input[type="password"]');

//Retrieve register input fields.
const emailField = document.querySelector('.register-form input[type="email"]');
const passField = document.querySelector('.register-form input[type="password"]');

//Get the login and register pages for error handling.
const loginPage = document.querySelector('.login-form');
const loginBtn = document.querySelector('.login-btn');
const registerPage = document.querySelector('.register-form');
const registerBtn = document.querySelector('.register-button');

const isValidEmail = (email) => {
    const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.(com)$/;
    return emailRegex.test(email);
}

const isValidPassword = (password) => {
    const passwordRegex = /^(?=.*[!@#?])(?!.*[!@#?]{2})[a-zA-Z0-9!@#?]{8,128}$/;
    return passwordRegex.test(password);
}

// Add cooldown tracking at the top of file
let lastMessageTime = 0;
const COOLDOWN_PERIOD = 10000; // 10 seconds in milliseconds

//Function that displays a message in the login system.
const displayMessage = (container, message, type = 'error') => {
// Check if enough time has passed since last message
    const currentTime = Date.now();
    if (currentTime - lastMessageTime < COOLDOWN_PERIOD) {
        console.log('Message cooldown in effect. Please wait.');
        return;
    }

    // Remove any existing messages first
    const existingMessages = container.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());

    // Create and style new message
    const messageElement = document.createElement('p');
    messageElement.className = `message ${type}`;
    messageElement.style.cssText = `
        color: ${type === 'error' ? 'red' : 'green'};
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
        margin: 10px 0;
        opacity: 1;
        transition: opacity 0.5s ease;
    `;
    messageElement.textContent = message;

    container.insertBefore(messageElement, container.children[5]);
    lastMessageTime = currentTime;

    // Auto-remove after 5 seconds
    setTimeout(() => {
        messageElement.style.opacity = '0';
        setTimeout(() => {
            messageElement.remove();
        }, 500);
    }, 5000);
}

//Functionality for login and register.
const handleLogin = () => {
    //Retrieve username, email, and password.
    const password = passwordField.value;
    const email = usernameField.value;
    
    //Validate required fields.
    if (!isValidEmail(email)){
        let invalidEmailMsg = 'Please enter your email in a correct format.';
        //If the email service is off.
        if (!(email.includes('gmail') || email.includes('hotmail') || email.includes('yahoo'))){
            invalidEmailMsg = 'Invalid Email Service (Supported types: Gmail, Hotmail, Yahoo)';
        }
        displayMessage(loginPage, invalidEmailMsg, 'error');
        return;
    }
 
    const sensitive_info = {your_email: email, pass: password};
    //Make a post request to the login API endpoint.
    //Asynchronous calls
    $.ajax({
        url: 'http://127.0.0.1:5000/login',
        type: 'POST',  // Explicitly set the method
        data: JSON.stringify(sensitive_info),  // Convert payload to JSON string
        contentType: 'application/json',  // Ensure JSON format
        dataType: 'json',  // Expect JSON response
        success: function(data, textStatus, xhr) {
            // Check for successful HTTP status codes (200-299)
            if (xhr.status >= 200 && xhr.status < 300) {
                //Redirect to home page after successful login!
            }
        },
        error: function(xhr, status, error) {
            let errorMessage = 'An error occurred during registration.';
            // Handle different error scenarios
            if (xhr.responseJSON?.message) {
                errorMessage = xhr.responseJSON.message;
            }else{
                return;
            }
            
            displayMessage(loginPage, errorMessage, 'error');
      }
    });
}


const handleRegistration = () => {
    //Retrieve username, email, and password.
    const password = passField.value;
    const email = emailField.value;
    
    //Validate required fields.
    if (!isValidEmail(email)){
        let invalidEmailMsg = 'Please enter your email in a correct format.';
        //If the email service is off.
        if (!(email.includes('gmail') || email.includes('hotmail') || email.includes('yahoo'))){
            invalidEmailMsg = 'Invalid Email Service (Supported types: Gmail, Hotmail, Yahoo)';
        }
        displayMessage(registerPage, invalidEmailMsg, 'error');
        return;
    } else if (!isValidPassword(password)){
        displayMessage(registerPage, 'Please provide a valid password, as mentioned in the requirements above.', 'error');
        return;
    }
 
    const sensitive_info = {your_email: email, pass: password};
    //Make a post request to the login API endpoint.
    //Asynchronous calls
    $.ajax({
        url: 'http://127.0.0.1:5000/registration',
        type: 'POST',  // Explicitly set the method
        data: JSON.stringify(sensitive_info),  // Convert payload to JSON string
        contentType: 'application/json',  // Ensure JSON format
        dataType: 'json',  // Expect JSON response
        success: function(data, textStatus, xhr) {
            // Check for successful HTTP status codes (200-299)
            if (xhr.status >= 200 && xhr.status < 300) {
                displayMessage(registerPage, 'Registration successful, you are now a Personify user!', 'success');
                //Redirect to home page after successful registration!
            }
        },
        error: function(xhr, status, error) {
            let errorMessage = 'An error occurred during registration.';
            // Handle different error scenarios
            if (xhr.responseJSON?.message) {
                errorMessage = xhr.responseJSON.message;
            } else{
                return;
            }
            displayMessage(registerPage, errorMessage, 'error');
      }
    });
}

// Setting up event listeners for the login and register buttons, preventing a full page reload
// for form submissions.
loginBtn.addEventListener('click', (e) => handleLogin(e));
document.querySelector('.login-form').addEventListener('submit', (e) => e.preventDefault());

registerBtn.addEventListener('click', (e) => handleRegistration(e));
document.querySelector('.register-form').addEventListener('submit', (e) => e.preventDefault());