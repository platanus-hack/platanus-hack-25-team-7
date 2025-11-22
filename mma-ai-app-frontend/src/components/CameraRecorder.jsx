import { useRef, useState } from "react";
import useContinuousRecorder from "../hooks/useContinuousRecorder";

import ProcessingLoader from "./ProcessingLoader";
import ChatVideoInsights from "./ChatVideoInsights";

import { processFinalSummary, processChunk } from "../utils/apiAdapter";

export default function CameraRecorder({ onExit }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  const [chunks, setChunks] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [isFinishing, setIsFinishing] = useState(false);

  const { recording, startRecordingInternal, stopRecordingInternal } =
    useContinuousRecorder({
      onChunk: async (blob) => {
        setChunks((prev) => [...prev, blob]);
        console.log("Chunk generado (camara):", blob);
        await processChunk(blob); // si luego quieres quitarlo, aquí lo reemplazas
      },
      onStopAll: () => {},
    });

  async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true,
    });

    streamRef.current = stream;

    videoRef.current.srcObject = stream;
    videoRef.current.play();

    startRecordingInternal(stream);
  }

  async function stopRecording() {
    stopRecordingInternal();

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
    }

    videoRef.current.srcObject = null;

    // 🔥 mostrar barra de carga mientras se procesa último chunk
    setIsFinishing(true);

    const result = await processFinalSummary(chunks);

    setAnalysis(result);
    setIsFinishing(false);
  }

  // 🔥 mostrar chat cuando análisis termina
  if (analysis) {
    return <ChatVideoInsights analysis={analysis} onExit={onExit} />;
  }

  // 🔥 mostrar barra loader mientras procesa último batch
  if (isFinishing) {
    return (
      <ProcessingLoader text="Procesando análisis final de la cámara…" />
    );
  }

  return (
    <div className="page-container">
      <h2>📹 Grabación con Cámara</h2>

      <video
        ref={videoRef}
        className="locked-video"
        controls={false}
        disablePictureInPicture
        muted
        controlsList="nodownload nofullscreen noplaybackrate noremoteplayback"
        style={{
          width: "100%",
          maxWidth: "800px",
          borderRadius: "12px",
          marginTop: "20px",
          pointerEvents: "none",
          userSelect: "none",
          opacity: 0.9,
        }}
      />

      <div style={{ marginTop: "20px" }}>
        {!recording && (
          <button className="neon-btn" onClick={startRecording}>
            🎬 Iniciar Grabación
          </button>
        )}

        {recording && (
          <button className="neon-btn stop" onClick={stopRecording}>
            ⛔ Detener
          </button>
        )}
      </div>

      <button className="neon-btn" onClick={onExit} style={{ marginTop: "30px" }}>
        Volver
      </button>

      <style>{`
        .neon-btn.stop {
          background: #ff0033;
          box-shadow: 0 0 10px #ff0033;
        }
      `}</style>
    </div>
  );
}
