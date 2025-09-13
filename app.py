import os
import shutil
import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import agent
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader

load_dotenv()

app = FastAPI(title="🍷 Wine Concierge API (Groq-powered)")

# ✅ Enable CORS so frontend (React) can call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INDEX_PATH = "wine_docs_index"
DOCS_PATH = "wine_docs"


# --- Utility: rebuild FAISS index ---
def rebuild_index():
    """Rebuild the FAISS index from all .txt and .pdf files in DOCS_PATH."""
    if not os.path.exists(DOCS_PATH):
        os.makedirs(DOCS_PATH)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    docs = []

    for file in os.listdir(DOCS_PATH):
        file_path = os.path.join(DOCS_PATH, file)
        if file.endswith(".txt"):
            loader = TextLoader(file_path)
            docs.extend(loader.load())
        elif file.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            docs.extend(loader.load())

    if not docs:
        return None

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    db = FAISS.from_documents(chunks, embeddings)
    db.save_local(INDEX_PATH)
    return db


# --- Root endpoint ---
@app.get("/")
def root():
    return {"response": "🍷 Wine Concierge API is running with Groq!"}


# --- Ask endpoint ---
@app.post("/ask")
async def ask(payload: dict):
    """
    Handle user queries and always return clean format:
    { "response": "..." }
    """
    try:
        query = payload.get("query", "").strip()
        location = payload.get("location", "Napa Valley")

        if not query:
            return {"response": "⚠️ Please provide a question."}

        result = agent.agent_executor.invoke({"query": query, "location": location})

        # If agent returns structured response, normalize to string
        if isinstance(result, dict):
            text = result.get("response") or result.get("result") or str(result)
        else:
            text = str(result)

        return {"response": text}

    except Exception as e:
        return JSONResponse(status_code=500, content={"response": f"⚠️ {str(e)}"})


# --- Upload endpoint ---
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a new .txt or .pdf document and rebuild the FAISS index.
    """
    try:
        if not os.path.exists(DOCS_PATH):
            os.makedirs(DOCS_PATH)

        file_path = os.path.join(DOCS_PATH, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Rebuild index after upload
        rebuild_index()
        agent.update_retriever(INDEX_PATH)

        return {"response": f"✅ {file.filename} uploaded and index updated."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"response": f"⚠️ {str(e)}"})


# --- Weather endpoint ---
@app.get("/weather")
def get_weather(location: str = "Napa Valley"):
    """
    Fetch real-time weather for given location.
    Example: /weather?location=Paris
    """
    try:
        from agent import weather_tool
        result = weather_tool(location)
        return {"response": result}
    except Exception as e:
        return {"response": f"⚠️ Weather error: {str(e)}"}


# --- Run server ---
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
