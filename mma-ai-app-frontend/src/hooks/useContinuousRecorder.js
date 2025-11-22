// src/hooks/useContinuousRecorder.js
import { useRef, useState } from "react";

export default function useContinuousRecorder({ onChunk, onStopAll }) {
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null);

  function startRecordingInternal(stream) {
    mediaRecorderRef.current = new MediaRecorder(stream, {
      mimeType: "video/webm",
    });

    mediaRecorderRef.current.ondataavailable = async (event) => {
      if (event.data.size > 0) {

        console.log(
          "📸 Cámara: Chunk generado",
          new Date().toLocaleTimeString(),
          "Tamaño:",
          event.data.size
        );

        await onChunk(event.data);

        console.log(
          "📤 Chunk de cámara enviado",
          new Date().toLocaleTimeString()
        );
      }
    };

    mediaRecorderRef.current.start(1000); // chunk every 30 seconds
    setRecording(true);
  }

  async function stopRecordingInternal() {
    setRecording(false);
    mediaRecorderRef.current.stop();
    await onStopAll();
  }

  return { recording, startRecordingInternal, stopRecordingInternal };
}
