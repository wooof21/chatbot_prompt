const chatButton = document.getElementById("chat-button");
const chatWindow = document.getElementById("chat-window");
const messagesDiv = document.getElementById("messages");
const input = document.getElementById("chat-input");
const sendButton = document.getElementById("send-button");

const API_BASE = "http://localhost:8000";

let sessionId = localStorage.getItem("chat_session_id");
if (!sessionId) {
  sessionId = crypto.randomUUID();
  localStorage.setItem("chat_session_id", sessionId);
}

let conversation = JSON.parse(localStorage.getItem("chat_messages") || "[]");

function saveConversation() {
  localStorage.setItem("chat_messages", JSON.stringify(conversation));
}

function addMessage(text, sender, save = true) {
  const div = document.createElement("div");
  div.className = `message ${sender}`;
  div.textContent = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;

  if (save) {
    conversation.push({
      role: sender === "user" ? "user" : "assistant",
      content: text,
    });
    localStorage.setItem("chat_messages", JSON.stringify(conversation));
  }
}

function renderExistingMessages() {
  messagesDiv.innerHTML = "";
  for (const msg of conversation) {
    addMessage(msg.content, msg.role === "user" ? "user" : "bot", false);
  }
}

chatButton.addEventListener("click", async () => {
  chatWindow.classList.toggle("hidden");

  if (!chatWindow.classList.contains("hidden")) {
    renderExistingMessages();
  }

  if (!chatWindow.dataset.greeted) {
    const res = await fetch(`${API_BASE}/api/greeting`);
    const data = await res.json();

    addMessage(data.message, "bot");

    chatWindow.dataset.greeted = "true";
  }
});

async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";

  console.log("Sending request:", {
    session_id: sessionId,
    messages: conversation,
  });

  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: sessionId,
      messages: conversation,
    }),
  });

  if (!res.ok) {
    const errorText = await res.text();
    console.error("Chat API error:", errorText);
    addMessage(`Error: ${errorText}`, "bot");
    return;
  }

  const data = await res.json();
  addMessage(data.reply, "bot");
}

sendButton.addEventListener("click", sendMessage);

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});