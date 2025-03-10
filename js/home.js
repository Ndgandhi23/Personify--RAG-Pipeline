//Fetch the email from the url request to access the home page + populate it + store it for other pages.
const userEmailElement = document.querySelector('.account-email .nav-email'); //Get the current user's email!
const logoutButton = document.querySelector('.logout-button');

//Execute event listener once the home page has been fully rendered from the html/css
document.addEventListener('DOMContentLoaded', () => {
    //Get email from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const email = urlParams.get('email');
    
    //If the user 
    if (!email) {
        window.location.href = '/login.html';
        return;
    }
    
    localStorage.setItem('userEmail', decodeURIComponent(email));
    
    //Display user email in navbar
    if (userEmailElement) {
        userEmailElement.textContent = localStorage.getItem('userEmail');
    }

    //Set the logout button content.
    if(logoutButton){
        logoutButton.children[0].textContent = "Logout"
    }
});

if (logoutButton){
    //Logout button functionality
    logoutButton.addEventListener('click', () => {
        //Redirect back to the login page.
        localStorage.removeItem('userEmail'); //Remove before logging out.
        window.location.href = '/login.html';
        //PLEASE FIX the below part -> Once you logout, do not go back to home page with your email!
        history.pushState(null, null, '/home.html');
        // Listen for the back button or any popstate event.
        // When that happens, force a redirect to the home page.
        window.addEventListener('popstate', function(event) {
            window.location.href = '/home.html';
        });
    })
}else{
    console.log("Logout button not working.")
}

function refreshApplicationGrid(data) {

    $('.app-count').text(`Viewing ${data.length} applications`)

    data.forEach((email, index) => {
    
        Object.values(email).forEach((value, key) => {
            const backgroundColor = (index % 2 === 0 ? '#efefef' : 'white');
            const valueElement = $('<div></div>').text(value).css({
                'background-color': backgroundColor,
                'padding': '8px'
            });
    
            // Special handling for status column (4th column, key === 3)
            if (key === 3) {
                valueElement.empty(); // Remove the direct text
                const statusColor = value === 'rejected' ? '#ff5252' : 
                                  (value === 'offer' ? '#35ff35' : 
                                  (value === 'pending' ? 'rgb(255, 210, 31)' : 
                                  (value === 'interview' ? '#6c6cf1' : 'white')));
                
                const innerElement = $('<div></div>')
                    .text(value.charAt(0).toUpperCase() + value.slice(1))
                    .css({
                        'background-color': statusColor,
                        'color': 'white',
                        'padding': '0.7rem 1.2rem',
                        'border-radius': '0.8rem',
                        'display': 'block',
                        'text-align': 'center'
                    });
                
                valueElement.append(innerElement);
            }
            
            $('.application-grid').append(valueElement);
        });
    })
}



const debug = false;

$(document).ready(function() {
    if (debug === true) {
        //Refresh the application grid for any changes to the application collection.
        refreshApplicationGrid(exampleData);
    }
})

$('.new-btn').click(function() {
    $(this).hide();
    $('.new-input-wrapper').slideDown();
})

//For manually entering job applications
$('.confirm-btn').click(function() {
    const [date, company, role, email] = $('.input-field').map((_, el) => $(el).val()).get(), status = $('.status-dropdown').val();

    // Check if any field is missing
    if (!date || !company || !role || !email || !status) {
        $('.add-error').text('Please enter all required fields!').show(); // Show error if any field is missing
        return; // Exit the function early
    }

    //Prepare the application document.
    const payload = {
        'user_email': userEmailElement.textContent,
        'company': company,
        'role': role,
        'date': date,
        'company_email': email,
        'status': status
    }

    //Send the POST rrequest to manually add a new application.
    $.ajax({
        url: 'http://127.0.0.1:5000/jobstatuses',
        type: 'POST',  // Explicitly set the method
        data: JSON.stringify(payload),  // Convert payload to JSON string
        contentType: 'application/json',  // Ensure JSON format
        dataType: 'json',  // Expect JSON response
        success: function(data) {
            if (data.success) {
                alert('Application added successfully!');
                $('.new-input-wrapper').hide();
                $('.new-btn').show();
            } else {
                alert('Failed to add application. Please try again.');
            }
        },
        error: function(xhr, status, error) {
            console.error("Error:", status, error);
            alert('Something went wrong: ' + xhr.responseText);
        }
    });
})
