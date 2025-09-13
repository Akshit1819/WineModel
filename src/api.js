// frontend/src/api.js
import axios from "axios";

// Base URL for your FastAPI backend
const API_BASE = "http://127.0.0.1:8000";

// Ask the concierge (wine Q&A, business docs, web search)
export const askConcierge = async (query) => {
  try {
    const res = await axios.post(`${API_BASE}/ask`, { query });
    return res.data.response;
  } catch (err) {
    console.error("Ask Concierge Error:", err);
    return "⚠️ Failed to reach concierge service.";
  }
};

// Get weather info from backend (which calls OpenWeatherMap)
export const getWeather = async (location) => {
  try {
    const res = await axios.get(`${API_BASE}/weather`, {
      params: { location },
    });
    return res.data.response;
  } catch (err) {
    console.error("Weather Error:", err);
    return "⚠️ Weather service unavailable.";
  }
};

// Upload new PDF or TXT document to the backend
export const uploadDocument = async (file) => {
  try {
    const formData = new FormData();
    formData.append("file", file);

    const res = await axios.post(`${API_BASE}/upload`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data.response;
  } catch (err) {
    console.error("Upload Error:", err);
    return "⚠️ Upload failed.";
  }
};
