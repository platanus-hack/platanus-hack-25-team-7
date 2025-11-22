export default function ProcessingLoader({ text = "Procesando último segmento…" }) {
  return (
    <div style={{ padding: "40px", textAlign: "center" }}>
      <h2>{text}</h2>

      <div style={{
        margin: "30px auto",
        width: "80%",
        height: "12px",
        background: "#222",
        borderRadius: "10px",
        overflow: "hidden",
      }}>
        <div className="loading-bar" />
      </div>

      <style>{`
        .loading-bar {
          width: 0%;
          height: 100%;
          background: linear-gradient(90deg, #ff00ff, #ff77ff);
          animation: loadingMove 2.5s infinite;
        }
        @keyframes loadingMove {
          0% { width: 0%; }
          50% { width: 100%; }
          100% { width: 0%; }
        }
      `}</style>
    </div>
  );
}
