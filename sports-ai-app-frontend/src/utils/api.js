// src/utils/api.js
export async function uploadVideo(blob) {
  const formData = new FormData();
  formData.append("file", blob);

  return fetch(`${import.meta.env.VITE_API_URL}/upload`, {
    method: "POST",
    body: formData,
  }).then(res => res.json());
}

export async function checkAnalysis(id) {
  return fetch(`${import.meta.env.VITE_API_URL}/analysis/${id}`)
    .then(res => res.json());
}

export async function uploadChunk(blob) {
  const formData = new FormData();
  formData.append("chunk", blob);

  return fetch(`${import.meta.env.VITE_API_URL}/upload_chunk`, {
    method: "POST",
    body: formData
  }).then(res => res.json());
}

export function getSummary() {
  return fetch(`${import.meta.env.VITE_API_URL}/final_summary`)
    .then(res => res.json());
}

export async function askAgent(question) {
  const url = new URL(`${import.meta.env.VITE_API_URL}/agent/`);
  url.searchParams.append("question", question);
  
  return fetch(url)
    .then(res => res.json())
    .then(data => data.response);
}
