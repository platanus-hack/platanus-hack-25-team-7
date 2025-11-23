// src/pages/ReviewPage.jsx
import { useEffect, useState, useRef } from "react";
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { useParams, useNavigate } from "react-router-dom";
import { getAnalysis } from "../utils/apiAdapter";
import remarkGfm from "remark-gfm";
import ReactMarkdown from "react-markdown";

function extractPreview(text) {
  if (!text) return "";

  const cleaned = text.replace(/\*/g, "").replace(/\n/g, " ");
  const parts = cleaned.split("Resumen Estadístico:");
  const after = parts[1] ?? cleaned;

  return after.trim().slice(0, 200) + "...";
}

export default function ReviewPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();

  const [analysis, setAnalysis] = useState(null);
  const [hoverSummary, setHoverSummary] = useState(null);

  const [selectedSegmentIndex, setSelectedSegmentIndex] = useState(null); // SIEMPRE número
  const [openCategory, setOpenCategory] = useState(null); // "striking" | "grappling" | "submission" | null

  const [selectedSummary, setSelectedSummary] = useState(null);

  const videoRef = useRef(null);
  const [videoURL, setVideoURL] = useState(null);

  function parseS3Url(url) {
    const m = url.match(/^https:\/\/([^.]+)\.s3\.amazonaws\.com\/(.+)$/);
    return { bucket: m[1], key: m[2] };
  }

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
    }
    load();
  }, [jobId]);

  /* ================= JUMP TO SEGMENT ================= */
  function jumpToSegment(idx) {
    if (!videoRef.current) return;

    const seconds = idx * analysis.segment_size;

    if (Number.isFinite(seconds)) {
      videoRef.current.currentTime = seconds;
    }

    setSelectedSegmentIndex(idx);   // SIEMPRE número
    setOpenCategory(null);          // cierra secciones
    setSelectedSummary(analysis.chunk_analyses[idx].general_analyst);
  }

  if (!analysis) return <p>Cargando análisis…</p>;

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 4fr 2fr 1fr",
        width: "100vw",
        minHeight: "100vh",
      }}
    >
      {/* ================= VIDEO ================= */}
      <div style={{ gridColumn: "2", padding: "20px" }}>
        <video
          ref={videoRef}
          src={videoURL}
          controls
          style={{ width: "100%", borderRadius: "10px", marginBottom: "20px" }}
        />

        {/* ================= TIMELINE ================= */}
        <div
          style={{
            display: "flex",
            gap: "4px",
            padding: "10px 0",
            width: "100%",
            height: "40px",
          }}
        >
          {analysis.chunk_analyses.map((seg, i) => (
            <div
              key={i}
              onMouseEnter={() =>
                setHoverSummary(extractPreview(seg.general_analyst))
              }
              onMouseLeave={() => setHoverSummary(null)}
              onClick={() => jumpToSegment(i)}
              style={{
                flex: 1,
                background: "#2575FC",
                border: "1px solid #0057ec",
                borderRadius: "4px",
                cursor: "pointer"
              }}
            />
          ))}
        </div>

        {hoverSummary && (
          <div
            style={{
              marginTop: "10px",
              padding: "10px",
              background: "#111",
              color: "white",
              borderRadius: "6px",
              border: "1px solid #444",
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
          padding: "20px",
          background: "rgba(0,0,0,0.7)",
          color: "white",
        }}
      >
        <h2 className="gradient-text2">Detalle del segmento</h2>

        {selectedSummary ? (
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{selectedSummary}</ReactMarkdown>
        ) : (
          <p className="gradient-text2">Haz click en un segmento.</p>
        )}

        {/* ================= CATEGORIES ================= */}
        {selectedSegmentIndex !== null && (
          <div style={{ marginTop: "30px" }}>
            <h3 style={{ fontWeight: 700 }}>
              Detalle técnico — Segmento {selectedSegmentIndex}
            </h3>

            <ul style={{ listStyle: "none", paddingLeft: "20px" }}>

              {/* STRIKING */}
              <li
                style={{ cursor: "pointer" }}
                onClick={() =>
                  setOpenCategory(openCategory === "striking" ? null : "striking")
                }
              >
                🥊 <strong>Striking</strong>
              </li>
              {openCategory === "striking" && (
                <ReactMarkdown style={{ paddingLeft: "20px" }}>
                  {analysis.chunk_analyses[selectedSegmentIndex].striking ??
                    "No hay datos"}
                </ReactMarkdown>
              )}

              {/* GRAPPLING */}
              <li
                style={{ cursor: "pointer", marginTop: "10px" }}
                onClick={() =>
                  setOpenCategory(openCategory === "grappling" ? null : "grappling")
                }
              >
                🤼 <strong>Grappling</strong>
              </li>
              {openCategory === "grappling" && (
                <ReactMarkdown style={{ paddingLeft: "20px" }}>
                  {analysis.chunk_analyses[selectedSegmentIndex].grappling ??
                    "No hay datos"}
                </ReactMarkdown>
              )}

              {/* SUBMISSION */}
              <li
                style={{ cursor: "pointer", marginTop: "10px" }}
                onClick={() =>
                  setOpenCategory(openCategory === "submission" ? null : "submission")
                }
              >
                🧩 <strong>Submission</strong>
              </li>
              {openCategory === "submission" && (
                <ReactMarkdown style={{ paddingLeft: "20px" }}>
                  {analysis.chunk_analyses[selectedSegmentIndex].submission ??
                    "No hay datos"}
                </ReactMarkdown>
              )}
            </ul>
          </div>
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
