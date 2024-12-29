document.addEventListener('DOMContentLoaded', () => {
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const getOtpButton = document.getElementById('getOtp');
    const otpGroup = document.getElementById('otp-group');
    const otpInput = document.getElementById('otp');
    const submitOtpButton = document.getElementById('submitOtp');
    const messageDiv = document.getElementById('message');

    getOtpButton.addEventListener('click', async () => {
        const username = usernameInput.value;
        const email = emailInput.value;

        if (!username || !email) {
            displayMessage("Please enter both username and email.");
            return;
        }

        if (!isValidEmail(email)) {
            displayMessage("Please enter a valid email.");
            return;
        }

        usernameInput.disabled = true;
        emailInput.disabled = true;
        getOtpButton.disabled = true;

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
                getOtpButton.style.display = 'none'; // Hide the button
                displayMessage(data.message);
            } else if (response.status === 401) {
                displayMessage(data.message);
                enableInputs();
            } else if (response.status === 400) {
                displayMessage(data.message);
                enableInputs();
            } else {
                displayMessage("An error occurred.");
                enableInputs();
            }
        } catch (error) {
            console.error("Error:", error);
            displayMessage("An error occurred.");
            enableInputs();
        }
    });

    // submitOtpButton.addEventListener('click', async () => {
    //     const username = usernameInput.value;
    //     const email = emailInput.value;
    //     const otp = otpInput.value;

    //     if (!otp || otp.length != 6) {
    //         displayMessage("Please enter a valid 6-digit OTP.");
    //         return;
    //     }

    //     try {
    //         const response = await fetch('/api/auth/validate-otp', {
    //             method: 'POST',
    //             headers: { 'Content-Type': 'application/json' },
    //             body: JSON.stringify({ username, email, otp }),
    //         });

    //         if (response.status === 200) {
    //             window.location.href = '/profile';
    //         } else if (response.status === 401) {
    //             const data = await response.json();
    //             displayMessage(data.message);
    //         } else {
    //             displayMessage("An error occurred.");
    //         }
    //     } catch (error) {
    //         console.error("Error:", error);
    //         displayMessage("An error occurred.");
    //     }
    // });

    submitOtpButton.addEventListener('click', async () => {
        const username = usernameInput.value;
        const email = emailInput.value;
        const otp = otpInput.value;
    
        if (!otp || otp.length != 6) {
            displayMessage("Please enter a valid 6-digit OTP.");
            return;
        }
    
        try {
            const response = await fetch('/api/auth/validate-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, otp }),
            });
    
            if (response.status === 200) {
                const data = await response.json();
                
                if (data.status === "success" && data.data.length > 0) {
                    const { access_token, user_id, username, email, request_id } = data.data[0];
    
                    // Set cookies
                    document.cookie = `access_token=${access_token}; path=/;`;
                    document.cookie = `user_id=${user_id}; path=/;`;
                    document.cookie = `username=${username}; path=/;`;
                    document.cookie = `email=${email}; path=/;`;
                    document.cookie = `request_id=${request_id}; path=/;`;
    
                    // Redirect to profile page
                    window.location.href = '/profile';
                } else {
                    displayMessage("Unexpected response data.");
                }
            } else if (response.status === 401) {
                const data = await response.json();
                displayMessage(data.message);
            } else {
                displayMessage("An error occurred.");
            }
        } catch (error) {
            console.error("Error:", error);
            displayMessage("An error occurred.");
        }
    });
    


    function displayMessage(msg) {
        messageDiv.textContent = msg;
    }

    function enableInputs() {
        usernameInput.disabled = false;
        emailInput.disabled = false;
        getOtpButton.style.display = 'block'; // Show button again
        getOtpButton.disabled = false;
    }

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
});
