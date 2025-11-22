// src/hooks/useRecorder.js
import { useState, useRef } from 'react';

export default function useRecorder() {
  const [recording, setRecording] = useState(false);
  const [videoURL, setVideoURL] = useState(null);
  const mediaRecorderRef = useRef(null);
  const chunks = useRef([]);

  async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: "video/webm" });

    mediaRecorderRef.current.ondataavailable = (e) => chunks.current.push(e.data);
    mediaRecorderRef.current.onstop = () => {
      const blob = new Blob(chunks.current, { type: "video/webm" });
      chunks.current = [];
      setVideoURL(URL.createObjectURL(blob));
    };

    mediaRecorderRef.current.start();
    setRecording(true);

    // stop after 30s
    setTimeout(() => stopRecording(), 30000);
  }

  function stopRecording() {
    mediaRecorderRef.current.stop();
    setRecording(false);
  }

  return { recording, videoURL, startRecording, stopRecording };
}
