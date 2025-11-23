// src/pages/UploadPage.jsx
import { useNavigate } from "react-router-dom";
import { useRef } from "react";
import { uploadFullVideo } from "../utils/apiAdapter";

export default function UploadPage() {
  const fileRef = useRef();
  const navigate = useNavigate();

  async function handleFile() {
    const file = fileRef.current.files[0];
    if (!file) return;

    // Subir archivo → backend devuelve job_id
    const result = await uploadFullVideo(file);
    navigate(`/processing/${result.job_id}`);
  }

  return (
    <div className="page-container">
      <h1 className="text-3xl font-bold mb-6 gradient-text">Subir Video</h1>

      <div className="button-row">
        <label className="neon-border-btn" style={{ cursor: "pointer" }}>
          ⬆ <span className="gradient-text">Seleccionar Archivo de Video</span>
          <input
            type="file"
            accept="video/*"
            ref={fileRef}
            onChange={handleFile}
            style={{ display: "none" }}
          />
        </label>

        <button
          className="neon-border-btn"
          onClick={() => navigate("/")}
        >
          ⬅ <span className="gradient-text">Volver al Inicio</span>
        </button>
      </div>
    </div>
  );
}
