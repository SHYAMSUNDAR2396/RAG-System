import logging

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

persist_directory = "db/chroma_db"
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)
db = Chroma(
    # collection_name="documents",
    embedding_function=embedding_model,
    persist_directory=persist_directory,
    collection_metadata={"hnsw:space": "cosine"}
)
query = "What was NVIDIA's first graphics accelerator called?"

retriever = db.as_retriever(search_kwargs={"k": 5})

relevent_docs = retriever.invoke(query)
print(f"user query: {query}")
print("----- Context -----")
for i, doc in enumerate(relevent_docs):
    print(f"Document {i}: {doc.page_content}\n")
