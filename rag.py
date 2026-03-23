"""Dagster GraphQL RAG Chatbot - Answers questions using Dagster docs."""

import os
from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# --- Config ---
DOCS_DIR = Path(__file__).parent / "docs"
QDRANT_PATH = Path(__file__).parent / ".qdrant_store"
COLLECTION_NAME = "dagster_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
CHUNK_SIZE = 800
CHUNK_OVERLAP = 200
TOP_K = 4

SYSTEM_PROMPT = """You are a helpful Dagster expert assistant. Answer questions about Dagster's GraphQL API, Python client, and MCP server using ONLY the provided context. If the context doesn't contain enough information, say so honestly.

Context:
{context}"""


def load_docs(docs_dir: Path) -> list:
    """Load all markdown files from the docs directory."""
    loader = DirectoryLoader(
        str(docs_dir), glob="**/*.md", loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    return loader.load()


def build_vector_store(docs: list) -> QdrantVectorStore:
    """Split documents, embed, and store in Qdrant."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(docs)
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    store = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        path=str(QDRANT_PATH),
        collection_name=COLLECTION_NAME,
        force_recreate=True,
    )
    print(f"✓ Indexed {len(chunks)} chunks into Qdrant")
    return store


def load_vector_store() -> QdrantVectorStore:
    """Load existing Qdrant store from disk."""
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        path=str(QDRANT_PATH),
        collection_name=COLLECTION_NAME,
    )


def get_chain(vector_store: QdrantVectorStore):
    """Build the RAG chain: retriever → prompt → LLM → output."""
    retriever = vector_store.as_retriever(search_kwargs={"k": TOP_K})
    llm = ChatOllama(model=LLM_MODEL)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}"),
    ])

    def format_docs(docs):
        return "\n\n---\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


def main():
    """Interactive chatbot loop."""
    print("=" * 60)
    print("  Dagster GraphQL RAG Chatbot")
    print("=" * 60)

    # Build or load vector store
    if QDRANT_PATH.exists():
        print("Loading existing index...")
        store = load_vector_store()
        print("✓ Index loaded")
    else:
        print("Building index from docs...")
        docs = load_docs(DOCS_DIR)
        if not docs:
            print("✗ No docs found in", DOCS_DIR)
            return
        store = build_vector_store(docs)

    chain = get_chain(store)

    print(f"\nUsing model: {LLM_MODEL}")
    print("Type 'quit' to exit, 'rebuild' to re-index docs.\n")

    while True:
        question = input("You: ").strip()
        if not question:
            continue
        if question.lower() == "quit":
            print("Goodbye!")
            break
        if question.lower() == "rebuild":
            print("Rebuilding index...")
            docs = load_docs(DOCS_DIR)
            store = build_vector_store(docs)
            chain = get_chain(store)
            continue

        try:
            answer = chain.invoke(question)
            print(f"\nAssistant: {answer}\n")
        except Exception as e:
            print(f"\n✗ Error: {e}\n")


if __name__ == "__main__":
    main()
