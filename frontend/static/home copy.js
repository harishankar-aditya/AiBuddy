document.addEventListener('DOMContentLoaded', () => {
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const getOtpButton = document.getElementById('getOtp');
    const otpGroup = document.getElementById('otp-group');
    const otpInput = document.getElementById('otp');
    const submitOtpButton = document.getElementById('submitOtp');
    const loaderOtp = document.getElementById('loaderOtp');
    const messageErrorDiv = document.getElementById('error-message');
    const messageSuccessDiv = document.getElementById('success-message');

    function getCredentialsFromCookies() {
        const credentials = { username: '', email: '' };
        const allCookies = document.cookie.split(';');

        for (const cookie of allCookies) {
            const [key, value] = cookie.trim().split('=');
            if (key === 'username') {
                credentials.username = decodeURIComponent(value);
            } else if (key === 'email') {
                credentials.email = decodeURIComponent(value);
            }
        }
        return credentials;
    }

    // Populate username and email from cookies if available
    const { username, email } = getCredentialsFromCookies();
    if (username) usernameInput.value = username;
    if (email) emailInput.value = email;

    getOtpButton.addEventListener('click', async () => {
        const username = usernameInput.value;
        const email = emailInput.value;

        if (!username || !email) {
            displayErrorMessage("Please enter both username and email.");
            return;
        }

        if (!isValidEmail(email)) {
            displayErrorMessage("Please enter a valid email.");
            return;
        }

        usernameInput.disabled = true;
        emailInput.disabled = true;
        getOtpButton.disabled = true;
        loaderOtp.style.display = 'block'; // Show loader

        try {
            const response = await fetch('/api/auth/send-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email }),
            });

            const data = await response.json();
            if (response.status === 200) {
                otpGroup.style.display = 'flex';
                submitOtpButton.style.display = 'block';
                getOtpButton.style.display = 'none';
                displaySuccessMessage(data.message);
            } else {
                displayErrorMessage(data.detail.message);
                enableInputs();
            }
        } catch (error) {
            console.error("Error:", error);
            displayErrorMessage("An error occurred.");
            enableInputs();
        } finally {
            loaderOtp.style.display = 'none'; // Hide loader
        }
    });

    submitOtpButton.addEventListener('click', async () => {
        const otp = otpInput.value;
        const username = usernameInput.value;
        const email = emailInput.value;

        if (!otp || otp.length !== 6) {
            displayErrorMessage("Please enter a valid 6-digit OTP.");
            return;
        }

        try {
            const response = await fetch('/api/auth/validate-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, otp }), // Include username and email here
            });

            const data = await response.json();
            if (response.status === 200) {
                if (data.status === "success" && data.data.length > 0) {
                    const { access_token, user_id, username, email, request_id } = data.data[0];

                    // Set cookies
                    document.cookie = `access_token=${encodeURIComponent(access_token)}; path=/;`;
                    document.cookie = `user_id=${encodeURIComponent(user_id)}; path=/;`;
                    document.cookie = `username=${encodeURIComponent(username)}; path=/;`;
                    document.cookie = `email=${encodeURIComponent(email)}; path=/;`;
                    document.cookie = `request_id=${encodeURIComponent(request_id)}; path=/;`;

                    // Redirect to profile page
                    window.location.href = '/profile';
                } else {
                    displayErrorMessage("Unexpected response data.");
                }
            } else {
                displayErrorMessage(data.detail.message);
            }
        } catch (error) {
            console.error("Error:", error);
            displayErrorMessage("An error occurred.");
        }
    });

    // function displayMessage(msg) {
    //     messageDiv.textContent = msg;
    // }
    function displayErrorMessage(msg) {
        messageErrorDiv.textContent = msg;
    }
    function displaySuccessMessage(msg) {
        messageSuccessDiv.textContent = msg;
    }

    function enableInputs() {
        usernameInput.disabled = false;
        emailInput.disabled = false;
        getOtpButton.style.display = 'block';
        getOtpButton.disabled = false;
    }

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
});
