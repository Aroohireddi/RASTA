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

Evaluated on 30 Telugu-English code-mixed sentences across 10 domains.

| Metric | Value |
|--------|-------|
| Total sentences | 30 |
| Average RTF (CPU) | 0.3243 |
| Min RTF | 0.2660 |
| Max RTF | 0.4006 |
| Real-time capable | ✅ YES |
| Avg CER (monolingual Telugu) | 0.0451 |
| Avg CER (code-mixed with OOV) | 0.3315 |
| Avg CER (all sentences) | 0.2838 |

### Key Finding
Monolingual Telugu sentences achieve CER of **0.045** (near-perfect).
Code-mixed sentences with OOV tokens achieve CER of **0.331** — a 7x increase —
directly motivating the RAG-based pronunciation disambiguation store.

### Domain Breakdown

| Domain | CER | RTF | n |
|--------|-----|-----|---|
| Space | 0.0809 | 0.3219 | 2 |
| Law | 0.1732 | 0.3052 | 2 |
| Health | 0.0758 | 0.3389 | 1 |
| Finance | 0.2206 | 0.3066 | 3 |
| Sports | 0.2053 | 0.3201 | 2 |
| Agriculture | 0.2198 | 0.3196 | 2 |
| Education | 0.2449 | 0.3167 | 2 |
| Politics | 0.2867 | 0.3484 | 4 |
| Infrastructure | 0.3712 | 0.3214 | 4 |
| Technology | 0.4744 | 0.3223 | 5 |

Technology domain shows highest CER (0.47) due to dense English OOV tokens
(AI, software, platform names) — the primary target of the RAG disambiguation store.

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