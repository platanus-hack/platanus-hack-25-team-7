// src/pages/ChatPage.jsx
import { useParams } from "react-router-dom";
import ChatVideoInsights from "../components/ChatVideoInsights";
import { useEffect, useState } from "react";
import { getAnalysis } from "../utils/apiAdapter";

export default function ChatPage() {
  const { jobId } = useParams();
  const [analysis, setAnalysis] = useState(null);

  useEffect(() => {
    getAnalysis(jobId).then(setAnalysis);
  }, [jobId]);

  if (!analysis) return <p>Cargando...</p>;

  return <ChatVideoInsights analysis={analysis} />;
}
