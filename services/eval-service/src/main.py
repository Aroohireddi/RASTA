import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from pydantic import BaseModel
from asr import transcribe, compute_cer
from llm_judge import judge_naturalness
from metrics import save_result, get_summary, init_db
import time

app = FastAPI(title="RASTA Evaluation Service", version="1.0.0")

class EvalInput(BaseModel):
    original_text: str
    wav_bytes_b64: str
    rtf: float = 0.0
    oov_tokens: list[str] = []
    switch_count: int = 0
    source: str = "unknown"

class QuickEvalInput(BaseModel):
    original_text: str
    transcription: str
    rtf: float = 0.0
    oov_tokens: list[str] = []
    switch_count: int = 0
    source: str = "unknown"

@app.on_event("startup")
def startup():
    init_db()
    print("[eval-service] Database initialised.")

@app.get("/health")
def health():
    return {"status": "ok", "service": "eval-service"}

@app.post("/evaluate/quick")
def evaluate_quick(input: QuickEvalInput):
    """
    Evaluate using pre-computed transcription (no audio needed).
    Faster for batch evaluation.
    """
    cer = compute_cer(input.original_text, input.transcription)
    llm_scores = judge_naturalness(
        input.original_text,
        input.transcription,
        input.oov_tokens
    )

    result = {
        "original_text": input.original_text,
        "transcription": input.transcription,
        "cer": cer,
        "rtf": input.rtf,
        "oov_count": len(input.oov_tokens),
        "switch_count": input.switch_count,
        "fidelity": llm_scores.get("fidelity"),
        "naturalness": llm_scores.get("naturalness"),
        "intelligibility": llm_scores.get("intelligibility"),
        "llm_skipped": llm_scores.get("skipped", True),
        "source": input.source
    }

    save_result(result)
    return result

@app.get("/results/summary")
def results_summary():
    return get_summary()

@app.get("/results/dashboard")
def dashboard():
    summary = get_summary()
    html = f"""
    <html>
    <head>
        <title>RASTA Evaluation Dashboard</title>
        <style>
            body {{ font-family: Arial; padding: 20px; background: #f5f5f5; }}
            h1 {{ color: #333; }}
            .metric {{ background: white; padding: 15px; margin: 10px;
                      border-radius: 8px; display: inline-block; min-width: 150px;
                      box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .metric h3 {{ margin: 0; color: #666; font-size: 12px; }}
            .metric p {{ margin: 5px 0 0; font-size: 24px; font-weight: bold; color: #333; }}
        </style>
    </head>
    <body>
        <h1>RASTA Evaluation Dashboard</h1>
        <div class="metric"><h3>Total Evaluations</h3>
            <p>{summary.get('total_evaluations', 0)}</p></div>
        <div class="metric"><h3>Avg CER</h3>
            <p>{summary.get('avg_cer', 'N/A')}</p></div>
        <div class="metric"><h3>Avg RTF</h3>
            <p>{summary.get('avg_rtf', 'N/A')}</p></div>
        <div class="metric"><h3>Avg Fidelity</h3>
            <p>{summary.get('avg_fidelity', 'N/A')}</p></div>
        <div class="metric"><h3>Avg Naturalness</h3>
            <p>{summary.get('avg_naturalness', 'N/A')}</p></div>
        <div class="metric"><h3>Avg Intelligibility</h3>
            <p>{summary.get('avg_intelligibility', 'N/A')}</p></div>
    </body>
    </html>
    """
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)