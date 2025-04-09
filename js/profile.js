//Profile modal function for opening up profile modal
// Displaying profile modal when clicking on the profile pic.
const profilePic = $(".profile-pic");
const profileModal = $("<div></div>")
    .html(
    `
        <article class="flex flex-col bg-white h-fit w-[230px]">
            <header class="flex flex-col">
                <h2 class="name w-full text-lg font-medium text-center text-green-900 h-[23px]">
                    Name
                </h2>
                <p class="email w-full text-base text-center h-[31px] text-green-950">Email</p>
            </header>

            <nav class="flex flex-col gap-3 justify-center items-center w-full">
                <button
                    class="flex relative justify-center items-center bg-red-500 h-[40px] w-full"
                    aria-label="View Profile"
                >
                    <div class="absolute top-0 h-4 bg-red-500 w-[90px]"></div>
                    <span class="relative text-lg text-white z-[1]">Profile</span>
                </button>

                <button
                    class="flex relative justify-center items-center bg-red-500 h-[40px] w-full"
                    aria-label="Open Settings"
                >
                    <div class="absolute top-0 h-4 bg-red-500 w-[90px]"></div>
                    <span class="relative text-lg text-center text-white z-[1]">Settings</span>
                </button>

                <button
                    class="flex relative justify-center items-center bg-red-500 h-[40px] w-full"
                    aria-label="FAQ"
                >
                    <div class="absolute top-0 h-4 bg-red-500 w-[90px]"></div>
                    <span class="relative text-lg text-white z-[1]">FAQ</span>
                </button>

                <button
                    class="flex relative justify-center items-center bg-red-500 h-[40px] w-full"
                    aria-label="Contact us for any issues"
                >
                    <div class="absolute top-0 h-4 bg-red-500 w-[90px]"></div>
                    <span class="relative text-lg text-white z-[1]">Contact</span>
                </button>

                <button
                    class="logout-button flex relative justify-center items-center bg-red-500 h-[40px] w-full"
                    aria-label="Logout from account"
                >
                    <div class="absolute top-0 h-4 bg-red-500 w-[90px]"></div>
                    <span class="relative text-lg text-white z-[1]">Logout</span>
                </button>
            </nav>
        </article>
    `
    )
    .css({
    position: "absolute",
    top: "16%",
    right: "0.1%",
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

        //Set routing for the other four buttons 

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

//Event listener for clicking outside the profile modal
$(document).click(function (event) {
    if (
    !profileModal.is(event.target) &&
    !$.contains(profileModal[0], event.target) &&
    event.target !== profilePic[0]
    ) {
    profileModal.hide();
    }
});