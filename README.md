# RASTA 🎙️
### Real-Time Retrieval-Augmented Speech Accessibility System for Telugu-English Code-Mixed Content

[![CI](https://github.com/YOUR_USERNAME/RASTA/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/RASTA/actions)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Docker](https://img.shields.io/badge/docker-compose-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Overview

RASTA is the first real-time end-to-end speech accessibility pipeline for
visually impaired and low-literacy Telugu-English bilingual users. It
continuously ingests live Telugu news content, processes it through a
code-mixed NLP pipeline, and delivers natural sentence-level audio output
as content is published.

---

## Architecture

![Architecture](docs/architecture.png)

---

## Novel Contributions

1. **RAG-based Pronunciation Disambiguation** — Retrieval-augmented OOV
   handling using a 500-entry manually verified Telugu-English lexicon
2. **LoRA Adapter for Prosodic Continuity** — Parameter-efficient adapter
   trained on synthetic code-mixed data to smooth language-switch boundaries
3. **Three-Layer Evaluation Harness** — CER via Whisper + LLM-as-judge +
   pre-registered human MOS study (n=20)

---

## Quickstart
```bash
git clone https://github.com/YOUR_USERNAME/RASTA.git
cd RASTA
docker-compose up --build
```

---

## Pipeline

1. **Ingestor** — Live RSS ingestion from Eenadu, Sakshi, ABN Andhra Jyothi
2. **NLP Pipeline** — Segmentation, summarisation, code-mixing, transliteration
3. **RAG Store** — OOV pronunciation disambiguation
4. **TTS Server** — MMS-VITS with LoRA adapter
5. **Eval Service** — Automated evaluation harness
6. **API Gateway** — WebSocket and HTTP delivery

---

## Evaluation Results

*Results will be populated after system evaluation.*

| Metric | Baseline | RASTA |
|--------|----------|-------|
| OOV Pronunciation Accuracy | - | - |
| F0 Discontinuity at Switch | - | - |
| CER (Whisper) | - | - |
| MOS (n=20) | - | - |
| RTF (CPU) | - | - |

---

## Dataset Release

- 500-entry Telugu-English pronunciation lexicon
- 30-day live-ingested evaluation snapshot
- Code-mixing annotations
- Human MOS ratings

---

## Training the Adapter

See [training/README.md](training/README.md) for the Colab notebook link.

---

## Known Limitations

- CPU inference RTF ~0.76 (no GPU support in current release)
- RSS poll interval 60s (not true streaming)
- LoRA adapter trained on synthetic data

---

## Citation
```bibtex
@misc{rasta2025,
  title={RASTA: A Real-Time Retrieval-Augmented Speech Accessibility
         System for Telugu-English Code-Mixed Content Delivery},
  author={},
  year={2025}
}
```

---

## License

MIT