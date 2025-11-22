// src/components/VideoUploader.jsx
import { useRef, useState } from "react";
import { uploadChunk, getSummary } from "../utils/api";

export default function VideoUploader({ onExit }) {
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);

  const [processing, setProcessing] = useState(false);
  const [summary, setSummary] = useState(null);

  // FIXED: must be refs (persistent, non-reactive values)
  const mediaRecorderRef = useRef(null);

  async function handleFile() {
    const file = fileInputRef.current.files[0];
    if (!file) return;

    // 1. Preview video
    videoRef.current.src = URL.createObjectURL(file);
    await videoRef.current.play();

    // 2. Create a canvas stream from the video
    const canvas = document.createElement("canvas");
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const ctx = canvas.getContext("2d");

    function draw() {
      ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
      requestAnimationFrame(draw);
    }
    draw();

    const stream = canvas.captureStream();

    // FIXED: store in ref, not reassign local variable
    mediaRecorderRef.current = new MediaRecorder(stream, {
      mimeType: "video/webm",
    });

    mediaRecorderRef.current.ondataavailable = async (e) => {
      if (e.data.size > 0) {
        await uploadChunk(e.data);
      }
    };

    setProcessing(true);

    // 3. Start chunking at 30-second intervals
    mediaRecorderRef.current.start(30000);

    // 4. When full video file finishes playing
    videoRef.current.onended = async () => {
      mediaRecorderRef.current.stop();
      const result = await getSummary();
      setSummary(result);
      setProcessing(false);
    };
  }

  return (
    <div>
      <h2>Upload and Process Video</h2>

      <input ref={fileInputRef} type="file" accept="video/*" onChange={handleFile} />

      <video ref={videoRef} className="w-full rounded border mt-4" controls />

      <button onClick={onExit}>Back</button>

      {processing && <p>Processing video in 30s chunks...</p>}

      {summary && (
        <div className="mt-4 p-4 border">
          <h2>Final Summary</h2>
          <pre>{JSON.stringify(summary, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
