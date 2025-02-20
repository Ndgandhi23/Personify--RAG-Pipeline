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