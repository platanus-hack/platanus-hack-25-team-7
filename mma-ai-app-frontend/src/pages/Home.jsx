// src/pages/Home.jsx
import { useState } from "react";
import CameraRecorder from "../components/CameraRecorder";
import VideoUploader from "../components/VideoUploader";

export default function Home() {
  const [mode, setMode] = useState(null);

  return (
    <div>
      <h1>MMA AI Round Analyzer</h1>

      {!mode && (
        <div>
          <button onClick={() => setMode("camera")}>
            Start Camera Recording
          </button>

          <button onClick={() => setMode("upload")}>
            Upload Video File
          </button>
        </div>
      )}

      {mode === "camera" && <CameraRecorder onExit={() => setMode(null)} />}
      {mode === "upload" && <VideoUploader onExit={() => setMode(null)} />}
    </div>
  );
}
