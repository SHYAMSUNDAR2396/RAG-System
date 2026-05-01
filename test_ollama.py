import asyncio
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

async def main():
    llm = ChatOllama(model="llama3", base_url="http://127.0.0.1:11434")
    print("Starting stream...")
    async for chunk in llm.astream([HumanMessage(content="Hello!")]):
        print(repr(chunk.content), end="", flush=True)
    print("\nDone!")

asyncio.run(main())
