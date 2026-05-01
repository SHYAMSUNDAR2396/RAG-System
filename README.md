# 🔍 RAG — Semantic Document Retrieval System

A comprehensive **Retrieval-Augmented Generation (RAG)** system that demonstrates the full pipeline from document ingestion to answer generation. This project explores multiple chunking strategies, retrieval methods, re-ranking techniques, and LLM-powered answer generation using LangChain, ChromaDB, and Google Gemini.

---

## 📐 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        DOCUMENT SOURCES                        │
│   docs/Google.txt · Microsoft.txt · Nvidia.txt · SpaceX.txt    │
│   docs/Tesla.txt · docs/attention-is-all-you-need.pdf          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
           ┌───────────────▼───────────────┐
           │     1. CHUNKING STRATEGIES     │
           │  ┌───────────────────────────┐ │
           │  │ Recursive Character Split │◄├── recursive_character_text_spliiter.py
           │  │ Semantic Chunking         │◄├── semantic_chunking.py
           │  │ Agentic Chunking (LLM)    │◄├── agentic_chunking.py
           │  └───────────────────────────┘ │
           └───────────────┬───────────────┘
                           │
           ┌───────────────▼───────────────┐
           │    2. INGESTION PIPELINE       │
           │  Load → Split → Embed → Store │◄── ingetion_pipeline.py
           │  (PDF pipeline)               │◄── multi_model_rag.ipynb
           └───────────────┬───────────────┘
                           │
                    ┌──────▼──────┐
                    │  ChromaDB   │
                    │  Vector DB  │
                    │  (db/ dbv1/)│
                    └──────┬──────┘
                           │
           ┌───────────────▼───────────────┐
           │     3. RETRIEVAL METHODS       │
           │  ┌───────────────────────────┐ │
           │  │ Similarity Search         │ │
           │  │ Score Threshold           │◄├── retrieval_methods.py
           │  │ MMR (Max Marginal Relev.) │ │
           │  ├───────────────────────────┤ │
           │  │ Multi-Query Retrieval     │◄├── multi_query_retrieval.py
           │  │ Reciprocal Rank Fusion    │◄├── reciprocal_rank_fusion.py
           │  │ Hybrid Search (BM25+Vec)  │◄├── hybrid_search.ipynb
           │  └───────────────────────────┘ │
           └───────────────┬───────────────┘
                           │
           ┌───────────────▼───────────────┐
           │      4. RE-RANKING             │
           │  Cohere Rerank v3             │◄── reranker.ipynb
           └───────────────┬───────────────┘
                           │
           ┌───────────────▼───────────────┐
           │    5. ANSWER GENERATION        │
           │  ┌───────────────────────────┐ │
           │  │ Single-turn QA            │◄├── answer_generation.py
           │  │ Interactive Retrieval QA  │◄├── retrieval_pipeline.py
           │  │ History-Aware Chat        │◄├── history_aware_generation.py
           │  └───────────────────────────┘ │
           └───────────────────────────────┘
```

---

## 🗂 Project Structure

```
RAG/
├── docs/                                  # Source documents
│   ├── Google.txt
│   ├── Microsoft.txt
│   ├── Nvidia.txt
│   ├── SpaceX.txt
│   ├── Tesla.txt
│   └── attention-is-all-you-need.pdf
│
├── db/chroma_db/                          # Vector store (text docs)
├── dbv1/chroma_db/                        # Vector store (PDF pipeline)
│
├── recursive_character_text_spliiter.py   # Chunking strategy 1
├── semantic_chunking.py                   # Chunking strategy 2
├── agentic_chunking.py                    # Chunking strategy 3
│
├── ingetion_pipeline.py                   # Text document ingestion
├── multi_model_rag.ipynb                  # PDF ingestion + multimodal RAG
│
├── retrieval_methods.py                   # Basic retrieval strategies
├── multi_query_retrieval.py               # LLM-generated query variations
├── reciprocal_rank_fusion.py              # RRF scoring across queries
├── hybrid_search.ipynb                    # BM25 + vector hybrid search
├── reranker.ipynb                         # Cohere reranking pipeline
│
├── answer_generation.py                   # Single-turn RAG answer
├── retrieval_pipeline.py                  # Interactive retrieval + QA
├── history_aware_generation.py            # Multi-turn conversational RAG
│
├── chunks_export.json                     # Exported chunk data
├── rag_results.json                       # Sample RAG query results
├── .env                                   # API keys (GOOGLE_API_KEY, etc.)
└── requirements.txt                       # (optional) Python dependencies
```

---

## ⚙️ Setup

### Prerequisites

- Python 3.10+
- A [Google AI Studio](https://aistudio.google.com/) API key (for Gemini)
- (Optional) [Cohere](https://cohere.com/) API key for reranking

### Installation

```bash
# Clone the repository
git clone <repo-url> && cd RAG

# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install langchain langchain-community langchain-chroma langchain-huggingface \
            langchain-google-genai langchain-experimental langchain-classic \
            chromadb sentence-transformers python-dotenv pydantic rank_bm25

# For PDF processing (multi_model_rag.ipynb)
brew install poppler tesseract libmagic        # macOS
pip install "unstructured[all-docs]"

# For reranking (reranker.ipynb)
pip install langchain_cohere
```

### Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key_here
COHERE_API_KEY=your_cohere_api_key_here    # optional, for reranker
```

---

## 📖 File-by-File Walkthrough

👉 **See [WALKTHROUGH.md](WALKTHROUGH.md) for detailed documentation of every file.**

Quick overview:

| Phase | File | Purpose |
|-------|------|---------|
| **Chunking** | `recursive_character_text_spliiter.py` | Recursive separator-based splitting |
| | `semantic_chunking.py` | Embedding-similarity-based splitting |
| | `agentic_chunking.py` | LLM-driven topic-boundary splitting |
| **Ingestion** | `ingetion_pipeline.py` | Text docs → ChromaDB pipeline |
| | `multi_model_rag.ipynb` | PDF parsing + multimodal RAG |
| **Retrieval** | `retrieval_methods.py` | Similarity / Threshold / MMR strategies |
| | `multi_query_retrieval.py` | LLM-generated query variations |
| | `reciprocal_rank_fusion.py` | RRF scoring across multiple queries |
| | `hybrid_search.ipynb` | BM25 + vector hybrid search |
| **Re-Ranking** | `reranker.ipynb` | Cohere cross-encoder reranking |
| **Generation** | `answer_generation.py` | Single-turn RAG QA |
| | `retrieval_pipeline.py` | Interactive retrieval + QA |
| | `history_aware_generation.py` | Multi-turn conversational RAG |

---

## 🔄 Recommended Workflow

For a complete end-to-end run:

```bash
# 1. Ingest documents into ChromaDB
python ingetion_pipeline.py

# 2. Try different retrieval methods
python retrieval_methods.py

# 3. Run multi-query + RRF
python reciprocal_rank_fusion.py

# 4. Interactive Q&A
python retrieval_pipeline.py

# 5. Conversational Q&A
python history_aware_generation.py
```

For notebook workflows, run in Jupyter:
1. `multi_model_rag.ipynb` — PDF ingestion pipeline
2. `hybrid_search.ipynb` — Hybrid retrieval experiments
3. `reranker.ipynb` — Reranking with Cohere

---

## 🧰 Tech Stack

| Component | Technology |
|-----------|-----------|
| **LLM** | Google Gemini 2.5 Flash-Lite (via `langchain-google-genai`) |
| **Embeddings** | HuggingFace `all-MiniLM-L6-v2` (384-dim) |
| **Vector Store** | ChromaDB (cosine similarity) |
| **Keyword Search** | BM25 (via `rank_bm25`) |
| **Reranking** | Cohere Rerank v3 |
| **PDF Parsing** | Unstructured (`hi_res` strategy) |
| **Framework** | LangChain |

---

## 📝 Sample Queries

These queries work well against the included `docs/` dataset:

- *"What was NVIDIA's first graphics accelerator called?"*
- *"Which company did NVIDIA acquire to enter the mobile processor market?"*
- *"How much did Microsoft pay to acquire GitHub?"*
- *"In what year did Tesla begin production of the Roadster?"*
- *"What was the name of the autonomous spaceport drone ship?"*

---

## ⚠️ Common Issues

| Issue | Fix |
|-------|-----|
| `ChatGoogleGenerativeAI has no attribute 'embed_documents'` | Use `GoogleGenerativeAIEmbeddings` for embeddings, not `ChatGoogleGenerativeAI` (chat model ≠ embedding model) |
| `RateLimitError: 429 insufficient_quota` | Your OpenAI/Gemini API quota is exhausted. Check billing or wait for quota reset |
| `Cannot find module langchain.retrievers` | Use `langchain_community.retrievers` instead — modules were reorganized in LangChain v0.2+ |
| ChromaDB `No such file or directory` | Run `ingetion_pipeline.py` first to create the vector store |

---

## 📄 License

This project is for educational purposes.