import { useState, useRef, useEffect } from "react";

export default function ChatVideoInsights({ analysis, onExit }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: analysis.resumen_global,
    },
  ]);

  const inputRef = useRef(null);
  const chatEndRef = useRef(null);

  const containerWidth = "max-w-3xl"; // controla ancho máximo del texto

  function scrollToBottom() {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  function answerUserQuestion(question) {
    const intervalMatch = analysis.intervalos
      .map(
        (i) =>
          `**${i.intervalo}**  
• *Errores*: ${i.errores.join(", ")}  
• *Oportunidades*: ${i.oportunidades.join(", ")}`
      )
      .join("\n\n");

    const response = `
Preguntaste: **${question}**

Aquí tienes un desglose basado en el video:

${intervalMatch}

Si quieres profundizar, menciona un minuto o un segmento.
`;

    addMessage("assistant", response);
  }

  function addMessage(role, content) {
    setMessages((prev) => [...prev, { role, content }]);
  }

  function handleSend() {
    const text = inputRef.current.value.trim();
    if (!text) return;
    addMessage("user", text);
    inputRef.current.value = "";
    answerUserQuestion(text);
  }

  return (
    <div className="page-container">

      <h2 className="text-4xl font-bold mb-6 text-red-500">Análisis del Video</h2>

      <div
        className={`w-full ${containerWidth} h-[500px] overflow-y-auto border border-gray-700 rounded-xl bg-[#111] p-6 shadow-xl`}
      >
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`my-4 px-5 py-4 rounded-xl leading-relaxed whitespace-pre-line ${
              m.role === "user"
                ? "bg-[#242424] text-right ml-auto w-fit max-w-[85%]"
                : "bg-[#1A1A1A] border border-gray-700 mr-auto w-fit max-w-[85%]"
            }`}
          >
            {m.content}
          </div>
        ))}
        <div ref={chatEndRef}></div>
      </div>

      {/* INPUT AREA - Modern GPT style */}
      <div className={`w-full ${containerWidth} mt-6 flex items-center gap-3`}>
        <input
          ref={inputRef}
          className="flex-grow bg-[#1A1A1A] border border-gray-700 text-gray-200 rounded-xl p-4 text-lg focus:outline-none focus:ring-2 focus:ring-red-600"
          placeholder="Escribe tu pregunta sobre el video…"
        />
        <button
          onClick={handleSend}
          className="bg-red-600 hover:bg-red-700 px-6 py-4 rounded-xl text-white font-semibold"
        >
          Enviar
        </button>
      </div>

      <button
        onClick={onExit}
        className="mt-6 text-gray-400 hover:text-gray-200 text-sm underline"
      >
        Volver
      </button>
    </div>
  );
}
