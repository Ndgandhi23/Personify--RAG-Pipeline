//Search engine functionality
$(document).ready(function () {
    // Ensure the search overlay is hidden initially.
    $("#searchOverlay").hide();
    
    // When the search button is clicked, show the inline overlay.
    $("#searchButton").on("click", function (e) {
      anyField = $(".date-field").length > 0 || $(".company-field").length > 0 || $(".email-field").length > 0 || $(".status-field").length > 0;
      role = $(".search-engine-input").val()
      console.log(role)
      if (role || anyField){
         //Filter out the applications
         //Get the entered fields and prepare it in the request's payload
         const payload = {};
         if ($(".date-field").length > 0) {
            const dateCondition = $(".date-field select").val(); // Get the selected condition (e.g., "greater", "equal", "less")
            const dateValue = $(".date-field input[type='date']").val(); // Get the entered date value
            payload["date_cond"] = { condition: dateCondition, value: dateValue };
         } if($(".company-field").length > 0) {
            payload["company"] = $(".company-field input").val()
         } if ($(".email-field").length > 0) {
            payload["company_email"] = $(".email-field input").val()
         } if ($(".status-field").length > 0) {
            payload["status"] = $(".status-field select").val()
         } if (role != ""){
            payload["role"] = role
         }

         //Make a POST request to the /filter endpoint
         $.ajax({
            url: "http://127.0.0.1:5000/filter",
            type: "POST",
            data: JSON.stringify(payload),
            contentType: "application/json",
            dataType: "json",
            success: function (response) {
                // Handle the response and refresh the application grid
                refreshApplicationGrid(response.data);
            },
            error: function (xhr, status, error) {
                console.error("Error:", status, error);
                alert("Failed to filter applications. Please try again.");
            }
         });  
      }else{
        e.stopPropagation(); // Prevent event bubbling.
        $("#searchOverlay").fadeIn(200); // Show the overlay with a fade-in effect.
      }
    });
    
    // Functionality for open button to open the search window.
    $(".open-button").on("click", function (e) {
        e.stopPropagation(); // Prevent event bubbling.
        $("#searchOverlay").fadeIn(200); // Show the overlay with a fade-in effect.
    });

    // When the "Close" button is clicked, hide the overlay.
    $("#closeOverlay").on("click", function (e) {
      e.stopPropagation();
      $("#searchOverlay").fadeOut(200);
    });
    
    // Optional: When clicking outside of the overlay, hide it.
    $(document).on("click", function (e) {
      if (!$(e.target).closest("#searchOverlay, #searchButton, #searchButton *").length) {
        $("#searchOverlay").fadeOut(200);
      }
    });
  });

//Set up event functionality when clicking on search results
$(".search-results").children().each(function () {
    $(this).on("click", function () {
        //Set input in search engine to result text
        $(".search-engine-input").val($(this).text().trim());
        //Search Engine overlay closes
        $("#searchOverlay").fadeOut(200);
    });
});

//Set up functionality when clicking on filter checkboxes.
$(document).ready(function(){
    // Listen for changes on the filter checkboxes.
    $("#filterForm input[type='checkbox']").on("change", function(){
      var value = $(this).val(); // e.g., "Date", "Company", "Email", "Status"
      
      if($(this).is(":checked")) { // Checkbox is checked—add the corresponding field
        if(value === "Date"){
          $(this).closest("label").after(
            `<div class="filter-field date-field mt-2">
                <label class="block text-gray-700 mb-1">Date Condition</label>
                <select class="w-full border border-gray-300 rounded p-1 mb-2">
                    <option value="greater">After</option>
                    <option value="equal">On</option>
                    <option value="less">Before</option>
                </select>
                <input type="date" class="w-full border border-gray-300 rounded p-2">
             </div>`
          );
        } else if(value === "Company"){
          $(this).closest("label").after(
            `<div class="filter-field company-field mt-2">
                <label class="block text-gray-700 mb-1">Enter Company</label>
                <input type="text" class="w-full border border-gray-300 rounded p-2" placeholder="Company Name">
             </div>`
          );
        } else if(value === "Email"){
          $(this).closest("label").after(
            `<div class="filter-field email-field mt-2">
                <label class="block text-gray-700 mb-1">Enter Company Email</label>
                <input type="email" class="w-full border border-gray-300 rounded p-2" placeholder="Email">
             </div>`
          );
        } else if(value === "Status"){
          $(this).closest("label").after(
            `<div class="filter-field status-field mt-2">
                <label class="block text-gray-700 mb-1">Select Status</label>
                <select class="w-full border border-gray-300 rounded p-2">
                    <option value="pending">Pending</option>
                    <option value="accepted">Accepted</option>
                    <option value="rejected">Rejected</option>
                    <option value="interview">Interview</option>
                </select>
             </div>`
          );
        }
      } else {
        // Checkbox unchecked—remove the corresponding field container.
        if(value === "Date"){
          $(this).closest("label").next(".date-field").remove();
        } else if(value === "Company"){
          $(this).closest("label").next(".company-field").remove();
        } else if(value === "Email"){
          $(this).closest("label").next(".email-field").remove();
        } else if(value === "Status"){
          $(this).closest("label").next(".status-field").remove();
        }
      }
    });
  });

// Displaying profile modal when clicking on the profile pic.
const profilePic = $(".profile-pic");
const profileModal = $("<div></div>")
    .html(
    `
        <article class="flex flex-col bg-white h-[190px] w-[250px]">
            <header class="flex flex-col">
                <h2 class="name w-full text-lg font-medium text-center text-green-900 h-[23px]">
                    Name
                </h2>
                <p class="email w-full text-base text-center h-[31px] text-green-950">Email</p>
            </header>

            <nav class="flex flex-wrap gap-10 justify-center items-center w-full">
                <button
                    class="flex relative justify-center items-center bg-red-500 h-[50px] w-[100px]"
                    aria-label="View Profile"
                >
                    <div class="absolute top-0 h-5 bg-red-500 w-[100px]"></div>
                    <span class="relative text-xl text-white z-[1]">Profile</span>
                </button>

                <button
                    class="flex relative justify-center items-center bg-red-500 h-[46px] w-[100px]"
                    aria-label="Open Settings"
                >
                    <div class="absolute top-0 h-5 bg-red-500 w-[100px]"></div>
                    <span class="relative text-xl text-center text-white z-[1]">Settings</span>
                </button>

                <button
                    class="logout-button flex relative justify-center items-center bg-red-500 h-[46px] w-[100px]"
                    aria-label="Logout from account"
                >
                    <div class="absolute top-0 h-5 bg-red-500 w-[100px]"></div>
                    <span class="relative text-xl text-white z-[1]">Logout</span>
                </button>
            </nav>
        </article>
    `
    )
    .css({
    position: "absolute",
    top: "20%",
    right: "0.5%",
    display: "none",
    });

$("body").append(profileModal);

profilePic.click(function (event) {
    event.stopPropagation(); // Prevents the event from bubbling up to the document click handler.
    profileModal.toggle();
    if (profileModal.is(":visible")) {
        $(document).ready(function () {
            const userEmailElement = $(".email"); //Get the current user's email!
            const nameElement = $(".name");
            const logoutButton = $(".logout-button");
        
            //Get email from URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            const email = urlParams.get("email");
        
            //If the user is not valid
            if (!email) {
                window.location.href = "/login.html";
                return;
            }
        
            //How do we get the name and the profile pic? (Maybe from google oauth -> Ask Neil for later?)
            
            //Store in localStorage (find a better way pls!)
            localStorage.setItem("userEmail", decodeURIComponent(email));
            //Display user email in navbar
            if (userEmailElement.length) {
                userEmailElement.text(localStorage.getItem("userEmail"));
            }
        });

        const logoutButton = $('.logout-button');
        if (logoutButton) {
            //Logout button functionality
            logoutButton.click(function () {
                //Redirect back to the login page.
                localStorage.removeItem("userEmail"); //Remove before logging out.
                window.location.href = "/login.html";
                /*
                //PLEASE FIX the below part -> Once you logout, do not go back to home page with your email!
                history.pushState(null, null, "/newhome.html");
                // Listen for the back button or any popstate event.
                // When that happens, force a redirect to the home page.
                window.addEventListener("popstate", function (event) {
                    window.location.href = "/newhome.html";
                });
                */
            });
        } else {
            console.log("Logout button not working.");
        }
    }
});

// Set up an event listener for clicking outside any clickable component to close it.
$(document).click(function (event) {
    //Clicking outside the profile modal
    if (
    !profileModal.is(event.target) &&
    !$.contains(profileModal[0], event.target) &&
    event.target !== profilePic[0]
    ) {
    profileModal.hide();
    }
});

function refreshApplicationGrid(data) {
    $(".app-count").text(`Viewing ${data.length} applications`);

    data.forEach((email, index) => {
    Object.values(email).forEach((value, key) => {
        const backgroundColor = index % 2 === 0 ? "#efefef" : "white";
        const valueElement = $("<div></div>").text(value).css({
        "background-color": backgroundColor,
        padding: "8px",
        });

        // Special handling for status column (4th column, key === 3)
        if (key === 3) {
        valueElement.empty(); // Remove the direct text
        const statusColor =
            value === "rejected"
            ? "#ff5252"
            : value === "offer"
            ? "#35ff35"
            : value === "pending"
            ? "rgb(255, 210, 31)"
            : value === "interview"
            ? "#6c6cf1"
            : "white";

        const innerElement = $("<div></div>")
            .text(value.charAt(0).toUpperCase() + value.slice(1))
            .css({
            "background-color": statusColor,
            color: "white",
            padding: "0.7rem 1.2rem",
            "border-radius": "0.8rem",
            display: "block",
            "text-align": "center",
            });

        valueElement.append(innerElement);
        }

        $(".application-grid").append(valueElement);
    });
    });
}

/*
    const debug = false;

    $(document).ready(function() {
        if (debug === true) {
            //Refresh the application grid for any changes to the application collection.
            refreshApplicationGrid(exampleData);
        }
    });

    $('.new-btn').click(function() {
        $(this).hide();
        $('.new-input-wrapper').slideDown();
    });

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
            'user_email': userEmailElement.text(),
            'company': company,
            'role': role,
            'date': date,
            'company_email': email,
            'status': status
        };

        //Send the POST request to manually add a new application.
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
    });
    */
