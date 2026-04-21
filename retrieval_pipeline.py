import logging
import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

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

relevant_docs = retriever.invoke(query)
print(f"user query: {query}")
print("----- Context -----")
for i, doc in enumerate(relevant_docs):
    print(f"Document {i}: {doc.page_content}\n")

combined_input = f"""Answer the question based on the following documents, please answer this question: {query}
Documents: 
{chr(10).join([f"document {i}: {doc.page_content}" for i, doc in enumerate(relevant_docs)])}
please provide a concise and accurate answer based on the information from the documents. If the documents do not contain enough information to answer the question, please indicate that as well.
"""
print("----- Combined Input -----")
print(combined_input)
# model_name = os.getenv("GEMINI_MODEL", "Gemini 2.5 Flash-Lite")
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
messages = [
    SystemMessage(content="You are a helpful assistant that answers questions based on the provided documents. Please provide concise and accurate answers based on the information from the documents. If the documents do not contain enough information to answer the question, please indicate that as well."),
    HumanMessage(content=combined_input)
]
print("----- Answer -----")
try:
    result = model.invoke(messages)
    print(result.content)
except Exception as exc:
    error_text = str(exc)
    if "RESOURCE_EXHAUSTED" in error_text or "429" in error_text or "quota" in error_text.lower():
        print(
            "Gemini API quota is exhausted or unavailable for this project. "
            "Set billing/quotas in Google AI Studio, wait for quota reset, "
            "or use another API key/model via GEMINI_MODEL."
        )
        if relevant_docs:
            print("Fallback answer from top retrieved context:")
            print(relevant_docs[0].page_content.splitlines()[0])
    else:
        raise

    # Synthetic Questions: 

# 1. "What was NVIDIA's first graphics accelerator called?"
# 2. "Which company did NVIDIA acquire to enter the mobile processor market?"
# 3. "What was Microsoft's first hardware product release?"
# 4. "How much did Microsoft pay to acquire GitHub?"
# 5. "In what year did Tesla begin production of the Roadster?"
# 6. "Who succeeded Ze'ev Drori as CEO in October 2008?"
# 7. "What was the name of the autonomous spaceport drone ship that achieved the first successful sea landing?"
# 8. "What was the original name of Microsoft before it became Microsoft?"