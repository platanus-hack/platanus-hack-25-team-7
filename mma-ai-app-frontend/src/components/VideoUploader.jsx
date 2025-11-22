import { useRef, useState } from "react";
import ChatVideoInsights from "./ChatVideoInsights";
import { processChunk, processFinalSummary } from "../utils/apiAdapter";

export default function VideoUploader({ onExit }) {
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);

  const [processing, setProcessing] = useState(false);
  const [chunks, setChunks] = useState([]); // solo para UI
  const [analysis, setAnalysis] = useState(null);

  const mediaRecorderRef = useRef(null);
  
  // FIX: source of truth for chunks
  const chunksRef = useRef([]);

  async function handleFile() {
    const file = fileInputRef.current.files[0];
    if (!file) return;

    // Vista previa
    videoRef.current.src = URL.createObjectURL(file);
    await videoRef.current.play();

    // Canvas para procesar frame por frame
    const canvas = document.createElement("canvas");
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const ctx = canvas.getContext("2d");

    function drawLoop() {
        const video = videoRef.current;

        // esperar hasta que el video esté listo para ser dibujado
        if (!video || video.readyState < 2) {
            requestAnimationFrame(drawLoop);
            return;
        }

        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        requestAnimationFrame(drawLoop);
        }

    drawLoop();

    const stream = canvas.captureStream();
    mediaRecorderRef.current = new MediaRecorder(stream);

    mediaRecorderRef.current.ondataavailable = async (e) => {
      if (e.data.size > 0) {
        console.log("Chunk generado:", e.data);

        // FIX: guardar chunk en ref para evitar problemas de timing
        chunksRef.current.push(e.data);

        // actualizar UI
        setChunks([...chunksRef.current]);

        // En ambiente real llamarías a:
        await processChunk(e.data);
      }
    };

    setProcessing(true);

    mediaRecorderRef.current.start(30000); // chunk de 30 segundos

    videoRef.current.onended = async () => {
      mediaRecorderRef.current.stop();

      console.log("📦 Cantidad total de chunks capturados:", chunksRef.current.length);

      // FIX: Usar chunksRef en vez de state (para datos consistentes)
      const result = await processFinalSummary(chunksRef.current);

      setAnalysis(result);
      setProcessing(false);
    };
  }

  if (analysis) {
    return <ChatVideoInsights analysis={analysis} onExit={onExit} />;
  }

  return (
  <div className="page-container">

    <h2 className="text-4xl font-bold mb-8 text-red-500">Subir y Analizar Video</h2>

    {/* BUTTON + HIDDEN FILE INPUT */}
    <div className="mb-6">
    <input
        id="video-upload"
        ref={fileInputRef}
        type="file"
        accept="video/*"
        className="hidden"   // ⬅️ Esto lo oculta 100% y elimina filename
        onChange={handleFile}
    />

    <label
        htmlFor="video-upload"
        className="
        neon-button
        cursor-pointer
        "
    >
        <svg width="20" height="20" fill="currentColor">
        <path d="M16 13v5H4v-5H2v7h16v-7zM11 1v9.17l3.59-3.58L16 8l-6 6-6-6 1.41-1.41L9 10.17V1h2z"/>
        </svg>
        Subir Video
    </label>
    </div>


    {/* VIDEO PREVIEW NON-INTERACTIVE */}
    <div className="relative w-full max-w-4xl border border-gray-800 rounded-xl overflow-hidden shadow-xl">

      <video
        ref={videoRef}
        className="w-full block pointer-events-none select-none opacity-90"
        controls={false}
        disablePictureInPicture
        controlsList="nodownload noplaybackrate nofullscreen noremoteplayback"
        muted
        playsInline
      />

      {/* Optional: overlay that blocks EVERYTHING */}
      <div className="absolute inset-0 pointer-events-none"></div>
    </div>

    {processing && (
      <p className="mt-4 text-lg text-gray-400 animate-pulse">
        Procesando video en chunks de 30s…
      </p>
    )}

    <p className="mt-3 text-sm text-gray-500">
      Chunks capturados: {chunks.length}
    </p>

    <button
      onClick={onExit}
      className="mt-8 text-gray-400 hover:text-gray-200 text-sm underline"
    >
      Volver
    </button>
  </div>
);

}
