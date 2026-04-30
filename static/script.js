const chatWindow = document.getElementById('chat-window');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // Hiển thị tin nhắn user
    appendMessage(message, 'user-msg');
    userInput.value = '';

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        const data = await response.json();

        // Hiển thị phản hồi từ Bot
        appendMessage(data.reply.replace(/\n/g, '<br>'), 'bot-msg', true);

        if (data.images && data.images.length > 0) {
            data.images.forEach(imgUrl => {
                const img = document.createElement('img');
                img.src = imgUrl;
                chatWindow.appendChild(img);
            });
        }
        chatWindow.scrollTop = chatWindow.scrollHeight;
    } catch (e) {
        appendMessage("Lỗi kết nối server rồi!", 'bot-msg');
    }
}

function appendMessage(text, className, isHTML = false) {
    const div = document.createElement('div');
    div.className = `message ${className}`;
    if (isHTML) div.innerHTML = text; else div.textContent = text;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

sendBtn.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});