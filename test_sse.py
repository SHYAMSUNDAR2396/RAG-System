from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse
import uvicorn
import asyncio
from pydantic import BaseModel

app = FastAPI()

class ChatEvent(BaseModel):
    token: str

async def generate():
    yield f"data: {ChatEvent(token='A').model_dump_json()}\n\n"
    yield f"data: {ChatEvent(token='B').model_dump_json()}\n\n"
    yield ChatEvent(token='C').model_dump_json()

@app.get("/stream")
def stream():
    return EventSourceResponse(generate())

if __name__ == "__main__":
    uvicorn.run(app, port=8001)
