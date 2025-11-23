// src/pages/ReviewPage.jsx
import { useEffect, useState, useRef } from "react";
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { useParams } from "react-router-dom";
import { getAnalysis, askAgent } from "../utils/apiAdapter";
import remarkGfm from "remark-gfm";
import ReactMarkdown from "react-markdown";
import "../styles/ReviewPage.css";

function extractPreview(text) {
  if (!text) return "";

  const cleaned = text.replace(/\*/g, "").replace(/\n/g, " ");
  const parts = cleaned.split("Resumen Estadístico:");
  const after = parts[1] ?? cleaned;

  return after.trim().slice(0, 200) + "...";
}

export default function ReviewPage() {
  const { jobId } = useParams();

  const [analysis, setAnalysis] = useState(null);
  const [hoverSummary, setHoverSummary] = useState(null);

  const [selectedSegmentIndex, setSelectedSegmentIndex] = useState(null);
  const [playingSegmentIndex, setPlayingSegmentIndex] = useState(null);
  const [activeTab, setActiveTab] = useState("general"); // "general" | "striking" | "grappling" | "submission"

  const videoRef = useRef(null);
  const [videoURL, setVideoURL] = useState(null);

  // Chat state
  const [messages, setMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [isChatCollapsed, setIsChatCollapsed] = useState(false);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const chatEndRef = useRef(null);

  function parseS3Url(url) {
    const m = url.match(/^https:\/\/([^.]+)\.s3\.amazonaws\.com\/(.+)$/);
    return { bucket: m[1], key: m[2] };
  }
  
  // Scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isChatCollapsed]);

  async function streamToBlob(stream, mimeType) {
    const reader = stream.getReader();
    const chunks = [];
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
    }
    return new Blob(chunks, { type: mimeType });
  }

  /* ================= VIDEO LOAD ================= */
  useEffect(() => {
    const s3Path = localStorage.getItem("uploaded_video_url");
    if (!s3Path) return;

    async function loadVideo() {
      const { bucket, key } = parseS3Url(s3Path);
      const s3 = new S3Client({
        region: "us-east-1",
        credentials: {
          accessKeyId: import.meta.env.VITE_AWS_ACCESS_KEY,
          secretAccessKey: import.meta.env.VITE_AWS_SECRET_KEY,
        },
      });

      const data = await s3.send(new GetObjectCommand({ Bucket: bucket, Key: key }));
      const blob = await streamToBlob(data.Body, "video/mp4");
      setVideoURL(URL.createObjectURL(blob));
    }

    loadVideo();
  }, []);

  /* ================= ANALYSIS LOAD ================= */
  useEffect(() => {
    async function load() {
      const data = await getAnalysis(jobId);
      setAnalysis(data);
      
      // Initialize chat with overall summary
      if (data?.overall_summary) {
        setMessages([{
          sender: "ai",
          text: data.overall_summary
        }]);
      }
    }
    load();
  }, [jobId]);

  /* ================= VIDEO TIME UPDATE ================= */
  function handleTimeUpdate() {
    if (!videoRef.current || !analysis) return;
    const currentTime = videoRef.current.currentTime;
    const segmentSize = analysis.segment_size || 30; // Default to 30s if not present
    const currentIdx = Math.floor(currentTime / segmentSize);
    
    if (currentIdx < analysis.chunk_analyses.length) {
      setPlayingSegmentIndex(currentIdx);
    }
  }

  /* ================= JUMP TO SEGMENT ================= */
  function jumpToSegment(idx) {
    if (!videoRef.current) return;

    const seconds = idx * (analysis.segment_size || 30);

    if (Number.isFinite(seconds)) {
      videoRef.current.currentTime = seconds;
    }

    setSelectedSegmentIndex(idx);
    setActiveTab("general"); // Reset to general tab
  }

  /* ================= CHAT FUNCTIONS ================= */
  async function handleSendMessage() {
    if (!chatInput.trim()) return;

    const userMessage = { sender: "user", text: chatInput };
    setMessages(prev => [...prev, userMessage]);
    setChatInput("");
    setIsChatLoading(true);

    try {
      const responseText = await askAgent(userMessage.text);
      
      const aiResponse = {
        sender: "ai",
        text: responseText
      };
      
      setMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      console.error("Error asking agent:", error);
      const errorResponse = {
        sender: "ai",
        text: "Lo siento, hubo un error al procesar tu pregunta. Por favor intenta de nuevo."
      };
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsChatLoading(false);
    }
  }

  /* ================= GET CURRENT CONTENT ================= */
  function getCurrentContent() {
    if (selectedSegmentIndex === null) {
      return analysis.overall_summary || "Selecciona un segmento para ver el análisis detallado.";
    }

    const segment = analysis.chunk_analyses[selectedSegmentIndex];
    
    switch (activeTab) {
      case "striking":
        return segment.striking || "No hay datos de striking para este segmento.";
      case "grappling":
        return segment.grappling || "No hay datos de grappling para este segmento.";
      case "submission":
        return segment.submission || "No hay datos de submission para este segmento.";
      default:
        return segment.general_analyst || "No hay análisis general para este segmento.";
    }
  }

  if (!analysis) return <p>Cargando análisis…</p>;

  return (
    <div 
      className="review-page-container"
      style={{
        gridTemplateColumns: isChatCollapsed ? "50% 45% 5%" : "40% 35% 25%"
      }}
    >
      
      {/* ================= LEFT COLUMN: VIDEO ================= */}
      <div className="video-column">
        <video
          ref={videoRef}
          src={videoURL}
          controls
          className="video-player"
          style={{ aspectRatio: "16/9", objectFit: "cover" }}
          onTimeUpdate={handleTimeUpdate}
        />

        {/* ================= TIMELINE ================= */}
        <div className="timeline-container">
          {analysis.chunk_analyses?.map((seg, i) => (
            <div
              key={i}
              className={`timeline-segment ${selectedSegmentIndex === i ? 'active' : ''} ${playingSegmentIndex === i ? 'playing' : ''}`}
              onMouseEnter={() => setHoverSummary(extractPreview(seg.general_analyst))}
              onMouseLeave={() => setHoverSummary(null)}
              onClick={() => jumpToSegment(i)}
              title={`Segmento ${i + 1}`}
            />
          ))}
        </div>

        {hoverSummary && (
          <div className="timeline-tooltip">
            <strong>Resumen del segmento:</strong>
            <br />
            {hoverSummary}
          </div>
        )}
      </div>

      {/* ================= MIDDLE COLUMN: ANALYSIS ================= */}
      <div className="analysis-column">
        <h2 className="gradient-text2">
          {selectedSegmentIndex !== null 
            ? `Análisis - Segmento ${selectedSegmentIndex + 1}` 
            : "Resumen General"}
        </h2>

        {/* Tabs */}
        {selectedSegmentIndex !== null && (
          <div className="tabs-container">
            <button
              className={`tab-button ${activeTab === "general" ? 'active' : ''}`}
              onClick={() => setActiveTab("general")}
            >
              📊 General
            </button>
            <button
              className={`tab-button ${activeTab === "striking" ? 'active' : ''}`}
              onClick={() => setActiveTab("striking")}
            >
              🥊 Striking
            </button>
            <button
              className={`tab-button ${activeTab === "grappling" ? 'active' : ''}`}
              onClick={() => setActiveTab("grappling")}
            >
              🤼 Grappling
            </button>
            <button
              className={`tab-button ${activeTab === "submission" ? 'active' : ''}`}
              onClick={() => setActiveTab("submission")}
            >
              🧩 Submission
            </button>
          </div>
        )}

        {/* Content */}
        <div className="analysis-content">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {getCurrentContent()}
          </ReactMarkdown>
        </div>
      </div>

      {/* ================= RIGHT COLUMN: CHAT ================= */}
      <div className={`chat-column ${isChatCollapsed ? 'collapsed' : ''}`}>
        <div className="chat-header">
          <h3 className="gradient-text2">💬 Chat</h3>
          <button 
            className="collapse-button"
            onClick={() => setIsChatCollapsed(!isChatCollapsed)}
          >
            {isChatCollapsed ? '◀' : '▶'}
          </button>
        </div>

        {!isChatCollapsed && (
          <>
            <div className="chat-messages">
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`chat-message ${msg.sender === 'user' ? 'user-message' : 'ai-message'}`}
                >
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.text}
                  </ReactMarkdown>
                </div>
              ))}
              {isChatLoading && (
                <div className="chat-message ai-message">
                  <em>Pensando...</em>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            <div className="suggested-questions">
               <button className="suggestion-chip" onClick={() => setChatInput("¿Cuáles son mis errores principales?")}>Errores principales</button>
               <button className="suggestion-chip" onClick={() => setChatInput("¿Cómo mejorar mi defensa?")}>Mejorar defensa</button>
               {selectedSegmentIndex !== null && (
                 <button className="suggestion-chip" onClick={() => setChatInput(`Analiza el segmento ${selectedSegmentIndex + 1}`)}>Analizar este segmento</button>
               )}
            </div>

            <div className="chat-input-container">
              <input
                className="chat-input"
                placeholder="Pregunta sobre el video..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !isChatLoading && handleSendMessage()}
                disabled={isChatLoading}
              />
              <button className="chat-send-button" onClick={handleSendMessage} disabled={isChatLoading}>
                {isChatLoading ? '...' : 'Enviar'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
