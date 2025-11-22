// src/pages/Analysis.jsx
import { useEffect, useState } from "react";
import { checkAnalysis } from "../utils/api";

export default function Analysis({ jobId }) {
  const [status, setStatus] = useState("Processing...");
  const [result, setResult] = useState(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      const res = await checkAnalysis(jobId);

      if (res.status === "done") {
        setResult(res.data);
        setStatus("Complete");
        clearInterval(interval);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId]);

  return (
    <div>
      <h1>{status}</h1>
      {result && (
        <pre>{JSON.stringify(result, null, 2)}</pre>
      )}
    </div>
  );
}
