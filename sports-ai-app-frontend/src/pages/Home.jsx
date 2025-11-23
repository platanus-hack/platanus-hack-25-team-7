// src/pages/Home.jsx
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import CameraRecorder from "../components/CameraRecorder";

export default function Home() {
  const [mode, setMode] = useState(null);
  const navigate = useNavigate();

  // 🔥 cuando mode cambia a "upload", navega correctamente
  useEffect(() => {
    if (mode === "upload") {
      navigate("/upload");
    }
  }, [mode, navigate]);

  return (
    <div className="page-container">
      <h1 className="gradient-text">MMA AI Round Analyzer</h1>

      {!mode && (
        <div>
          <button className="neon-border-btn" onClick={() => setMode("camera")}>
            <span className="gradient-text">Start Camera Recording</span>
          </button>

          <button className="neon-border-btn" onClick={() => setMode("upload")}>
            <span className="gradient-text">Upload Video File</span>
          </button>
        </div>
      )}

      {mode === "camera" && <CameraRecorder onExit={() => setMode(null)} />}
    </div>
  );
}
