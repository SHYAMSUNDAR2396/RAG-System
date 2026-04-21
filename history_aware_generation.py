from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

load_dotenv()

persist_directory = "db/chroma_db"
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)
db = Chroma(
    persist_directory=persist_directory,
    embedding_function=embedding_model,
    # collection_metadata={"hnsw:space": "cosine"}
)
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
chat_history = []
def ask_question(user_questions):
    print(f"You Asked: {user_questions}")
    if chat_history:
        message =[
             SystemMessage(content="Given the following conversation history and the new question, please provide a concise and accurate answer based on the information from the documents. If the documents do not contain enough information to answer the question, please indicate that as well.")
        ]+ chat_history + [
            HumanMessage(content=user_questions)
        ]
    else:
        message = [
            SystemMessage(content="You are a helpful assistant that answers questions based on the provided documents. Please provide concise and accurate answers based on the information from the documents. If the documents do not contain enough information to answer the question, please indicate that as well."),
            HumanMessage(content=user_questions)
        ]
    retriever = db.as_retriever(search_kwargs={"k": 5})
    docs = retriever.invoke(user_questions)
    for i,doc in enumerate(docs):
        lines = doc.page_content.splitlines()
        preview = "\n".join(lines)
        print(f"Document {i} Preview:\n{preview}\n")
    combined_input = f"""Answer the question based on the following documents, please answer this question: {user_questions}
        Documents:
        {chr(10).join([f"document {i}: {doc.page_content}" for i, doc in enumerate(docs)])}
        please provide a concise and accurate answer based on the information from the documents. If the documents do not contain enough information to answer the question, please indicate that as well.
        """
    messages = [
        SystemMessage(content="You are a helpful assistant that answers questions based on the provided documents. Please provide concise and accurate answers based on the information from the documents. If the documents do not contain enough information to answer the question, please indicate that as well.")
    ] + chat_history + [
        HumanMessage(content=combined_input)
    ]
    result = model.invoke(messages)
    answer = result.content
    chat_history.append(HumanMessage(content=user_questions))
    chat_history.append(SystemMessage(content=answer))
    print(f"Answer: {answer}")
    return answer

def start_chat():
        print("Ask me questions ! Type 'exit' to end the chat.")
        while True:
            question= input("Your Question: ")
            if question.lower() == "exit":
                print("Chat ended. Goodbye!")
                break
            ask_question(question)
if __name__ == "__main__":
    start_chat()