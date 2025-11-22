
import { generateFakeVideoSummary } from "./fakeVideoAnalysis";
import { uploadChunk, getSummary } from "./api";

// El backend REAL trabaja chunk por chunk → (FastAPI)
// La simulación trabaja con todos los blobs → (local)
const USE_FAKE_API = true

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
