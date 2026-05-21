import time
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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
