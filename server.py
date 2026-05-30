import time
import logging
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from multi_agent import coordinator

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class Question(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(body: Question):
    start = time.time()
    answer = coordinator(body.question)
    duration = round((time.time() - start) * 1000)
    logging.info(f"question={body.question!r} duration={duration}ms")
    return {"answer": answer, "duration_ms": duration}


# ── OpenAI-compatible endpoint ────────────────────────────────────────────────
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: Optional[str] = "multi-agent-devops"
    messages: List[ChatMessage]

@app.post("/v1/chat/completions")
def chat_completions(body: ChatRequest):
    question = body.messages[-1].content
    start = time.time()
    answer = coordinator(question)
    duration = round((time.time() - start) * 1000)
    logging.info(f"openai-compat question={question!r} duration={duration}ms")
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
        "object": "chat.completion",
        "model": "multi-agent-devops",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": answer},
            "finish_reason": "stop"
        }]
    }

@app.get("/v1/models")
def list_models():
    return {"data": [{"id": "multi-agent-devops", "object": "model"}]}
