# RASTA Architecture

## Pipeline Flow
```
Live RSS Feeds (Eenadu, Sakshi, TV9, NTV, 10TV)
         ↓
   Ingestor :8001  (dedup, archive, queue)
         ↓
   NLP Pipeline :8002  (segment, summarise, code-mix, transliterate)
         ↓              ↓
RAG Store :8003  →  TTS Server :8004  (MMS-VITS + LoRA adapter)
                        ↓
               API Gateway :8000  (route, stream, WebSocket)
               ↓               ↓
        Eval Service :8005    End User (audio)
               ↓
          Dashboard :3000
```

## Service Summary

| Service | Port | Role |
|---------|------|------|
| Ingestor | 8001 | Live RSS polling, deduplication, storage |
| NLP Pipeline | 8002 | Segmentation, code-mixing, transliteration |
| RAG Store | 8003 | ChromaDB pronunciation disambiguation |
| TTS Server | 8004 | MMS-VITS synthesis + LoRA adapter |
| API Gateway | 8000 | Request routing, audio streaming |
| Eval Service | 8005 | CER, LLM judge, SQLite results |
| Dashboard | 3000 | Nginx static evaluation UI |