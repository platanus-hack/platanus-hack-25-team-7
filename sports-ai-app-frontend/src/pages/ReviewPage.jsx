// src/pages/ReviewPage.jsx
import { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getAnalysis } from "../utils/apiAdapter";

export default function ReviewPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();

  const [analysis, setAnalysis] = useState(null);
  const [hoverSummary, setHoverSummary] = useState(null);
  const [selectedSummary, setSelectedSummary] = useState(null);

  const videoRef = useRef(null);

  useEffect(() => {
    async function load() {
      const data = await getAnalysis(jobId);
      setAnalysis(data);
    }
    load();
  }, [jobId]);

  // Click segment → jump video
  function jumpToSegment(i) {
    if (!videoRef.current) return;

    const seconds = (i - 1) * analysis.segment_size;
    videoRef.current.currentTime = seconds;

    setSelectedSummary(analysis.segments[i - 1].summary);
  }

  if (!analysis) return <p>Cargando análisis…</p>;

  return (
    <div   style={{
    display: "grid",
    gridTemplateColumns: "1fr 4fr 2fr 1fr",
    height: "100vh",
    width: "100vw"
  }}>

      {/* ================= VIDEO SIDE ================= */}
      <div style={{ gridColumn: "2", padding: "20px" }}>
        <video
          ref={videoRef}
          src={analysis.video_url}
          controls
          style={{
            width: "100%",
            borderRadius: "10px",
            marginBottom: "20px"
          }}
        />

        {/* ================= TIMELINE ================= */}
        <div
          style={{
            display: "flex",
            gap: "4px",
            padding: "10px 0",
            width: "100%",
            height: "40px",
            alignItems: "center"
          }}
        >
          {analysis.chunk_analyses.map((seg, index) => (
            <div
              key={seg.id}
              onMouseEnter={() => setHoverSummary(seg.summary)}
              onMouseLeave={() => setHoverSummary(null)}
              onClick={() => jumpToSegment(seg.id)}
              style={{
                flex: 1,
                height: "100%",
                background: "#2575FC",
                border: "1px solid #0057ecff",
                borderRadius: "4px",
                cursor: "pointer",
                transition: "0.2s"
              }}
            />
          ))}
        </div>

        {/* ================= TOOLTIP HOVER ================= */}
        {hoverSummary && (
          <div
            style={{
              marginTop: "10px",
              padding: "10px",
              background: "#111",
              border: "1px solid #444",
              borderRadius: "5px",
              color: "white",
              maxWidth: "80%"
            }}
          >
            <strong>Resumen del segmento:</strong>
            <br />
            {hoverSummary}
          </div>
        )}
      </div>

      {/* ================= SIDE PANEL ================= */}
      <div
        style={{
          flex: 1.3,
          background: "rgba(0,0,0,0.7)",
          padding: "20px",
          color: "white"
        }}
      >
        <h2 className="gradient-text2" style={{ marginBottom: "20px" }}>Detalle del segmento</h2>

        {selectedSummary ? (
          <p>{selectedSummary}</p>
        ) : (
          <p className="gradient-text2">Haz click en un segmento.</p>
        )}

        <button
          className="neon-border-btn"
          onClick={() => navigate(`/chat/${jobId}`)}
          style={{ marginTop: "30px" }}
        >
          <span className="gradient-text">Ir al Chat</span>
        </button>
      </div>
    </div>
  );
}
