"""
LoRA Adapter placeholder for prosodic continuity at language-switch boundaries.
Full adapter training runs in training/adapter_training.ipynb on Colab.
This module loads adapter weights if available, otherwise runs base model.
"""
import os
from pathlib import Path

ADAPTER_PATH = Path("models/tts_adapter/adapter_weights.pt")

def adapter_available() -> bool:
    return ADAPTER_PATH.exists()

def load_adapter(model):
    """
    Load LoRA adapter weights onto the base VITS model.
    Called at startup if adapter weights exist.
    """
    if not adapter_available():
        print("[adapter] No adapter weights found. Running base model.")
        return model

    try:
        import torch
        weights = torch.load(str(ADAPTER_PATH), map_location="cpu")
        model.load_state_dict(weights, strict=False)
        print(f"[adapter] Adapter weights loaded from {ADAPTER_PATH}")
    except Exception as e:
        print(f"[adapter] Failed to load adapter: {e}. Running base model.")

    return model

def get_language_switch_positions(tagged_tokens: list[dict]) -> list[int]:
    """
    Identify positions where language switches occur in tagged token sequence.
    Used for F0 discontinuity evaluation.
    """
    switch_positions = []
    for i in range(1, len(tagged_tokens)):
        prev_tag = tagged_tokens[i-1].get("tag", "TE")
        curr_tag = tagged_tokens[i].get("tag", "TE")
        if prev_tag != curr_tag:
            switch_positions.append(i)
    return switch_positions