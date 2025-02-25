const isValidEmail = (email) => {
    const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.(com)$/;
    return emailRegex.test(email);
}

const isValidUsername = (user_name) => {
    if (user_name.endsWith('.com')){
        isValidEmail(user_name) //Username = Email Address
    }
    const uNameRegex = /^(?!.*[-_'.@]{2})[a-zA-Z0-9][-_'\.@a-zA-Z0-9]*[a-zA-Z0-9]$/;
    return uNameRegex.test(user_name);
}

const isValidPassword = (password) => {
    const passwordRegex = /^(?=.*[!@#?])(?!.*[!@#?]{2})[a-zA-Z0-9!@#?]{8,}$/;
    return passwordRegex.test(password);
}

console.log(isValidPassword("Pass123.."))

