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
    
    // Functionality for open button to open the filter window.
    $(document).ready(function () {
        // Functionality for open button to open the search window.
        $(".open-button").on("click", function (e) {
            e.stopPropagation(); // Prevent event bubbling.
            if (!$("#searchOverlay").is(":visible")){
                $("#searchOverlay").fadeIn(200); // Show the overlay with a fade-in effect.
            }else{
                $("#searchOverlay").fadeOut(200); // Show the overlay with a fade-in effect.
            }
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
