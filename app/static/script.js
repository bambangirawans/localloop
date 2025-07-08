const chatBox = document.getElementById("chat-box");
const inputField = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");
const voiceButton = document.getElementById("voice-button");
const loader = document.getElementById("loader");

function appendMessage(role, content) {
  const div = document.createElement("div");
  div.className = `message ${role}`;

  if (role === "bot" && typeof content === "object" && content.orders) {
    const title = document.createElement("p");
    title.innerText = "🧾 Your order:";
    div.appendChild(title);

    content.orders.forEach(order => {
      const card = document.createElement("div");
      card.style.border = "1px solid #ddd";
      card.style.borderRadius = "8px";
      card.style.padding = "0.5rem";
      card.style.margin = "0.5rem 0";
      card.style.display = "flex";
      card.style.gap = "1rem";
      card.style.alignItems = "center";
      card.style.backgroundColor = "#fff";

      if (order.image || order.image_url) {
        const img = document.createElement("img");
        img.src = order.image || order.image_url;
        img.alt = order.title || order.item || "image";
        img.style.width = "60px";
        img.style.height = "60px";
        img.style.borderRadius = "8px";
        img.style.objectFit = "cover";
        card.appendChild(img);
      }

      const desc = document.createElement("div");
      const title = order.title || order.item || "Item";
      const quantity = order.subtitle || order.quantity || "1 pcs";
      desc.innerHTML = `<strong>${title}</strong><br/>Jumlah: ${quantity}`;
      card.appendChild(desc);

      div.appendChild(card);
    });

    if (content.delivery_time) {
      const waktu = document.createElement("p");
      waktu.innerHTML = `🕒 Waktu antar: <strong>${content.delivery_time}</strong>`;
      div.appendChild(waktu);
    }
  } else {
    div.innerHTML = typeof content === "string"
      ? marked.parse(content)
      : `<pre>${JSON.stringify(content, null, 2)}</pre>`;
  }

  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage(text) {
  if (!text.trim()) return;
  appendMessage("user", text);
  inputField.value = "";
  loader.style.display = "block";

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        mode: "text"
      }),
    });

    const data = await res.json();

    if (data.response) {
      // Handle string response
      if (typeof data.response === "string") {
        appendMessage("bot", data.response);
      }
      // Handle structured response with text + render
      else {
        if (data.response.text) {
          appendMessage("bot", data.response.text);
        }
        if (data.response.render?.type === "order_summary") {
          appendMessage("bot", {
            orders: data.response.render.orders,
            delivery_time: data.response.render.delivery_time
          });
        }
      }
    }

  } catch (err) {
    appendMessage("bot", "⚠️ Error contacting server.");
    console.error(err);
  } finally {
    loader.style.display = "none";
  }
}

sendButton.onclick = () => {
  const message = inputField.value;
  sendMessage(message);
};

inputField.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendButton.click();
});

// --- Voice input ---
let mediaRecorder;
let audioChunks = [];

voiceButton.addEventListener("click", async () => {
  voiceButton.disabled = true;
  voiceButton.innerText = "🎙️ Listening...";

  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);

  mediaRecorder.ondataavailable = (e) => {
    audioChunks.push(e.data);
  };

  mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
    audioChunks = [];

    const formData = new FormData();
    formData.append("audio", audioBlob);

    loader.style.display = "block";

    try {
      const res = await fetch("/voice", {
        method: "POST",
        body: formData,
      });

      const contentType = res.headers.get("content-type") || "";
      if (!contentType.includes("application/json")) {
        const raw = await res.text();
        console.error("❌ Not JSON. Raw response:", raw);
        appendMessage("bot", "⚠️ Server returned invalid response.");
        return;
      }

      const data = await res.json();
      appendMessage("user", data.transcription || "[Voice not recognized]");

      if (typeof data.response === "string") {
        appendMessage("bot", data.response);
      } else {
        if (data.response.text) {
          appendMessage("bot", data.response.text);
        }
        if (data.response.render?.type === "order_summary") {
          appendMessage("bot", {
            orders: data.response.render.orders,
            delivery_time: data.response.render.delivery_time
          });
        }
      }

    } catch (err) {
      appendMessage("bot", "🎤 Voice error.");
      console.error(err);
    } finally {
      loader.style.display = "none";
      voiceButton.innerText = "🎤 Voice";
      voiceButton.disabled = false;
    }
  };

  mediaRecorder.start();

  setTimeout(() => {
    mediaRecorder.stop();
    stream.getTracks().forEach((track) => track.stop());
  }, 4000);
});
