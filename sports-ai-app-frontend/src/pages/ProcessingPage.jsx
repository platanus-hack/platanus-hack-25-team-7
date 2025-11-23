// src/pages/ProcessingPage.jsx
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { pollSplitProgress, pollAnalysisProgress } from "../utils/apiAdapter";

export default function ProcessingPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();

  const [phase, setPhase] = useState("split"); // "split" | "analysis"
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    async function process() {
      // 🔥 Fase 1: SPLIT
      console.log("⌛ Iniciando split...");
      await pollSplitProgress(jobId, (p) => setProgress(p));
      console.log("✅ Split completado");

      // cambiar texto y reiniciar barra
      setPhase("analysis");
      setProgress(0);

      // 🔥 Fase 2: ANALYSIS
      const analysisResult = await pollAnalysisProgress(jobId, (p) => setProgress(p));
      console.log("✅ Análisis completado", analysisResult);

      // Navegar al review
      navigate(`/review/${jobId}`); 
    }

    process();
  }, [jobId, navigate]);

  return (
    <div className="page-container">
      <h1 className="text-2xl mb-6 gradient-text">
        {phase === "split" ? "Procesando Video (Fragmentando)..." : "Analizando Video..."}
      </h1>

      <p className="mb-4 text-lg font-extrabold gradient-text">{progress}%</p>

      <div
        style={{
          width: "100%",
          maxWidth: "600px",
          height: "20px",
          background: "#222",
          borderRadius: "10px",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${progress}%`,
            height: "100%",
            background: "linear-gradient(90deg, #6A11CB, #2575FC)",
            transition: "width 0.25s ease-out",
          }}
        />
      </div>
    </div>
  );
}
