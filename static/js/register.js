
document.getElementById('registerForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const email = e.target.email.value.trim();
    const password = e.target.password.value;
    const confirmPassword = e.target.confirmPassword.value;
    const messageDiv = document.getElementById('message');

    messageDiv.textContent = '';

    // Client-side validation
    if (!email.match(/^\S+@\S+\.\S+$/)) {
        messageDiv.textContent = 'Invalid email format.';
        return;
    }
    if (password.length < 6) {
        messageDiv.textContent = 'Password must be at least 6 characters.';
        return;
    }
    if (password !== confirmPassword) {
        messageDiv.textContent = 'Passwords do not match.';
        return;
    }

    try {
        const response = await fetch('/users/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: email, email: email, password: password})
        });
        if (response.ok) {
            messageDiv.textContent = 'Registration successful!';
            e.target.reset();
        } else {
            const data = await response.json();
            messageDiv.textContent = data.detail || 'Registration failed.';
        }
    } catch (error) {
        messageDiv.textContent = 'Error connecting to server.';
    }
});
