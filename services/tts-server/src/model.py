import torch
import numpy as np
import io
import time
import re
from transformers import VitsModel, AutoTokenizer

MODEL_NAME = "facebook/mms-tts-tel"
_model = None
_tokenizer = None

def load_model():
    global _model, _tokenizer
    if _model is None:
        print(f"[model] Loading {MODEL_NAME}...")
        start = time.time()
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = VitsModel.from_pretrained(MODEL_NAME)
        _model.eval()
        elapsed = round(time.time() - start, 2)
        print(f"[model] Model loaded in {elapsed}s")
        # Run warmup to catch any issues early
        _warmup()
    return _model, _tokenizer

def _warmup():
    """Run a warmup inference to confirm model works."""
    try:
        test_text = "నమస్కారం"
        inputs = _tokenizer(test_text, return_tensors="pt")
        print(f"[model] Warmup input_ids shape: {inputs['input_ids'].shape}")
        print(f"[model] Warmup input_ids: {inputs['input_ids']}")
        with torch.no_grad():
            output = _model(**inputs).waveform
        print(f"[model] Warmup successful. Output shape: {output.shape}")
    except Exception as e:
        print(f"[model] Warmup failed: {e}")

def clean_text(text: str) -> str:
    """
    Clean and validate text before synthesis.
    Removes characters that cause tokenizer issues.
    """
    # Remove null bytes and control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove characters outside Telugu + basic Latin + punctuation
    # Keep: Telugu (0C00-0C7F), ASCII printable, common punctuation
    cleaned = []
    for char in text:
        cp = ord(char)
        if (0x0C00 <= cp <= 0x0C7F or  # Telugu
            0x0020 <= cp <= 0x007E or  # ASCII printable
            cp in (0x200C, 0x200D)):    # Zero-width joiners (needed for Telugu)
            cleaned.append(char)
    result = ''.join(cleaned).strip()
    return result if result else "నమస్కారం"

def validate_inputs(inputs) -> bool:
    """Check that tokenizer produced valid non-empty inputs."""
    if inputs['input_ids'].shape[1] == 0:
        return False
    if inputs['input_ids'].shape[1] > 512:
        return False
    return True

def synthesize(text: str) -> tuple[bytes, float, int]:
    """
    Synthesize text to WAV audio bytes.
    Returns (wav_bytes, real_time_factor, sample_rate).
    """
    model, tokenizer = load_model()

    # Clean text
    cleaned = clean_text(text)
    print(f"[model] Synthesizing: '{cleaned[:80]}'")

    start_time = time.time()

    inputs = tokenizer(cleaned, return_tensors="pt")
    print(f"[model] Token count: {inputs['input_ids'].shape[1]}")

    if not validate_inputs(inputs):
        raise ValueError(f"Invalid tokenizer output for text: '{cleaned[:50]}'")

    with torch.no_grad():
        output = model(**inputs).waveform

    waveform = output.squeeze().cpu().numpy()
    sample_rate = model.config.sampling_rate

    audio_duration = len(waveform) / sample_rate
    synthesis_time = time.time() - start_time
    rtf = round(synthesis_time / audio_duration, 4) if audio_duration > 0 else 0.0

    print(f"[model] RTF: {rtf} | Duration: {round(audio_duration, 2)}s | Synthesis: {round(synthesis_time, 2)}s")

    wav_bytes = numpy_to_wav(waveform, sample_rate)
    return wav_bytes, rtf, sample_rate

def numpy_to_wav(waveform: np.ndarray, sample_rate: int) -> bytes:
    """Convert numpy waveform to WAV bytes."""
    import soundfile as sf
    buffer = io.BytesIO()
    if len(waveform) == 0:
        raise ValueError("Empty waveform generated")
    # Normalize
    max_val = np.abs(waveform).max()
    if max_val > 0:
        waveform = waveform / max_val * 0.95
    sf.write(buffer, waveform, sample_rate, format='WAV', subtype='PCM_16')
    buffer.seek(0)
    return buffer.read()