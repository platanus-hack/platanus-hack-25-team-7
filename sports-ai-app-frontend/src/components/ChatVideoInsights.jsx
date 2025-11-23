// src/components/ChatVideoInsights.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { askAgent } from "../utils/apiAdapter";

export default function ChatVideoInsights({ analysis }) {
  const navigate = useNavigate();

  const [messages, setMessages] = useState([
    {
      sender: "ai",
      text: analysis.overallSummary || analysis.overall_summary || "Hola, soy tu asistente de video. ¿En qué puedo ayudarte?",
    },
  ]);

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSend() {
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const responseText = await askAgent(userMessage.text);
      const aiResponse = {
        sender: "ai",
        text: responseText,
      };
      setMessages((prev) => [...prev, aiResponse]);
    } catch (error) {
      console.error("Error asking agent:", error);
      setMessages((prev) => [...prev, { sender: "ai", text: "Error al conectar con el asistente." }]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="chat-wrapper">
      <div className="chat-card">

        <h2 className="chat-title gradient-text2">Análisis del Video</h2>

        <div className="chat-box">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`msg ${m.sender === "user" ? "user-msg" : "ai-msg"}`}
            >
              {m.text}
            </div>
          ))}
          {isLoading && <div className="msg ai-msg">...</div>}
        </div>

        <div className="chat-input-row">
          <input
            className="chat-input"
            placeholder="Escribe tu pregunta sobre el video..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSend()}
          />
          <button className="chat-send-btn" onClick={handleSend} disabled={isLoading}>
            {isLoading ? "..." : "Enviar"}
          </button>
        </div>

        <button
          className="neon-border-btn"
          onClick={() => navigate("/")}
          style={{ marginTop: "20px" }}
        >
        <span className="gradient-text">Volver</span>
        </button>

      </div>
    </div>
  );
}
