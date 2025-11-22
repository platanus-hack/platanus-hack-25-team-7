// src/components/CameraRecorder.jsx
import { useRef, useState } from "react";
import useContinuousRecorder from "../hooks/useContinuousRecorder";
import { uploadChunk, getSummary } from "../utils/api";

export default function CameraRecorder({ onExit }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [summary, setSummary] = useState(null);

  const { recording, startRecordingInternal, stopRecordingInternal } =
    useContinuousRecorder({
      onChunk: async (blob) => await uploadChunk(blob),
      onStopAll: async () => {
        const result = await getSummary();
        setSummary(result);
      },
    });

  async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true,
    });

    videoRef.current.srcObject = stream;
    videoRef.current.play();
    streamRef.current = stream;

    startRecordingInternal(stream);
  }

  async function stopRecording() {
    stopRecordingInternal();

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
    }

    videoRef.current.srcObject = null; // <--- SE LIMPIA EL VIDEO
  }

  return (
    <div>
      <h2>Camera Recording</h2>

      <video ref={videoRef} className="w-full rounded border" autoPlay muted />

      {!recording && <button onClick={startRecording}>Start</button>}
      {recording && <button onClick={stopRecording}>Stop</button>}

      <button onClick={onExit}>Back</button>

      {summary && (
        <div className="mt-4 p-4 border">
          <h2>Final Summary</h2>
          <pre>{JSON.stringify(summary, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
