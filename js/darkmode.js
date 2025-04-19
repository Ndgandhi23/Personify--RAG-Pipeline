// Function that changes the background color and text color
function setBackgroundColor(color) {
    $('body').css('background-color', color);
    setTextColor(color); // Update text color for specific elements
}

// Hashmap of background color -> text color
const colorTextMap = {
    'black': 'white',
    'bg-gray-100': 'black',
};

// Function to set text color for specific elements
function setTextColor(backgroundColor) {
    const textColor = colorTextMap[backgroundColor];

    // Update text color for h2 headers in each section
    $('#faqSection h2, #contactSection h2, #profileSection h2, #settingsSection h2').css('color', textColor);

    // Update text color for FAQ questions and answers
    $('.faq-question').css('color', textColor);
    $('.faq-answer').css('color', textColor);

    //Update the text color for the view jobs section
    $('.view-jobs p, .view-jobs span, .view-jobs div').css('color', textColor);
}

// Apply the background color from localStorage on page load
$(document).ready(function () {
    const savedColor = localStorage.getItem("color") || 'bg-gray-100';
    setBackgroundColor(savedColor);

    // Check if the dark mode button exists
    const darkModeButton = $('[data-setting="darkMode"]');
    if (darkModeButton.length === 0) {
        console.warn('⚠️ Dark mode button not found.');
        return;
    }

    // Set the button text based on the saved color
    darkModeButton.text(savedColor === 'black' ? 'On' : 'Off');

    // Add event listener to the dark mode button
    darkModeButton.click(function () {
        // Update the button text immediately
        const isDarkMode = $(this).text().trim() === 'On';
        console.log(isDarkMode);
        // Toggle the background color
        const newColor = isDarkMode ? 'black' : 'bg-gray-100'; // Toggle between light and dark
        setBackgroundColor(newColor); // Apply the background color immediately
        localStorage.setItem("color", newColor); // Save the selected color to localStorage
    });
});