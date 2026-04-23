import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
# from sentence_transformers import SentenceTransformer
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()
def document_loader(docs_path="docs"):
    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"Directory '{docs_path}' does not exist.")
    loader = DirectoryLoader(
        path = docs_path,
        glob= "*.txt",
        loader_cls=TextLoader
    )
    documents = loader.load()
    if(len(documents) == 0):
        raise ValueError(f"No documents found in the directory '{docs_path}'. Please ensure it contains .txt files.")
    
    # for i, doc in enumerate(documents):
    #     print(f"\nDocument {i+1}:")
    #     print(f"Source: {doc.metadata['source']}")
    #     print(f"Content: {doc.page_content[:200]}...")  # Print the first 200 characters of the document content for verification
    #     print(f"Content Length: {len(doc.page_content)} characters")
    #     print(f"Metadata: {doc.metadata}")
    return documents

def split_documents(documents, chunk_size=800, chunk_overlap=100):
    """Split documents into smaller chunks with overlap"""
    print("Splitting documents into chunks...")
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    chunks = text_splitter.split_documents(documents)
    print(f"Total chunks created: {len(chunks)}")
    
    # if chunks:
    
    #     for i, chunk in enumerate(chunks[:5]):
    #         print(f"\n--- Chunk {i+1} ---")
    #         print(f"Source: {chunk.metadata['source']}")
    #         print(f"Length: {len(chunk.page_content)} characters")
    #         print(f"Content:")
    #         print(chunk.page_content)
    #         print("-" * 50)
        
    #     if len(chunks) > 5:
    #         print(f"\n... and {len(chunks) - 5} more chunks")
    
    return chunks
def create_vetor_store(chunks, persist_directory="db/chroma_db"):
    print("Creating vector store and embedding chunks...")
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    print("Creating ChromaDB vector store...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space": "cosine"}
    )
    print("finished creating vector store")

    print(f"Persisting vector store saved to {persist_directory}...")

    return vector_store

def main():
    print("Starting the ingestion pipeline...")
    # 1. Load documents from the specified directory
documents = document_loader(docs_path="docs") 
chunks = split_documents(documents=documents)
vector_store = create_vetor_store(chunks)
    # 2. Chunking the documents into smaller pieces
    # 3. Embedding and Storing the chunks in ChromaDB


if __name__ == "__main__":    
    
    main()