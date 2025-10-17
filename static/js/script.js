document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");
    const sendBtn = document.getElementById("send-btn");

    // Add the initial bot message
    addMessage("Hello! I am a Gemini-powered AI. What can I help you create or discover today?", "bot-message");

    // Function to render markdown-like formatting
    function renderMarkdown(text) {
        text = text.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
        text = text.replace(/\*(.*?)\*/g, '<i>$1</i>');
        text = text.replace(/(\/\static\/image_\d+\.png|\/\static\/qrcode_\d+\.png)/g, '<img src="$1" alt="Generated Image" class="img-fluid my-2 rounded">');
        text = text.replace(/\n/g, '<br>');
        return text;
    }

    // Function to add a message to the chatbox
    function addMessage(text, className) {
        const messageDiv = document.createElement("div");
        messageDiv.className = `message ${className}`;
        
        const messageP = document.createElement("p");
        messageP.innerHTML = renderMarkdown(text);
        
        messageDiv.appendChild(messageP);
        chatBox.appendChild(messageDiv);
        
        chatBox.scrollTop = chatBox.scrollHeight;
        return messageDiv;
    }

    // Function to show/hide the typing indicator
    let typingIndicator;
    function showTypingIndicator() {
        if (typingIndicator) return;
        typingIndicator = document.createElement("div");
        typingIndicator.className = "message bot-message";
        typingIndicator.innerHTML = `
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        `;
        chatBox.appendChild(typingIndicator);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function hideTypingIndicator() {
        if (typingIndicator) {
            typingIndicator.remove();
            typingIndicator = null;
        }
    }

    // Handle form submission
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        userInput.value = "";
        userInput.disabled = true;
        sendBtn.disabled = true;
        addMessage(message, "user-message");
        showTypingIndicator();

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: message }),
            });

            if (!response.ok) throw new Error("Network response was not ok");
            
            const data = await response.json();
            hideTypingIndicator();
            addMessage(data.response, "bot-message");

        } catch (error) {
            console.error("Error:", error);
            hideTypingIndicator();
            addMessage("Oops! Something went wrong. Please check the console.", "bot-message");
        } finally {
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
        }
    });
});