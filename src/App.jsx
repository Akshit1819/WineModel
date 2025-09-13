// frontend/src/App.jsx
import { useState } from "react";
import { askConcierge, uploadDocument } from "./api";

export default function App() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [mode, setMode] = useState("business"); // business | web | weather
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [uploadMsg, setUploadMsg] = useState("");

  const handleAsk = async () => {
    if (!query.trim() && mode !== "weather") {
      setResponse("⚠️ Please enter a question.");
      return;
    }
    setLoading(true);
    try {
      const formattedQuery =
        mode === "weather"
          ? "weather"
          : mode === "web"
          ? query + " (search online)"
          : query;

      const res = await askConcierge(formattedQuery);
      setResponse(res);
    } catch (err) {
      console.error(err);
      setResponse("⚠️ Something went wrong.");
    }
    setLoading(false);
  };

  const handleUpload = async () => {
    if (!file) {
      setUploadMsg("⚠️ Please select a file first.");
      return;
    }
    setUploadMsg("⏳ Uploading...");
    try {
      const res = await uploadDocument(file);
      setUploadMsg(res);
    } catch (err) {
      console.error(err);
      setUploadMsg("⚠️ Upload failed.");
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #3b0a45, #7b113a)",
        color: "#fff",
        fontFamily: "'Poppins', sans-serif",
        padding: "2rem",
      }}
    >
      <h1 style={{ textAlign: "center", fontSize: "2.5rem", marginBottom: "1rem" }}>
        🍷 Napa Valley Wine Concierge
      </h1>

      {/* Mode Selection */}
      <div style={{ display: "flex", justifyContent: "center", gap: "1rem", marginBottom: "1rem" }}>
        <button
          onClick={() => setMode("business")}
          style={{
            background: mode === "business" ? "#e63946" : "#444",
            padding: "0.7rem 1.5rem",
            border: "none",
            borderRadius: "8px",
            color: "white",
            cursor: "pointer",
          }}
        >
          📖 Ask Business
        </button>
        <button
          onClick={() => setMode("web")}
          style={{
            background: mode === "web" ? "#e63946" : "#444",
            padding: "0.7rem 1.5rem",
            border: "none",
            borderRadius: "8px",
            color: "white",
            cursor: "pointer",
          }}
        >
          🌍 Search Web
        </button>
        <button
          onClick={() => setMode("weather")}
          style={{
            background: mode === "weather" ? "#e63946" : "#444",
            padding: "0.7rem 1.5rem",
            border: "none",
            borderRadius: "8px",
            color: "white",
            cursor: "pointer",
          }}
        >
          ☀️ Get Weather
        </button>
      </div>

      {/* Input */}
      {mode !== "weather" && (
        <input
          type="text"
          placeholder="Type your question here..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{
            width: "100%",
            maxWidth: "600px",
            margin: "0 auto",
            display: "block",
            padding: "0.8rem",
            borderRadius: "8px",
            border: "none",
            fontSize: "1rem",
          }}
        />
      )}

      {/* Ask Button */}
      <div style={{ textAlign: "center", marginTop: "1rem" }}>
        <button
          onClick={handleAsk}
          style={{
            background: "#e63946",
            padding: "0.8rem 2rem",
            border: "none",
            borderRadius: "10px",
            color: "white",
            fontSize: "1.1rem",
            cursor: "pointer",
            boxShadow: "0 4px 10px rgba(0,0,0,0.3)",
          }}
        >
          {loading ? "⏳ Thinking..." : "Ask"}
        </button>
      </div>

      {/* Response */}
      {response && (
        <div
          style={{
            marginTop: "2rem",
            background: "rgba(255, 255, 255, 0.1)",
            padding: "1.5rem",
            borderRadius: "12px",
            maxWidth: "700px",
            marginLeft: "auto",
            marginRight: "auto",
            whiteSpace: "pre-line",
          }}
        >
          <strong>Concierge:</strong> {response}
        </div>
      )}

      {/* Upload Section */}
      <div
        style={{
          marginTop: "3rem",
          padding: "1.5rem",
          background: "rgba(0,0,0,0.3)",
          borderRadius: "12px",
          maxWidth: "600px",
          margin: "2rem auto",
          textAlign: "center",
        }}
      >
        <h2>📤 Upload Wine Document</h2>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          style={{ margin: "1rem 0" }}
        />
        <br />
        <button
          onClick={handleUpload}
          style={{
            background: "#06d6a0",
            padding: "0.6rem 1.5rem",
            border: "none",
            borderRadius: "8px",
            color: "white",
            fontSize: "1rem",
            cursor: "pointer",
          }}
        >
          Upload
        </button>
        {uploadMsg && <p style={{ marginTop: "1rem" }}>{uploadMsg}</p>}
      </div>
    </div>
  );
}
