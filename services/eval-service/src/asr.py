from faster_whisper import WhisperModel
import numpy as np
import io
import soundfile as sf

_whisper_model = None

def load_whisper():
    global _whisper_model
    if _whisper_model is None:
        print("[asr] Loading faster-whisper small model...")
        _whisper_model = WhisperModel("small", device="cpu", compute_type="int8")
        print("[asr] faster-whisper loaded.")
    return _whisper_model

def wav_bytes_to_numpy(wav_bytes: bytes) -> tuple[np.ndarray, int]:
    buffer = io.BytesIO(wav_bytes)
    audio, sr = sf.read(buffer)
    if audio.dtype != np.float32:
        audio = audio.astype(np.float32)
    return audio, sr

def transcribe(wav_bytes: bytes) -> dict:
    model = load_whisper()
    try:
        audio, sr = wav_bytes_to_numpy(wav_bytes)
        tmp_path = "/tmp/rasta_eval.wav"
        sf.write(tmp_path, audio, sr)
        segments, info = model.transcribe(
            tmp_path,
            language="te",
            beam_size=5
        )
        transcription = " ".join(s.text for s in segments).strip()
        return {
            "transcription": transcription,
            "language": info.language,
            "success": True
        }
    except Exception as e:
        print(f"[asr] Transcription error: {e}")
        return {"transcription": "", "language": "te", "success": False, "error": str(e)}

def compute_cer(reference: str, hypothesis: str) -> float:
    if not reference:
        return 1.0
    ref_chars = list(reference.replace(" ", ""))
    hyp_chars = list(hypothesis.replace(" ", ""))
    if len(ref_chars) == 0:
        return 0.0 if len(hyp_chars) == 0 else 1.0
    d = [[0] * (len(hyp_chars) + 1) for _ in range(len(ref_chars) + 1)]
    for i in range(len(ref_chars) + 1):
        d[i][0] = i
    for j in range(len(hyp_chars) + 1):
        d[0][j] = j
    for i in range(1, len(ref_chars) + 1):
        for j in range(1, len(hyp_chars) + 1):
            if ref_chars[i-1] == hyp_chars[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                d[i][j] = 1 + min(d[i-1][j], d[i][j-1], d[i-1][j-1])
    return round(d[len(ref_chars)][len(hyp_chars)] / len(ref_chars), 4)