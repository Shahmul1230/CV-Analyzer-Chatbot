const API_URL = "http://localhost:8000/chat";


const chatToggle = document.getElementById("chatToggle");
const chatPanel = document.getElementById("chatPanel");
const closeChat = document.getElementById("closeChat");
const chatBody = document.getElementById("chatBody");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

const SESSION_KEY = "cv_assistant_session_id";

const fileInput = document.getElementById("fileInput");
let selectedFileName = "";
fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) {
    selectedFileName = fileInput.files[0].name;

    addMessage(
      `CV uploaded: ${selectedFileName}\nPlease click send to analyze your CV.`,
      "bot"
    );
  }
});

let sessionId = localStorage.getItem(SESSION_KEY);

if (!sessionId) {
  sessionId = crypto.randomUUID();
  localStorage.setItem(SESSION_KEY, sessionId);
}

chatToggle.addEventListener("click", () => {
  chatPanel.style.display = "flex";
  chatToggle.style.display = "none";
});

closeChat.addEventListener("click", () => {
  chatPanel.style.display = "none";
  chatToggle.style.display = "block";
});

sendBtn.addEventListener("click", sendMessage);

userInput.addEventListener("input", () => {
  userInput.style.height = "auto";
  userInput.style.height = `${userInput.scrollHeight}px`;
});

userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => {
    const prompt = button.getAttribute("data-prompt");
    userInput.value = prompt;
    sendMessage();
  });
});

async function sendMessage() {
  let message = userInput.value.trim();

  const hasFile = fileInput.files.length > 0;

  if (!message && !hasFile) return;

  if (!message && hasFile) {
    message = "Please analyze this CV and provide professional ATS-focused feedback.";
  }

  if (hasFile) {
    addMessage(
      `I have uploaded my CV: ${fileInput.files[0].name}\nPlease analyze it professionally.`,
      "user"
    );
  } else {
    addMessage(message, "user");
  }

  userInput.value = "";
  userInput.style.height = "auto";

  setLoading(true);
  const typingElement = showTyping();

  try {
    let response;

    if (hasFile) {
      const formData = new FormData();

      formData.append("message", message);
      formData.append("session_id", sessionId);
      formData.append("file", fileInput.files[0]);

      response = await fetch("http://localhost:8000/chat-with-file", {
        method: "POST",
        body: formData
      });

      fileInput.value = "";
      selectedFileName = "";
    } else {
      response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          message,
          session_id: sessionId
        })
      });
    }

    const data = await response.json();

    typingElement.remove();

    if (!response.ok) {
      addMessage(data.answer || "Something went wrong. Please try again.", "bot");
      return;
    }

    addMessage(data.answer, "bot");
  } catch (error) {
    typingElement.remove();

    addMessage(
      "Sorry, I could not connect to the chatbot server. Please make sure the backend is running.",
      "bot"
    );
  } finally {
    setLoading(false);
  }
}

function addMessage(text, sender) {
  const messageDiv = document.createElement("div");

  messageDiv.className =
    sender === "user" ? "message user-message" : "message bot-message";

  if (sender === "bot") {
    messageDiv.innerHTML = formatBotResponse(text);
  } else {
    messageDiv.textContent = text;
  }

  chatBody.appendChild(messageDiv);
  scrollToBottom();
}

function formatBotResponse(text) {
  let safeText = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  safeText = safeText
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/\*(.*?)\*/g, "$1")
    .replace(/^\s*\*\s+/gm, "• ")
    .replace(/^\s*-\s+/gm, "• ")
    .replace(/###|##|#/g, "");

  safeText = safeText
    .replace(/\n{3,}/g, "\n\n")
    .replace(/\n/g, "<br>")
    .replace(/(\d+)\.\s/g, "<br><strong>$1.</strong> ");

  return safeText;
}

function showTyping() {
  const typingDiv = document.createElement("div");

  typingDiv.className = "message bot-message typing";

  typingDiv.innerHTML = `
    <span></span>
    <span></span>
    <span></span>
  `;

  chatBody.appendChild(typingDiv);

  scrollToBottom();

  return typingDiv;
}

function setLoading(isLoading) {
  sendBtn.disabled = isLoading;
  userInput.disabled = isLoading;
}

function scrollToBottom() {
  chatBody.scrollTop = chatBody.scrollHeight;
}