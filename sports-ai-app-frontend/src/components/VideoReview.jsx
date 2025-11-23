// src/components/VideoReview.jsx
import { useState, useRef } from "react";

export default function VideoReview({ videoUrl, splitData, onContinue }) {
  // splitData = [{ chunkId, startSec, endSec, summary, insights }]
  const videoRef = useRef(null);
  const [activeChunk, setActiveChunk] = useState(null);

  function handleChunkClick(chunk) {
    setActiveChunk(chunk);

    // Hacer seek al segundo del chunk
    if (videoRef.current) {
      videoRef.current.currentTime = chunk.startSec;
    }
  }

  return (
    <div className="flex w-full h-full gap-4 px-6 py-6">

      {/* ================================
           🔴  VIDEO PRINCIPAL
      ================================= */}
      <div className="flex-1 bg-black/40 border border-white/20 rounded-xl p-4">
        <video
          src={videoUrl}
          ref={videoRef}
          className="w-full rounded-lg"
          controls
        />
      </div>
      {/* ================================
            🟩  HISTOGRAMA DE CHUNKS
        ================================= */}
        <div className="mt-4 w-full flex gap-1">
        {splitData.map((chunk) => {
            const active = chunk.chunkId === activeChunk?.chunkId;

            return (
            <div
                key={chunk.chunkId}
                onClick={() => handleChunkClick(chunk)}
                className={`
                flex-1 h-6 cursor-pointer 
                rounded-sm transition-all
                ${active ? "bg-green-400" : "bg-white/30 hover:bg-white/50"}
                `}
                title={`Chunk ${chunk.chunkId} (${chunk.startSec}s-${chunk.endSec}s)`}
            />
            );
        })}
        </div>


      {/* ================================
           🔵  PANEL LATERAL DE ANÁLISIS
      ================================= */}
      <div className="w-80 bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-4 overflow-y-auto">
        <h3 className="text-xl font-semibold mb-2">Detalles del Chunk</h3>

        {!activeChunk && (
          <p className="text-white/60">Selecciona un bloque del histograma.</p>
        )}

        {activeChunk && (
          <>
            <p className="text-sm text-white/70">Chunk #{activeChunk.chunkId}</p>
            <p className="text-xs text-white/50">
              {activeChunk.startSec}–{activeChunk.endSec}s
            </p>

            <h4 className="mt-4 font-semibold text-lg">Resumen</h4>
            <p className="text-white/80 text-sm">
              {activeChunk.summary}
            </p>

            <h4 className="mt-4 font-semibold text-lg">Insights</h4>
            <ul className="text-white/80 text-sm ml-3 list-disc">
              {activeChunk.insights?.map((i, idx) => (
                <li key={idx}>{i}</li>
              ))}
            </ul>
          </>
        )}

        <button
          onClick={onContinue}
          className="mt-6 w-full bg-purple-600 hover:bg-purple-500 transition text-white font-semibold py-2 rounded-lg"
        >
          Ir al Chat →
        </button>
      </div>
    </div>
  );
}
