//Fetch the email from the url request to access the home page + populate it + store it for other pages.
const userEmailElement = document.querySelector('.account-email .nav-email'); //Get the current user's email!
document.addEventListener('DOMContentLoaded', () => {
    //Get email from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const email = urlParams.get('email');
    if (!email && !localStorage.getItem('userEmail')) {
        //Redirect to login if no email found in URL or localStorage
        window.location.href = '/login.html';
        return;
    }
    //If email exists in URL, update localStorage
    if (email) {
        localStorage.setItem('userEmail', decodeURIComponent(email));
    }
    
    //Display user email in navbar (use URL param or stored email)
    if (userEmailElement) {
        userEmailElement.textContent = email || localStorage.getItem('userEmail');
    }
});

const logoutButton = document.querySelector('.logout-button');
if (logoutButton){

    logoutButton.addEventListener('click', () => {
        //Redirect back to the login page.
        localStorage.removeItem('userEmail'); //Remove before logging out.
        window.location.href = '/login.html';
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
        refreshApplicationGrid(exampleData);
    }
})

$('.new-btn').click(function() {
    $(this).hide();
    $('.new-input-wrapper').slideDown();
})


$('.confirm-btn').click(function() {
    const date = $('.input-field:first-child').val();
    const company = $('.input-field:nth-child(2)').val();
    const email = $('.input-field:nth-child(3)').val();
    const status = $('.status-dropdown').val();

    // Check if any field is missing
    if (!date || !company || !email || !status) {
        $('.add-error').text('Please enter all required fields!').show(); // Show error if any field is missing
        return; // Exit the function early
    }

    const payload = {
        'company': company,
        'date': date,
        'company_email': email,
        'status': status
    }

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

