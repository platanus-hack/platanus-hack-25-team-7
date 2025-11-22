// src/components/ChatVideoInsights.jsx
import { useState } from "react";

export default function ChatVideoInsights({ analysis, onExit }) {
  const [messages, setMessages] = useState([
    {
      sender: "ai",
      text: analysis.overallSummary,
    },
  ]);

  const [input, setInput] = useState("");

  function handleSend() {
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);

    // Simulación de respuesta basada en análisis
    const aiResponse = {
      sender: "ai",
      text: generateFakeResponse(input, analysis),
    };

    setMessages((prev) => [...prev, aiResponse]);
    setInput("");
  }

  function generateFakeResponse(question, analysis) {
    return (
      `Preguntaste: **${question}**.\n\n` +
      `Aquí tienes un desglose basado en el video:\n` +
      (analysis.segmentSummaries?.join("\n") || "Sin datos de segmentos.")
    );
  }

  return (
    <div className="chat-wrapper">
      <div className="chat-card">

        <h2 className="chat-title">Análisis del Video</h2>

        <div className="chat-box">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`msg ${m.sender === "user" ? "user-msg" : "ai-msg"}`}
            >
              {m.text}
            </div>
          ))}
        </div>

        <div className="chat-input-row">
          <input
            className="chat-input"
            placeholder="Escribe tu pregunta sobre el video..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button className="chat-send-btn" onClick={handleSend}>
            Enviar
          </button>
        </div>

        <button className="neon-btn" onClick={onExit} style={{ marginTop: "20px" }}>
          Volver
        </button>

      </div>
    </div>
  );
}
