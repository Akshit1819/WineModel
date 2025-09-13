🍷 Napa Valley Wine Concierge

An AI-powered conversational assistant for a Napa Valley wine business.
The agent can:
✅ Answer questions from business documents
✅ Provide real-time weather updates
✅ Perform web searches for wine-related events and news
✅ Offer a beautiful React-based UI for direct interaction

🚀 Features

Document Q&A – Upload business docs (PDF, text) and ask questions

Weather Tool – Get live weather updates (powered by OpenWeather API)

Web Search – Stay updated on events, festivals, and news

Conversational AI – Built with LangGraph + Groq LLM

Frontend UI – React + Vite, styled with Tailwind CSS

git clone https://github.com/<your-username>/wine-concierge.git
cd wine-concierge

GROQ_API_KEY=your_groq_api_key
OPENWEATHERMAP_API_KEY=your_openweather_api_key

python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000

➡ Backend runs at http://127.0.0.1:8000
➡ Frontend runs at http://127.0.0.1:5173

🎥 Demo Video

Watch the video in repositorie

🛠️ Tech Stack

Backend: FastAPI, LangGraph, Groq LLM, HuggingFace Embeddings, FAISS

Frontend: React, Vite, TailwindCSS

APIs: DuckDuckGo Search, OpenWeatherMap

Docs: PDF ingestion via pypdf
