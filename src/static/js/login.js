function fillCredentials(email) {
    const usernameInput = document.getElementById('id_username');
    const passwordInput = document.getElementById('id_password');
    
    if (usernameInput && passwordInput) {
        usernameInput.value = email;
        passwordInput.value = 'password123';
    }
}