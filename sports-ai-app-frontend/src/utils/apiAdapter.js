
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

import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";

export async function uploadFullVideo(file) {
  const API = import.meta.env.VITE_API_URL;

  // === 1. Configurar cliente S3 ===
  const s3 = new S3Client({
    region: "us-east-1",
    credentials: {
      accessKeyId: import.meta.env.VITE_AWS_ACCESS_KEY,
      secretAccessKey: import.meta.env.VITE_AWS_SECRET_KEY,
    }
  });

  // === 2. Generar ruta del archivo ===
  const fileKey = `uploads/${Date.now()}_${file.name}`;
  const fixedFile = file instanceof File ? file : new File([file], file.name, { type: file.type });
  const bucket = "pvhack-media-012468946780-us-east-1";

  // === 3. Subir directo a S3 ===
  const uploadParams = {
    Bucket: bucket,
    Key: fileKey,
    Body: await fixedFile.arrayBuffer(),
    ContentType: file.type,
  };

  console.log("Uploading to S3:", uploadParams);

  await s3.send(new PutObjectCommand(uploadParams));

  console.log("Upload completed.");

  // === 4. Avisar a tu API ===
  const s3Path = `https://${bucket}.s3.amazonaws.com/${fileKey}`;

  const response = await fetch(`${API}/upload`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      fileKey,
      s3Path,
    })
  });
  console.log("API Response:", response);
  return response.json();
}


export async function pollSplitProgress(jobId, onProgress) {
  if (typeof onProgress !== "function") {
    console.error("pollSplitProgress: onProgress NO es función");
    onProgress = () => {};
  }

  async function loop() {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/split/${jobId}`);
    const data = await res.json();

    if (typeof data.split_pct === "number") {
      onProgress(Math.floor(data.split_pct));
    }

    if (data.split_status === "completed") {
      return data;
    }

    await new Promise((r) => setTimeout(r, 350));
    return loop();
  }

  return loop();
}


export async function getAnalysis(jobId) {
  console.log("Fetching analysis for jobId:", jobId, "from URL:", `${import.meta.env.VITE_API_URL}/analysis/${jobId}`);
  const res = await fetch(`${import.meta.env.VITE_API_URL}/analysis/${jobId}`);
  if (!res.ok) throw new Error("Error fetching analysis");
  return res.json();
}


export async function pollAnalysisProgress(jobId, onProgress) {
  async function loop() {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/analysis/${jobId}`);
    const data = await res.json();

    // actualiza progreso si existe un campo analysis_pct
    if (typeof data.analysis_pct === "number") {
      onProgress(Math.floor(data.analysis_pct));
    }

    // si el análisis terminó
    if (data.analysis_status !== "processing") {
      return data;
    }

    await new Promise((r) => setTimeout(r, 1000));
    return loop();
  }

  return loop();
}
