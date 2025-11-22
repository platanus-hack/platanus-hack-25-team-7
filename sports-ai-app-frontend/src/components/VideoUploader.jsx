// src/components/VideoUploader.jsx
import { useRef, useState } from "react";
import ChatVideoInsights from "./ChatVideoInsights";
import { uploadFullVideo } from "../utils/apiAdapter";

export default function VideoUploader({ onExit }) {
  const fileInputRef = useRef(null);

  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [analysis, setAnalysis] = useState(null);

  // Ocultar el video: NO se usa ningún ref
  const [hideVideo, setHideVideo] = useState(true);

  async function handleFile() {
    const file = fileInputRef.current.files[0];
    if (!file) return;

    // Ocultar cualquier video previo
    setHideVideo(true);

    // Iniciar barra
    setProcessing(true);
    setProgress(0);

    try {
      const result = await uploadFullVideo(file, (p) => {
        setProgress(p);
      });

      setAnalysis(result);
    } catch (err) {
      console.error("Error:", err);
    } finally {
      setProcessing(false);
    }
  }

  if (analysis) {
    return <ChatVideoInsights analysis={analysis} onExit={onExit} />;
  }

  return (
    <div className="page-container">
      <h2 className="text-3xl font-bold mb-6">Subir y Analizar Video</h2>

      {/* Botón NEÓN */}
      <label className="neon-btn" style={{ cursor: "pointer" }}>
        ⬆ Subir Video
        <input
          type="file"
          accept="video/*"
          ref={fileInputRef}
          onChange={handleFile}
          style={{ display: "none" }}
        />
      </label>

      {/* VIDEO OCULTO SIEMPRE */}
      {!hideVideo && (
        <video
          style={{
            display: "none",
          }}
        />
      )}

      {/* BARRA DE PROGRESO */}
      {processing && (
        <div style={{ marginTop: "40px", width: "100%", maxWidth: "800px" }}>
          <p style={{ marginBottom: "8px" }}>
            Procesando video… <strong>{progress}%</strong>
          </p>

          <div
            style={{
              width: "100%",
              height: "14px",
              background: "#222",
              borderRadius: "10px",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: `${progress}%`,
                height: "100%",
                background:
                  "linear-gradient(90deg, #ff00ff, #ff66ff, #ff00aa)",
                transition: "width 0.3s ease-out",
              }}
            />
          </div>
        </div>
      )}

      <button
        className="neon-btn"
        style={{ marginTop: "40px" }}
        onClick={onExit}
      >
        Volver
      </button>
    </div>
  );
}
