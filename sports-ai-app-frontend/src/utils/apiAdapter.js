
import { generateFakeVideoSummary } from "./fakeVideoAnalysis";
import { uploadChunk, getSummary } from "./api";

// El backend REAL trabaja chunk por chunk → (FastAPI)
// La simulación trabaja con todos los blobs → (local)
const USE_FAKE_API = false

export async function processFinalSummary(chunks) {
  if (USE_FAKE_API) {
    // ------ MODO SIMULADO (local, sin backend) ------
    return generateFakeVideoSummary(chunks);
  } else {
    // ------ MODO REAL (backend conectado) ------
    // aquí llamas al endpoint real del backend
    return getSummary();
  }
}

export async function processChunk(blob) {
  if (USE_FAKE_API) {
    // no hacemos upload real en modo de desarrollo
    console.log("FAKE Mode: chunk simulado enviado.");
    return { ok: true };
  } else {
    return uploadChunk(blob); // ← API real FastAPI
  }
}


export async function uploadFullVideo(file, onProgress) {
  const useFake = USE_FAKE_API === true;
  // 🟣 SIMULACIÓN — Fake API activada
  if (useFake) {
    return new Promise((resolve) => {
      let percent = 0;

      const interval = setInterval(() => {
        percent += 10;     // 10% cada segundo
        onProgress(percent);

        if (percent >= 100) {
          clearInterval(interval);

          // pequeña pausa estética antes de devolver el resultado
          setTimeout(() => {
            resolve({
              overallSummary: "Procesado con FAKE API (simulación).",
              segmentSummaries: [
                "Segmento simulado A",
                "Segmento simulado B",
                "Segmento simulado C",
              ],
            });
          }, 500);
        }
      }, 1000); // ← total 10 segundos
    });
  }
 const uploadResponse = await new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const endpoint = `${import.meta.env.VITE_API_URL}/upload`;

    xhr.open("POST", endpoint);

    xhr.onload = () => {
      try {
        const data = JSON.parse(xhr.responseText);
        resolve(data);
      } catch (err) {
        reject(err);
      }
    };

    xhr.onerror = reject;

    const formData = new FormData();
    formData.append("file", file);
    xhr.send(formData);
  });

  const jobId = uploadResponse.job_id;
  console.log("📥 Upload completo. jobId =", jobId);

  async function pollSplitStatus() {
    const endpoint = `${import.meta.env.VITE_API_URL}/split/${jobId}`;

    const res = await fetch(endpoint);
    const data = await res.json();

    // 🔥 actualizar barra con split_pct
    if (typeof data.split_pct === "number") {
      onProgress(Math.floor(data.split_pct));
    }
    
    if (data.split_status === "completed") {
      console.log("✅ Split completado");
      return data;
    }

    // esperar un poco antes del siguiente fetch
    await new Promise((r) => setTimeout(r, 350));

    return pollSplitStatus();
  }

  // Esperar hasta que split diga "done"
  const final = await pollSplitStatus();

  // Preparamos un objeto compatible con tu ChatVideoInsights
  return {
    overallSummary: `Procesamiento completado (${final.completed_chunks}/${final.total_chunks} chunks).`,
    segmentSummaries: final.chunks,
  };
}