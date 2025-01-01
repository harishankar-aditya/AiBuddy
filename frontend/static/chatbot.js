const chatMessages = document.getElementById('chatMessages');
const scrollButton = document.getElementById('scrollButton');
const placeholder = document.getElementById('placeholder');
const userID = generateUUID();
const threadID = generateUUID();
const sendButton = document.getElementById('sendButton');
const loader = document.getElementById('loader');

document.getElementById('sessionTime').textContent = `Session started: ${new Date().toLocaleString()}`;

function toggleSidebar() {
    document.getElementById('container').classList.toggle('collapsed');
}

function checkEnter(event) {
    if (event.key === 'Enter') sendMessage();
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    if (input.value.trim() === '') return;

    const userMessage = input.value;
    addMessage('user', userMessage);
    input.value = '';
    placeholder.style.display = 'none';

    loader.style.display = 'block';
    sendButton.disabled = true;

    try {
        const response = await fetch('/api/pulse-buddy/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: userMessage,
                user_id: userID,
                thread_id: threadID
            })
        });

        if (response.ok && response.body) {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let botMessage = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                botMessage += chunk;
                updateBotMessage(botMessage); // Update message incrementally
            }

            finalizeBotMessage(botMessage); // Ensure the full message is handled
        } else {
            addMessage('bot', 'Error: Unable to process your request.');
        }
    } catch (error) {
        addMessage('bot', 'Error: Network issue or API unavailable.');
    } finally {
        loader.style.display = 'none';
        sendButton.disabled = false;
    }
}

function updateBotMessage(partialMessage) {
    let lastBotBubble = chatMessages.querySelector('.message-bubble.bot:last-child');
    if (!lastBotBubble) {
        lastBotBubble = document.createElement('div');
        lastBotBubble.className = 'message-bubble bot';
        chatMessages.appendChild(lastBotBubble);
    }
    lastBotBubble.innerHTML = marked.parse(partialMessage);
    autoScrollIfAtLatest();
}

function finalizeBotMessage(fullMessage) {
    updateBotMessage(fullMessage); // Ensure the last update is rendered
}

function addMessage(type, message) {
    const messageBubble = document.createElement('div');
    messageBubble.className = `message-bubble ${type}`;
    messageBubble.innerHTML = type === 'bot' ? marked.parse(message) : message;

    const timestamp = document.createElement('span');
    timestamp.className = 'timestamp';
    timestamp.textContent = new Date().toLocaleTimeString();
    messageBubble.appendChild(timestamp);

    chatMessages.appendChild(messageBubble);
    autoScrollIfAtLatest();
}

function autoScrollIfAtLatest() {
    const isAtBottom = chatMessages.scrollTop + chatMessages.clientHeight >= chatMessages.scrollHeight - 1;
    if (isAtBottom) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

function scrollToLatest() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

async function handleLogout() {
    try {
        // Send POST request to the /logout endpoint
        const response = await fetch('/logout', { // Replace with your logout URL
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        // Check for successful response
        if (!response.ok) {
            throw new Error('Network response was not ok.');
        }

        // Redirect to /home
        window.location.href = '/home';
    } catch (error) {
        console.error('Logout Error:', error);
        alert('Logout failed. Please try again.');
    }
}

async function homeRoute() {
    try {
        // Send POST request to the /logout endpoint
        const response = await fetch('/home', { // Replace with your logout URL
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        // Check for successful response
        if (!response.ok) {
            throw new Error('Network response was not ok.');
        }

        // Redirect to /home
        window.location.href = '/home';
    } catch (error) {
        console.error('Logout Error:', error);
        alert('Logout failed. Please try again.');
    }
}