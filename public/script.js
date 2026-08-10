const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatHistory = document.getElementById('chat-history');
const newChatBtn = document.querySelector('.new-chat-btn');

// Parse Discord Emojis into Images
function parseDiscordEmojis(text) {
    // Regex matches <:name:id> or <a:name:id>
    const emojiRegex = /<a?:([^:]+):(\d+)>/g;
    return text.replace(emojiRegex, (match, name, id) => {
        const isAnimated = match.startsWith('<a:');
        const ext = isAnimated ? 'gif' : 'png';
        return `<img class="dank-emoji" src="https://cdn.discordapp.com/emojis/${id}.${ext}" alt="${name}" title="${name}">`;
    });
}

function appendMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', role);

    const avatar = document.createElement('div');
    avatar.classList.add('avatar');
    avatar.textContent = role === 'user' ? 'U' : '🐸';

    const bubble = document.createElement('div');
    bubble.classList.add('bubble');
    
    if (role === 'assistant') {
        // Parse markdown and emojis
        const html = marked.parse(content);
        bubble.innerHTML = parseDiscordEmojis(html);
    } else {
        bubble.textContent = content;
    }

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(bubble);
    chatHistory.appendChild(messageDiv);

    // Scroll to bottom
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function appendTypingIndicator() {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', 'assistant');
    messageDiv.id = 'typing-indicator-msg';

    const avatar = document.createElement('div');
    avatar.classList.add('avatar');
    avatar.textContent = '🐸';

    const bubble = document.createElement('div');
    bubble.classList.add('bubble');
    bubble.innerHTML = `
        <div class="typing-indicator">
            <span></span><span></span><span></span>
        </div>
    `;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(bubble);
    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator-msg');
    if (indicator) {
        indicator.remove();
    }
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = userInput.value.trim();
    if (!text) return;

    // Display User Message
    appendMessage('user', text);
    userInput.value = '';

    // Show typing...
    appendTypingIndicator();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: text })
        });

        const data = await response.json();
        removeTypingIndicator();
        
        if (response.ok) {
            appendMessage('assistant', data.response);
        } else {
            appendMessage('assistant', `**Error:** ${data.detail || 'Something went wrong.'}`);
        }
    } catch (err) {
        removeTypingIndicator();
        appendMessage('assistant', '**Error:** Could not connect to the server.');
    }
});

newChatBtn.addEventListener('click', () => {
    chatHistory.innerHTML = `
        <div class="message assistant">
            <div class="avatar">🐸</div>
            <div class="bubble">
                Welcome to DankGPT! I have read every official guide, API, and over 150,000 community Discord messages. How can I help you dominate Dank Memer today?
            </div>
        </div>
    `;
});
