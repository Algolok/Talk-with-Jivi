const API_URL = "http://127.0.0.1:5000/chat";

async function sendMessage() {
    const inputField = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");
    const userMessage = inputField.value.trim();

    if (userMessage === "") return;

    // Append User Message (Right-Aligned Blue Bubble)
    chatBox.innerHTML += `
        <div class="flex justify-end">
            <div class="bg-blue-500 text-white p-3 rounded-lg max-w-xs">
                ${userMessage}
            </div>
        </div>
    `;

    // Clear Input Field
    inputField.value = "";

    // Append Bot Response Placeholder (Full-Width Gray Bubble)
    const botMessageContainer = document.createElement("div");
    botMessageContainer.className = "flex justify-start w-full"; // Full width
    const botMessageBubble = document.createElement("div");
    botMessageBubble.className = "bg-gray-700 text-white p-3 rounded-lg w-full"; // Full width
    botMessageContainer.appendChild(botMessageBubble);
    chatBox.appendChild(botMessageContainer);

    // Stream Response from API
    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userMessage })
        });

        if (!response.body) {
            botMessageBubble.innerHTML = "Error: No response from server.";
            return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let botMessage = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            botMessage += decoder.decode(value);
            botMessageBubble.innerHTML = botMessage.replace(/\n/g, "<br>");
        }

    } catch (error) {
        botMessageBubble.innerHTML = "Error: Server Issue";
    }

    // Auto-scroll
    chatBox.scrollTop = chatBox.scrollHeight;
}
