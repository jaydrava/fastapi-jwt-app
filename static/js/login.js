document.getElementById('loginForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const email = e.target.email.value.trim();
    const password = e.target.password.value;
    const messageDiv = document.getElementById('message');

    messageDiv.textContent = '';

    if (!email || !password) {
        messageDiv.textContent = 'Please fill all fields.';
        return;
    }

    try {
        const response = await fetch('/users/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: email, password: password})
        });
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            messageDiv.textContent = 'Login successful!';
            e.target.reset();
        } else if (response.status === 401) {
            messageDiv.textContent = 'Invalid credentials.';
        } else {
            messageDiv.textContent = 'Login failed.';
        }
    } catch (error) {
        messageDiv.textContent = 'Error connecting to server.';
    }
});
