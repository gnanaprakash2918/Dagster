"""FastAPI server exposing the RAG chatbot as API + serving the web UI."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path

from rag import DOCS_DIR, QDRANT_PATH, load_docs, build_vector_store, load_vector_store, get_chain

app = FastAPI(title="Dagster RAG Chatbot")

# --- Init RAG chain at startup ---
_chain = None


def _get_chain():
    global _chain
    if _chain is not None:
        return _chain
    if QDRANT_PATH.exists():
        store = load_vector_store()
    else:
        docs = load_docs(DOCS_DIR)
        store = build_vector_store(docs)
    _chain = get_chain(store)
    return _chain


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    chain = _get_chain()
    answer = chain.invoke(req.question)
    return ChatResponse(answer=answer)


@app.post("/api/rebuild")
async def rebuild():
    global _chain
    docs = load_docs(DOCS_DIR)
    store = build_vector_store(docs)
    _chain = get_chain(store)
    return {"status": "ok", "message": "Index rebuilt"}


# Serve static files and SPA fallback
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root():
    return FileResponse(str(STATIC_DIR / "index.html"))
