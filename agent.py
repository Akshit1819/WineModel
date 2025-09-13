# agent.py
import os
import requests
from typing import TypedDict
from dotenv import load_dotenv

from langgraph.graph import StateGraph
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from duckduckgo_search import DDGS

load_dotenv()

# --- LLM (Groq) ---
llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # Groq supported model
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY"),
)

# --- Embeddings ---
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# --- Globals for retriever and QA chain ---
doc_qa = None
retriever = None

def update_retriever(index_path: str = "wine_docs_index"):
    """
    Reload FAISS retriever and update doc_qa globally.
    """
    global retriever, doc_qa
    if os.path.exists(index_path):
        vectorstore = FAISS.load_local(
            index_path,
            embeddings,
            allow_dangerous_deserialization=True,
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
        doc_qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    else:
        retriever = None
        doc_qa = None

# Load retriever on startup
update_retriever()

# --- DuckDuckGo Web Search ---
def duckduckgo_search(query: str) -> str:
    try:
        with DDGS() as ddgs:
            results = [f"{r['title']}: {r['body']} ({r['href']})"
                       for r in ddgs.text(query, max_results=3)]
        return "\n\n".join(results) if results else "⚠️ No results found."
    except Exception as e:
        return f"⚠️ Web search failed: {str(e)}"

# --- Weather API ---
def weather_tool(location: str = "Napa Valley") -> str:
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        return "⚠️ No OpenWeather API key set."
    try:
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {"q": location, "appid": api_key, "units": "metric"}
        resp = requests.get(url, params=params, timeout=8)
        data = resp.json()
        if "weather" in data:
            desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            feels = data["main"]["feels_like"]
            return f"Weather in {location}: {desc}, {temp}°C (feels like {feels}°C)"
        return f"⚠️ Couldn’t fetch weather: {data.get('message', 'unknown error')}"
    except Exception as e:
        return f"⚠️ Weather fetch failed: {str(e)}"

# --- Graph State Schema ---
class GraphState(TypedDict):
    query: str
    answer: str
    response: str
    location: str

# --- LangGraph ---
graph = StateGraph(GraphState)

# --- Business docs node ---
def business_docs_answer(state: GraphState):
    if not doc_qa:
        return {"answer": "⚠️ No wine business documents uploaded yet. Please upload files via /upload."}
    try:
        result = doc_qa.run(state["query"])  # safer than .invoke
        return {"answer": result}
    except Exception as e:
        return {"answer": f"⚠️ QA chain failed: {str(e)}"}

# --- Nodes ---
graph.add_node("business_docs", business_docs_answer)
graph.add_node("web_search", lambda s: {"answer": duckduckgo_search(s["query"])})
graph.add_node("weather", lambda s: {"answer": weather_tool(s.get("location", "Napa Valley"))})
graph.add_node("final", lambda s: {"response": s["answer"]})

# --- Router ---
def router(state: GraphState) -> str:
    q = state["query"].lower()
    if any(word in q for word in ["weather", "temperature", "forecast", "climate"]):
        return "weather"
    elif any(word in q for word in ["festival", "news", "review", "event"]):
        return "web_search"
    else:
        return "business_docs"

graph.add_node("start", lambda s: s)
graph.add_conditional_edges("start", router, {
    "business_docs": "business_docs",
    "web_search": "web_search",
    "weather": "weather",
})

graph.add_edge("business_docs", "final")
graph.add_edge("web_search", "final")
graph.add_edge("weather", "final")

graph.set_entry_point("start")

# --- Compile agent ---
agent_executor = graph.compile()
