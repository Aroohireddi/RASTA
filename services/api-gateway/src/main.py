import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="RASTA API Gateway", version="1.0.0")

NLP_URL = os.getenv("NLP_URL", "http://localhost:8002")
TTS_URL = os.getenv("TTS_URL", "http://localhost:8004")
RAG_URL = os.getenv("RAG_URL", "http://localhost:8003")
INGESTOR_URL = os.getenv("INGESTOR_URL", "http://localhost:8001")
EVAL_URL = os.getenv("EVAL_URL", "http://localhost:8005")

class ArticleRequest(BaseModel):
    title: str
    summary: str
    source: str = "manual"

class TextRequest(BaseModel):
    text: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "api-gateway"}

@app.post("/process/article/audio")
async def process_article_to_audio(request: ArticleRequest):
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Step 1: NLP processing
        nlp_response = await client.post(f"{NLP_URL}/process/article", json={
            "title": request.title,
            "summary": request.summary,
            "source": request.source
        })
        if nlp_response.status_code != 200:
            raise HTTPException(status_code=500, detail="NLP pipeline failed")

        nlp_result = nlp_response.json()
        sentences = nlp_result.get("sentences", [])

        # If summariser returned nothing, process full text directly
        if not sentences:
            full_text = f"{request.title}. {request.summary}"
            nlp_response2 = await client.post(f"{NLP_URL}/process/sentence", json={
                "text": full_text,
                "source": request.source
            })
            if nlp_response2.status_code != 200:
                raise HTTPException(status_code=500, detail="No sentences extracted")
            sentence_result = nlp_response2.json()
            final_text = sentence_result.get("final_sentence", full_text)
            oov_tokens = sentence_result.get("oov_tokens", [])
        else:
            # Pick sentence with highest Telugu ratio
            best = max(sentences, key=lambda s: len([
                c for c in s["final"] if 0x0C00 <= ord(c) <= 0x0C7F
            ]))
            final_text = best["final"]
            oov_tokens = best.get("oov_tokens", [])

        if not final_text.strip():
            raise HTTPException(status_code=400, detail="No text to synthesize")

        # Step 2: RAG disambiguation
        if oov_tokens:
            await client.post(f"{RAG_URL}/disambiguate/batch", json={
                "tokens": oov_tokens
            })

        # Step 3: TTS synthesis
        tts_response = await client.post(f"{TTS_URL}/synthesize", json={
            "text": final_text,
            "tagged_tokens": [],
            "return_metadata": True
        })

        if tts_response.status_code != 200:
            raise HTTPException(status_code=500, 
                detail=f"TTS failed: {tts_response.text}")

        rtf = tts_response.headers.get("X-RTF", "unknown")

        return Response(
            content=tts_response.content,
            media_type="audio/wav",
            headers={
                "X-RTF": str(rtf),
                "X-Sentence": final_text[:100].encode("ascii", errors="replace").decode("ascii"),
                "X-OOV-Count": str(len(oov_tokens)),
                "X-Total-Sentences": str(len(sentences))
            }
        )

@app.get("/pipeline/status")
async def pipeline_status():
    """Check status of all services."""
    services = {
        "ingestor": f"{INGESTOR_URL}/health",
        "nlp-pipeline": f"{NLP_URL}/health",
        "rag-store": f"{RAG_URL}/health",
        "tts-server": f"{TTS_URL}/health",
        "eval-service": f"{EVAL_URL}/health"
    }
    status = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in services.items():
            try:
                r = await client.get(url)
                status[name] = "up" if r.status_code == 200 else "error"
            except Exception:
                status[name] = "down"
    return {"services": status}

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
    <head><title>RASTA - Telugu-English TTS Accessibility</title></head>
    <body style="font-family:Arial;padding:20px;background:#1a1a2e;color:#eee">
        <h1 style="color:#e94560">RASTA 🎙️</h1>
        <p>Real-Time Retrieval-Augmented Speech Accessibility System</p>
        <p>Telugu-English Code-Mixed TTS Pipeline</p>
        <ul>
            <li><a href="/docs" style="color:#0f3460">API Documentation</a></li>
            <li><a href="/pipeline/status" style="color:#0f3460">Pipeline Status</a></li>
        </ul>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)