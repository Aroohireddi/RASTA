import json
import sqlite3
import time
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/eval_results/results.db")

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            original_text TEXT,
            transcription TEXT,
            cer REAL,
            rtf REAL,
            fidelity INTEGER,
            naturalness INTEGER,
            intelligibility INTEGER,
            oov_count INTEGER,
            switch_count INTEGER,
            llm_skipped INTEGER,
            source TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_result(result: dict):
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        INSERT INTO evaluations
        (timestamp, original_text, transcription, cer, rtf,
         fidelity, naturalness, intelligibility, oov_count,
         switch_count, llm_skipped, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        result.get("original_text", ""),
        result.get("transcription", ""),
        result.get("cer", 0.0),
        result.get("rtf", 0.0),
        result.get("fidelity"),
        result.get("naturalness"),
        result.get("intelligibility"),
        result.get("oov_count", 0),
        result.get("switch_count", 0),
        int(result.get("llm_skipped", True)),
        result.get("source", "unknown")
    ))
    conn.commit()
    conn.close()

def get_summary() -> dict:
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.execute("""
        SELECT
            COUNT(*) as total,
            AVG(cer) as avg_cer,
            AVG(rtf) as avg_rtf,
            AVG(fidelity) as avg_fidelity,
            AVG(naturalness) as avg_naturalness,
            AVG(intelligibility) as avg_intelligibility,
            MIN(rtf) as min_rtf,
            MAX(rtf) as max_rtf
        FROM evaluations
    """)
    row = cursor.fetchone()
    conn.close()
    if not row or row[0] == 0:
        return {"total_evaluations": 0}
    return {
        "total_evaluations": row[0],
        "avg_cer": round(row[1] or 0, 4),
        "avg_rtf": round(row[2] or 0, 4),
        "avg_fidelity": round(row[3] or 0, 2),
        "avg_naturalness": round(row[4] or 0, 2),
        "avg_intelligibility": round(row[5] or 0, 2),
        "min_rtf": round(row[6] or 0, 4),
        "max_rtf": round(row[7] or 0, 4)
    }