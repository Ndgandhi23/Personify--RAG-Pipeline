//Redirect to home and personalize pages.
const redirectToHome = (email) => {
  // Encode email to safely pass in URL
  const encodedEmail = encodeURIComponent(email);
  window.location.href = `/newhome.html?email=${encodedEmail}`;
};

//Search engine functionality
$(document).ready(function () {
  // Check to see if email is present in URL (Otherwise, redirect them to login page.)
  const urlParams = new URLSearchParams(window.location.search);
  const userEmail = urlParams.get("email");
  //Validate user email to see if valid and currently logged in state.
  if (!userEmail && localStorage.get("email") !== userEmail) {
    window.location.href = "/login.html"; // Redirect to login page if email is not present
  }

  // When we click on the element with class new-titl, call the redirectToHome function.
  $(".new-titl").click(function () {
    const email = userEmail; // Use the email extracted from the URL
    redirectToHome(email);
  });

  // Ensure the search overlay is hidden initially.
  $("#searchOverlay").hide();

  // Application rendering logic
  // Load the applications from the user's last search
  // Make an api request to get the user's last search
  $.ajax({
    url: "http://127.0.0.1:8000/last-search",
    type: "POST",
    data: JSON.stringify({email: userEmail}),
    contentType: "application/json",
    dataType: "json",
    success: function (response) {
      // Pass that into filter applications 
      // Make an API request to /filter (POST), passing in the search term (response.content or wtvr)
      const payload = response;
      console.log("Payload content:", JSON.stringify(payload));
      $.ajax({
        url: "http://127.0.0.1:8000/filter",
        type: "POST",
        data: JSON.stringify(payload),
        contentType: "application/json",
        dataType: "json",
        success: function (filterResponse) {
          // If successful, refresh the application grid.
          refreshApplicationGrid(filterResponse["applications"]);
        },
        error: function (xhr, status, error) {
          console.error("Error:", status, error);
          alert("Failed to filter applications based on last search. Please try again.");
        },
      });
    },
    error: function (xhr, status, error) {
      console.error("Error:", status, error);
      alert("Failed to load last search results. Please try again.");
    },
  });

  // When the search button is clicked, show the inline overlay.
  $("#searchButton").on("click", function (e) {
    anyField =
      $(".date-field").length > 0 ||
      $(".company-field").length > 0 ||
      $(".email-field").length > 0 ||
      $(".status-field").length > 0;
    role = $(".search-engine-input").val();
    console.log(role);
    if (role || anyField) {
      //Filter out the applications
      //Get the entered fields and prepare it in the request's payload
      const payload = {};
      if ($(".date-field").length > 0) {
        const dateCondition = $(".date-field select").val(); // Get the selected condition (e.g., "greater", "equal", "less")
        const dateValue = $(".date-field input[type='date']").val(); // Get the entered date value
        payload["date_cond"] = { condition: dateCondition, value: dateValue };
      }
      if ($(".company-field").length > 0) {
        payload["company"] = $(".company-field input").val();
      }
      if ($(".email-field").length > 0) {
        payload["company_email"] = $(".email-field input").val();
      }
      if ($(".status-field").length > 0) {
        payload["status"] = $(".status-field select").val();
      }
      if (role != "") {
        payload["role"] = role;
      }

      //Make a POST request to the /filter endpoint
      $.ajax({
        url: "http://127.0.0.1:8000/filter",
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
        },
      });
    } else {
      e.stopPropagation(); // Prevent event bubbling.
      $("#searchOverlay").fadeIn(200); // Show the overlay with a fade-in effect.
    }
  });

  // Functionality for open button to open the filter window.
  $(document).ready(function () {
    // Functionality for open button to open the search window.
    $(".open-button").on("click", function (e) {
      e.stopPropagation(); // Prevent event bubbling.
      if (!$("#searchOverlay").is(":visible")) {
        $("#searchOverlay").fadeIn(200); // Show the overlay with a fade-in effect.
      } else {
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
      if (
        !$(e.target).closest("#searchOverlay, #searchButton, #searchButton *")
          .length
      ) {
        $("#searchOverlay").fadeOut(200);
      }
    });
  });
});

//Set up event functionality when clicking on search results
$(".search-results")
  .children()
  .each(function () {
    $(this).on("click", function () {
      //Set input in search engine to result text
      $(".search-engine-input").val($(this).text().trim());
      //Search Engine overlay closes
      $("#searchOverlay").fadeOut(200);
    });
  });

//Set up functionality when clicking on filter checkboxes.
$(document).ready(function () {
  // Listen for changes on the filter checkboxes.
  $("#filterForm input[type='checkbox']").on("change", function () {
    var value = $(this).val(); // e.g., "Date", "Company", "Email", "Status"

    if ($(this).is(":checked")) {
      // Checkbox is checked—add the corresponding field
      if (value === "Date") {
        $(this)
          .closest("label")
          .after(
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
      } else if (value === "Company") {
        $(this)
          .closest("label")
          .after(
            `<div class="filter-field company-field mt-2">
                <label class="block text-gray-700 mb-1">Enter Company</label>
                <input type="text" class="w-full border border-gray-300 rounded p-2" placeholder="Company Name">
             </div>`
          );
      } else if (value === "Email") {
        $(this)
          .closest("label")
          .after(
            `<div class="filter-field email-field mt-2">
                <label class="block text-gray-700 mb-1">Enter Company Email</label>
                <input type="email" class="w-full border border-gray-300 rounded p-2" placeholder="Email">
             </div>`
          );
      } else if (value === "Status") {
        $(this)
          .closest("label")
          .after(
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
      if (value === "Date") {
        $(this).closest("label").next(".date-field").remove();
      } else if (value === "Company") {
        $(this).closest("label").next(".company-field").remove();
      } else if (value === "Email") {
        $(this).closest("label").next(".email-field").remove();
      } else if (value === "Status") {
        $(this).closest("label").next(".status-field").remove();
      }
    }
  });
});

function refreshApplicationGrid(data) {
  console.log(data);
  if (data.length === 1){
  $(".jobs-head").text(`Viewing ${data.length} application`);
  } else{
    $(".jobs-head").text(`Viewing ${data.length} applications`);
  }

  // Clear the applications from the grid.
  $(".application-grid .apps").empty();

  data.forEach((application, index) => {
    // Create a new application element with class company-role
    const applicationElement = $("<div></div>")
      .addClass(`${application.company} - ${application.role}`);

    // Switch the background color every application.
    const backgroundColor = index % 2 === 0 ? "#efefef" : "white";
    applicationElement.css({
      "background-color": backgroundColor,
      "margin-bottom": "10px",
      "border-radius": "5px",
      "box-shadow": "0 2px 4px rgba(0, 0, 0, 0.1)",
      "display": "flex"
    });

    //For each value
    Object.entries(application).forEach(([key, value]) => {
      // If key is id, then just move on
      if (key === "_id" || key === "user_email") {
        return;
      }
      const valueElement = $(`<div class = ${key}></div>`).text(value).css({
      padding: "8px",
      });

      // Special handling for status column (key === "status")
      if (key === "status") {
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

      // Add the value element to the application element
      applicationElement.append(valueElement);
    });
    // Append the application element to the application grid
    $(".application-grid").append(applicationElement);
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
  });
    */
