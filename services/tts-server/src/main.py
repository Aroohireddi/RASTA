import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from model import synthesize, load_model
from adapter import adapter_available, load_adapter, get_language_switch_positions
import time

app = FastAPI(title="RASTA TTS Server", version="1.0.0")

class SynthesizeInput(BaseModel):
    text: str
    tagged_tokens: list[dict] = []
    return_metadata: bool = True

class PipelineInput(BaseModel):
    original: str
    final_sentence: str
    tagged_tokens: list[dict] = []
    oov_tokens: list[str] = []

@app.on_event("startup")
def startup():
    print("[tts-server] Loading TTS model at startup...")
    load_model()
    print(f"[tts-server] Adapter available: {adapter_available()}")
    print("[tts-server] Ready.")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "tts-server",
        "adapter_loaded": adapter_available()
    }

@app.post("/synthesize")
def synthesize_endpoint(input: SynthesizeInput):
    """Synthesize text and return WAV audio."""
    if not input.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        wav_bytes, rtf, sample_rate = synthesize(input.text)
        switch_positions = get_language_switch_positions(input.tagged_tokens)

        if input.return_metadata:
            # Return metadata as header, audio as body
            return Response(
                content=wav_bytes,
                media_type="audio/wav",
                headers={
                    "X-RTF": str(rtf),
                    "X-Sample-Rate": str(sample_rate),
                    "X-Switch-Positions": str(len(switch_positions)),
                    "X-Text-Length": str(len(input.text))
                }
            )
        return Response(content=wav_bytes, media_type="audio/wav")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/synthesize/pipeline")
def synthesize_pipeline(input: PipelineInput):
    """
    Receive processed sentence from NLP pipeline and synthesize.
    Uses final_sentence (transliterated Telugu script).
    """
    text = input.final_sentence if input.final_sentence else input.original
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text to synthesize")

    try:
        wav_bytes, rtf, sample_rate = synthesize(text)
        switch_positions = get_language_switch_positions(input.tagged_tokens)

        return Response(
            content=wav_bytes,
            media_type="audio/wav",
            headers={
                "X-RTF": str(rtf),
                "X-Original": input.original[:100],
                "X-Switch-Count": str(len(switch_positions)),
                "X-OOV-Count": str(len(input.oov_tokens))
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model/info")
def model_info():
    from model import MODEL_NAME
    return {
        "model": MODEL_NAME,
        "adapter": adapter_available(),
        "language": "Telugu (tel)",
        "architecture": "VITS/MMS"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)